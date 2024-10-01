from unittest.mock import ANY, Mock, call, patch

import pytest

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
