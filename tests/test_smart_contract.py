from unittest.mock import ANY, Mock, call, patch

import pytest

from cdp.client.models.solidity_value import SolidityValue
from cdp.smart_contract import SmartContract


def test_smart_contract_initialization(smart_contract_factory):
    """Test the initialization of a SmartContract object."""
    smart_contract = smart_contract_factory()
    assert isinstance(smart_contract, SmartContract)


def test_smart_contract_properties(smart_contract_factory):
    """Test the properties of a SmartContract object."""
    smart_contract = smart_contract_factory()
    assert smart_contract.smart_contract_id == "test-contract-id"
    assert smart_contract.wallet_id == "test-wallet-id"
    assert smart_contract.network_id == "base-sepolia"
    assert smart_contract.contract_address == "0xcontractaddress"
    assert smart_contract.deployer_address == "0xdeployeraddress"
    assert smart_contract.type.value == SmartContract.Type.ERC20.value
    assert smart_contract.options == {
        "name": "TestToken",
        "symbol": "TT",
        "total_supply": "1000000",
    }
    assert smart_contract.abi == {"abi": "data"}
    assert smart_contract.transaction.status.value == "complete"
    assert (
        smart_contract.transaction.transaction_link
        == "https://sepolia.basescan.org/tx/0xtransactionlink"
    )
    assert smart_contract.transaction.transaction_hash == "0xtransactionhash"


@patch("cdp.Cdp.api_clients")
def test_create_smart_contract(mock_api_clients, smart_contract_factory):
    """Test the creation of a SmartContract object."""
    mock_create_contract = Mock()
    mock_create_contract.return_value = smart_contract_factory()._model
    mock_api_clients.smart_contracts.create_smart_contract = mock_create_contract

    smart_contract = SmartContract.create(
        wallet_id="test-wallet-id",
        address_id="0xaddressid",
        type=SmartContract.Type.ERC20,
        options=SmartContract.TokenContractOptions(
            name="TestToken", symbol="TT", total_supply="1000000"
        ),
    )

    assert isinstance(smart_contract, SmartContract)
    mock_create_contract.assert_called_once_with(
        wallet_id="test-wallet-id",
        address_id="0xaddressid",
        create_smart_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_broadcast_smart_contract(mock_api_clients, smart_contract_factory):
    """Test the broadcasting of a SmartContract object."""
    smart_contract = smart_contract_factory(status="signed")
    mock_broadcast = Mock(return_value=smart_contract_factory(status="broadcast")._model)
    mock_api_clients.smart_contracts.deploy_smart_contract = mock_broadcast

    response = smart_contract.broadcast()

    assert isinstance(response, SmartContract)
    mock_broadcast.assert_called_once_with(
        wallet_id=smart_contract.wallet_id,
        address_id=smart_contract.deployer_address,
        smart_contract_id=smart_contract.smart_contract_id,
        deploy_smart_contract_request=ANY,
    )


def test_broadcast_unsigned_smart_contract(smart_contract_factory):
    """Test the broadcasting of an unsigned SmartContract object."""
    smart_contract = smart_contract_factory(status="pending")
    with pytest.raises(ValueError, match="Cannot broadcast unsigned SmartContract deployment"):
        smart_contract.broadcast()


@patch("cdp.Cdp.api_clients")
def test_reload_smart_contract(mock_api_clients, smart_contract_factory):
    """Test the reloading of a SmartContract object."""
    smart_contract = smart_contract_factory(status="pending")
    complete_contract = smart_contract_factory(status="complete")
    mock_get_contract = Mock()
    mock_api_clients.smart_contracts.get_smart_contract = mock_get_contract
    mock_get_contract.return_value = complete_contract._model

    smart_contract.reload()

    mock_get_contract.assert_called_once_with(
        wallet_id=smart_contract.wallet_id,
        address_id=smart_contract.deployer_address,
        smart_contract_id=smart_contract.smart_contract_id,
    )
    assert smart_contract.transaction.status.value == "complete"


@patch("cdp.Cdp.api_clients")
@patch("cdp.smart_contract.time.sleep")
@patch("cdp.smart_contract.time.time")
def test_wait_for_smart_contract(mock_time, mock_sleep, mock_api_clients, smart_contract_factory):
    """Test the waiting for a SmartContract object to complete."""
    pending_contract = smart_contract_factory(status="pending")
    complete_contract = smart_contract_factory(status="complete")
    mock_get_contract = Mock()
    mock_api_clients.smart_contracts.get_smart_contract = mock_get_contract
    mock_get_contract.side_effect = [pending_contract._model, complete_contract._model]

    mock_time.side_effect = [0, 0.2, 0.4]

    result = pending_contract.wait(interval_seconds=0.2, timeout_seconds=1)

    assert result.transaction.status.value == "complete"
    mock_get_contract.assert_called_with(
        wallet_id=pending_contract.wallet_id,
        address_id=pending_contract.deployer_address,
        smart_contract_id=pending_contract.smart_contract_id,
    )
    assert mock_get_contract.call_count == 2
    mock_sleep.assert_has_calls([call(0.2)] * 2)
    assert mock_time.call_count == 3


@patch("cdp.Cdp.api_clients")
@patch("cdp.smart_contract.time.sleep")
@patch("cdp.smart_contract.time.time")
def test_wait_for_smart_contract_timeout(
    mock_time, mock_sleep, mock_api_clients, smart_contract_factory
):
    """Test the waiting for a SmartContract object to complete with a timeout."""
    pending_contract = smart_contract_factory(status="pending")
    mock_get_contract = Mock(return_value=pending_contract._model)
    mock_api_clients.smart_contracts.get_smart_contract = mock_get_contract

    mock_time.side_effect = [0, 0.5, 1.0, 1.5, 2.0, 2.5]

    with pytest.raises(TimeoutError, match="SmartContract deployment timed out"):
        pending_contract.wait(interval_seconds=0.5, timeout_seconds=2)

    assert mock_get_contract.call_count == 5
    mock_sleep.assert_has_calls([call(0.5)] * 4)
    assert mock_time.call_count == 6


def test_sign_smart_contract_invalid_key(smart_contract_factory):
    """Test the signing of a SmartContract object with an invalid key."""
    smart_contract = smart_contract_factory()
    with pytest.raises(ValueError, match="key must be a LocalAccount"):
        smart_contract.sign("invalid_key")


def test_smart_contract_str_representation(smart_contract_factory):
    """Test the string representation of a SmartContract object."""
    smart_contract = smart_contract_factory()
    expected_str = (
        f"SmartContract: (smart_contract_id: {smart_contract.smart_contract_id}, "
        f"wallet_id: {smart_contract.wallet_id}, network_id: {smart_contract.network_id}, "
        f"contract_address: {smart_contract.contract_address}, type: {smart_contract.type}, "
        f"transaction_hash: {smart_contract.transaction.transaction_hash}, "
        f"transaction_link: {smart_contract.transaction.transaction_link}, "
        f"status: {smart_contract.transaction.status})"
    )
    assert str(smart_contract) == expected_str


def test_smart_contract_repr(smart_contract_factory):
    """Test the representation of a SmartContract object."""
    smart_contract = smart_contract_factory()
    assert repr(smart_contract) == str(smart_contract)


@patch("cdp.Cdp.api_clients")
def test_read_pure_string(mock_api_clients, all_read_types_abi):
    """Test reading a string value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="string", value="Hello, World!")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureString",
        abi=all_read_types_abi,
    )

    assert result == "Hello, World!"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes1(mock_api_clients, all_read_types_abi):
    """Test reading a bytes1 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="bytes1", value="0x01")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes1",
        abi=all_read_types_abi,
    )

    assert result == "0x01"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes2(mock_api_clients, all_read_types_abi):
    """Test reading a bytes2 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="bytes2", value="0x0102")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes2",
        abi=all_read_types_abi,
    )

    assert result == "0x0102"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes3(mock_api_clients, all_read_types_abi):
    """Test reading a bytes3 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="bytes3", value="0x010203")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes3",
        abi=all_read_types_abi,
    )

    assert result == "0x010203"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes4(mock_api_clients, all_read_types_abi):
    """Test reading a bytes4 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="bytes4", value="0x01020304")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes4",
        abi=all_read_types_abi,
    )

    assert result == "0x01020304"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes5(mock_api_clients, all_read_types_abi):
    """Test reading a bytes5 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="bytes5", value="0x0102030405")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes5",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes6(mock_api_clients, all_read_types_abi):
    """Test reading a bytes6 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="bytes6", value="0x010203040506")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes6",
        abi=all_read_types_abi,
    )

    assert result == "0x010203040506"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes7(mock_api_clients, all_read_types_abi):
    """Test reading a bytes7 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="bytes7", value="0x01020304050607")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes7",
        abi=all_read_types_abi,
    )

    assert result == "0x01020304050607"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes8(mock_api_clients, all_read_types_abi):
    """Test reading a bytes8 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="bytes8", value="0x0102030405060708")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes8",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes9(mock_api_clients, all_read_types_abi):
    """Test reading a bytes9 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="bytes9", value="0x010203040506070809")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes9",
        abi=all_read_types_abi,
    )

    assert result == "0x010203040506070809"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes10(mock_api_clients, all_read_types_abi):
    """Test reading a bytes10 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="bytes10", value="0x01020304050607080910")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes10",
        abi=all_read_types_abi,
    )

    assert result == "0x01020304050607080910"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes11(mock_api_clients, all_read_types_abi):
    """Test reading a bytes11 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes11", value="0x0102030405060708091011"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes11",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708091011"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes12(mock_api_clients, all_read_types_abi):
    """Test reading a bytes12 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes12", value="0x010203040506070809101112"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes12",
        abi=all_read_types_abi,
    )

    assert result == "0x010203040506070809101112"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes13(mock_api_clients, all_read_types_abi):
    """Test reading a bytes13 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes13", value="0x01020304050607080910111213"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes13",
        abi=all_read_types_abi,
    )

    assert result == "0x01020304050607080910111213"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes14(mock_api_clients, all_read_types_abi):
    """Test reading a bytes14 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes14", value="0x0102030405060708091011121314"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes14",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708091011121314"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes15(mock_api_clients, all_read_types_abi):
    """Test reading a bytes15 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes15", value="0x010203040506070809101112131415"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes15",
        abi=all_read_types_abi,
    )

    assert result == "0x010203040506070809101112131415"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes16(mock_api_clients, all_read_types_abi):
    """Test reading a bytes16 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes16", value="0x0102030405060708090a0b0c0d0e0f10"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes16",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708090a0b0c0d0e0f10"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes17(mock_api_clients, all_read_types_abi):
    """Test reading a bytes17 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes17", value="0x0102030405060708090a0b0c0d0e0f1011"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes17",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708090a0b0c0d0e0f1011"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes18(mock_api_clients, all_read_types_abi):
    """Test reading a bytes18 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes18", value="0x0102030405060708090a0b0c0d0e0f101112"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes18",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708090a0b0c0d0e0f101112"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes19(mock_api_clients, all_read_types_abi):
    """Test reading a bytes19 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes19", value="0x0102030405060708090a0b0c0d0e0f10111213"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes19",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708090a0b0c0d0e0f10111213"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes20(mock_api_clients, all_read_types_abi):
    """Test reading a bytes20 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes20", value="0x0102030405060708090a0b0c0d0e0f1011121314"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes20",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708090a0b0c0d0e0f1011121314"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes21(mock_api_clients, all_read_types_abi):
    """Test reading a bytes21 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes21", value="0x0102030405060708090a0b0c0d0e0f10111213141516"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes21",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708090a0b0c0d0e0f10111213141516"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes22(mock_api_clients, all_read_types_abi):
    """Test reading a bytes22 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes22", value="0x0102030405060708090a0b0c0d0e0f10111213141516171819"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes22",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708090a0b0c0d0e0f10111213141516171819"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes23(mock_api_clients, all_read_types_abi):
    """Test reading a bytes23 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes23", value="0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f2021"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes23",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f2021"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes24(mock_api_clients, all_read_types_abi):
    """Test reading a bytes24 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes24",
        value="0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122",
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes24",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes25(mock_api_clients, all_read_types_abi):
    """Test reading a bytes25 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes25",
        value="0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20212223",
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes25",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20212223"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes26(mock_api_clients, all_read_types_abi):
    """Test reading a bytes26 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes26",
        value="0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425",
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes26",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes27(mock_api_clients, all_read_types_abi):
    """Test reading a bytes27 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes27",
        value="0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f2021222324252627",
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes27",
        abi=all_read_types_abi,
    )

    assert (
        result == "0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f2021222324252627"
    )
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes28(mock_api_clients, all_read_types_abi):
    """Test reading a bytes28 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes28", value="0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes28",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes29(mock_api_clients, all_read_types_abi):
    """Test reading a bytes29 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes29", value="0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes29",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes30(mock_api_clients, all_read_types_abi):
    """Test reading a bytes30 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes30", value="0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes30",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes31(mock_api_clients, all_read_types_abi):
    """Test reading a bytes31 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes31", value="0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes31",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes32(mock_api_clients, all_read_types_abi):
    """Test reading a bytes32 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes32", value="0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes32",
        abi=all_read_types_abi,
    )

    assert result == "0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bytes(mock_api_clients, all_read_types_abi):
    """Test reading a bytes value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes",
        value="0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20212223242526272829",
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBytes",
        abi=all_read_types_abi,
    )

    assert (
        result
        == "0x0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20212223242526272829"
    )
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_uint8(mock_api_clients, all_read_types_abi):
    """Test reading a uint8 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="uint8", value="123")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureUint8",
        abi=all_read_types_abi,
    )

    assert result == 123
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_uint16(mock_api_clients, all_read_types_abi):
    """Test reading a uint16 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="uint16", value="12345")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureUint16",
        abi=all_read_types_abi,
    )

    assert result == 12345
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_uint32(mock_api_clients, all_read_types_abi):
    """Test reading a uint32 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="uint32", value="4294967295")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureUint32",
        abi=all_read_types_abi,
    )

    assert result == 4294967295
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_uint64(mock_api_clients, all_read_types_abi):
    """Test reading a uint64 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="uint64", value="18446744073709551615")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureUint64",
        abi=all_read_types_abi,
    )

    assert result == 18446744073709551615
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_uint128(mock_api_clients, all_read_types_abi):
    """Test reading a uint128 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="uint128", value="340282366920938463463374607431768211455"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureUint128",
        abi=all_read_types_abi,
    )

    assert result == 340282366920938463463374607431768211455
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_uint256(mock_api_clients, all_read_types_abi):
    """Test reading a uint256 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="uint256",
        value="115792089237316195423570985008687907853269984665640564039457584007913129639935",
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureUint256",
        abi=all_read_types_abi,
    )

    assert result == 115792089237316195423570985008687907853269984665640564039457584007913129639935
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_int8(mock_api_clients, all_read_types_abi):
    """Test reading an int8 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="int8", value="-128")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureInt8",
        abi=all_read_types_abi,
    )

    assert result == -128
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_int16(mock_api_clients, all_read_types_abi):
    """Test reading an int16 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="int16", value="-32768")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureInt16",
        abi=all_read_types_abi,
    )

    assert result == -32768
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_int32(mock_api_clients, all_read_types_abi):
    """Test reading an int32 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="int32", value="-2147483648")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureInt32",
        abi=all_read_types_abi,
    )

    assert result == -2147483648
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_int64(mock_api_clients, all_read_types_abi):
    """Test reading an int64 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="int64", value="-9223372036854775808")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureInt64",
        abi=all_read_types_abi,
    )

    assert result == -9223372036854775808
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_int128(mock_api_clients, all_read_types_abi):
    """Test reading an int128 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="int128", value="-170141183460469231731687303715884105728"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureInt128",
        abi=all_read_types_abi,
    )

    assert result == -170141183460469231731687303715884105728
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_int256(mock_api_clients, all_read_types_abi):
    """Test reading an int256 value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="int256",
        value="-57896044618658097711785492504343953926634992332820282019728792003956564819968",
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureInt256",
        abi=all_read_types_abi,
    )

    assert result == -57896044618658097711785492504343953926634992332820282019728792003956564819968
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_address(mock_api_clients, all_read_types_abi):
    """Test reading an address value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="address", value="0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureAddress",
        abi=all_read_types_abi,
    )

    assert result == "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bool(mock_api_clients, all_read_types_abi):
    """Test reading a boolean value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="bool", value="true")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBool",
        abi=all_read_types_abi,
    )

    assert result is True
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_array(mock_api_clients, all_read_types_abi):
    """Test reading an array value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="array",
        values=[
            SolidityValue(type="uint256", value="1"),
            SolidityValue(type="uint256", value="2"),
            SolidityValue(type="uint256", value="3"),
            SolidityValue(type="uint256", value="4"),
            SolidityValue(type="uint256", value="5"),
        ],
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureArray",
        abi=all_read_types_abi,
    )

    assert result == [1, 2, 3, 4, 5]  # Note: In Python, we use regular integers, not BigInt
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_return_function(mock_api_clients, all_read_types_abi):
    """Test reading a function type as bytes from a view function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes", value="0x12341234123412341234123400000000"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="returnFunction",
        abi=all_read_types_abi,
    )

    assert result == "0x12341234123412341234123400000000"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_tuple(mock_api_clients, all_read_types_abi):
    """Test reading a tuple value from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="tuple",
        values=[
            SolidityValue(type="uint256", value="1", name="a"),
            SolidityValue(type="uint256", value="2", name="b"),
        ],
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureTuple",
        abi=all_read_types_abi,
    )

    assert result == {"a": 1, "b": 2}  # In Python, we use regular integers, not BigInt
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_tuple_mixed_types(mock_api_clients, all_read_types_abi):
    """Test reading a tuple with mixed types from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="tuple",
        values=[
            SolidityValue(type="uint256", value="1", name="a"),
            SolidityValue(
                type="address", value="0x1234567890123456789012345678901234567890", name="b"
            ),
            SolidityValue(type="bool", value="true", name="c"),
        ],
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureTupleMixedTypes",
        abi=all_read_types_abi,
    )

    assert result == {"a": 1, "b": "0x1234567890123456789012345678901234567890", "c": True}
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_function_type_as_bytes(mock_api_clients, all_read_types_abi):
    """Test reading a function type as bytes."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="bytes", value="0x12341234123412341234123400000000"
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="returnFunction",
        abi=all_read_types_abi,
    )

    assert result == "0x12341234123412341234123400000000"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_nested_struct(mock_api_clients, all_read_types_abi):
    """Test reading a nested struct from a pure function."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(
        type="tuple",
        values=[
            SolidityValue(type="uint256", value="42", name="a"),
            SolidityValue(
                type="tuple",
                name="nestedFields",
                values=[
                    SolidityValue(
                        type="tuple",
                        name="nestedArray",
                        values=[
                            SolidityValue(
                                type="array",
                                name="a",
                                values=[
                                    SolidityValue(type="uint256", value="1"),
                                    SolidityValue(type="uint256", value="2"),
                                    SolidityValue(type="uint256", value="3"),
                                ],
                            ),
                        ],
                    ),
                    SolidityValue(type="uint256", value="123", name="a"),
                ],
            ),
        ],
    )
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureNestedStruct",
        abi=all_read_types_abi,
    )

    assert result == {
        "a": 42,
        "nestedFields": {
            "nestedArray": {
                "a": [1, 2, 3],
            },
            "a": 123,
        },
    }
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_string_without_abi(mock_api_clients):
    """Test reading a string value from a pure function without an ABI."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="string", value="Hello, World!")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureString",
    )

    assert result == "Hello, World!"
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_bool_without_abi(mock_api_clients):
    """Test reading a boolean value from a pure function without an ABI."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="bool", value="true")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureBool",
    )

    assert result is True
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_read_pure_int8_without_abi(mock_api_clients):
    """Test reading an int8 value from a pure function without an ABI."""
    mock_read_contract = Mock()
    mock_read_contract.return_value = SolidityValue(type="int8", value="42")
    mock_api_clients.smart_contracts.read_contract = mock_read_contract

    result = SmartContract.read(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        method="pureInt8",
    )

    assert result == 42
    mock_read_contract.assert_called_once_with(
        network_id="1",
        contract_address="0x1234567890123456789012345678901234567890",
        read_contract_request=ANY,
    )
