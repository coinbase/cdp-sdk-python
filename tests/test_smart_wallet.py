from unittest.mock import Mock, patch

import pytest
from eth_account import Account

from cdp.client.models.call import Call
from cdp.client.models.create_smart_wallet_request import CreateSmartWalletRequest
from cdp.evm_call_types import EVMAbiCallDict, EVMCallDict
from cdp.smart_wallet import SmartWallet, to_smart_wallet
from cdp.user_operation import UserOperation


def test_smart_wallet_initialization(smart_wallet_factory, account_factory):
    """Test SmartWallet initialization."""
    account = account_factory()
    smart_wallet_address = "0x1234567890123456789012345678901234567890"
    smart_wallet = smart_wallet_factory(smart_wallet_address, account)
    assert smart_wallet.address == smart_wallet_address
    assert smart_wallet.owners == [account]


@patch("cdp.Cdp.api_clients")
def test_smart_wallet_create(
    mock_api_clients,
    smart_wallet_model_factory,
):
    """Test SmartWallet create method."""
    account = Account.create()
    smart_wallet_address = "0x1234567890123456789012345678901234567890"
    mock_create_smart_wallet = Mock(
        return_value=smart_wallet_model_factory(address=smart_wallet_address, owner=account.address)
    )
    mock_api_clients.smart_wallets.create_smart_wallet = mock_create_smart_wallet

    smart_wallet = SmartWallet.create(account)
    mock_create_smart_wallet.assert_called_once_with(
        CreateSmartWalletRequest(owner=account.address)
    )

    assert smart_wallet.address == smart_wallet_address
    assert smart_wallet.owners == [account]


def test_smart_wallet_use_network(smart_wallet_factory):
    """Test SmartWallet use_network method."""
    account = Account.create()
    smart_wallet_address = "0x1234567890123456789012345678901234567890"
    smart_wallet = smart_wallet_factory(smart_wallet_address, account)
    network_scoped_wallet = smart_wallet.use_network(84532, "https://paymaster.com")
    assert network_scoped_wallet.chain_id == 84532
    assert network_scoped_wallet.paymaster_url == "https://paymaster.com"


@patch("cdp.Cdp.api_clients")
def test_smart_wallet_send_user_operation_with_encoded_call(
    mock_api_clients, smart_wallet_factory, user_operation_model_factory, account_factory
):
    """Test SmartWallet send_user_operation method."""
    account = account_factory()
    smart_wallet_address = "0x1234567890123456789012345678901234567890"
    smart_wallet = smart_wallet_factory(smart_wallet_address, account)

    mock_user_operation = user_operation_model_factory(
        id="test-user-operation-id",
        network_id="base-sepolia",
        calls=[Call(to=account.address, value="1000000000000000000", data="0x")],
        user_op_hash="0x" + "0" * 64,  # 32 bytes in hex
        signature="0xe0a180fdd0fe38037cc878c03832861b40a29d32bd7b40b10c9e1efc8c1468a05ae06d1624896d0d29f4b31e32772ea3cb1b4d7ed4e077e5da28dcc33c0e78121c",
        transaction_hash="0x4567890123456789012345678901234567890123",
        status="pending",
    )

    mock_create_user_operation = Mock(return_value=mock_user_operation)
    mock_api_clients.smart_wallets.create_user_operation = mock_create_user_operation

    calls = [EVMCallDict(to=account.address, value=1000000000000000000, data="0x")]

    user_operation = smart_wallet.send_user_operation(
        calls=calls, chain_id=84532, paymaster_url="https://paymaster.com"
    )

    mock_create_user_operation.assert_called_once()

    assert user_operation.smart_wallet_address == smart_wallet_address
    assert user_operation.user_op_hash == mock_user_operation.user_op_hash
    assert user_operation.signature == mock_user_operation.signature
    assert user_operation.transaction_hash == mock_user_operation.transaction_hash
    assert user_operation.status == UserOperation.Status(mock_user_operation.status)
    assert not user_operation.terminal_state


@patch("cdp.Cdp.api_clients")
def test_send_user_operation_with_abi_call(
    mock_api_clients, smart_wallet_factory, user_operation_model_factory, account_factory
):
    """Test sending user operation with EVMAbiCallDict."""
    account = account_factory()
    smart_wallet_address = "0x1234567890123456789012345678901234567890"
    smart_wallet = smart_wallet_factory(smart_wallet_address, account)

    mock_user_operation = user_operation_model_factory(
        id="test-op-id",
        network_id="base-sepolia",
        calls=[Call(to=account.address, data="0x123", value="0")],
        user_op_hash="0x" + "0" * 64,
        signature="0xe0a180fdd0fe38037cc878c03832861b40a29d32bd7b40b10c9e1efc8c1468a05ae06d1624896d0d29f4b31e32772ea3cb1b4d7ed4e077e5da28dcc33c0e78121c",
        transaction_hash="0x4567890123456789012345678901234567890123",
        status="pending",
    )

    mock_create_user_operation = Mock(return_value=mock_user_operation)
    mock_api_clients.smart_wallets.create_user_operation = mock_create_user_operation

    abi_call = EVMAbiCallDict(
        to=account.address,
        abi=[{"inputs": [], "name": "transfer", "type": "function"}],
        function_name="transfer",
        args=[],
        value=None,
    )

    user_operation = smart_wallet.send_user_operation(calls=[abi_call], chain_id=84532)

    assert user_operation.smart_wallet_address == smart_wallet_address
    assert user_operation.user_op_hash == mock_user_operation.user_op_hash
    assert user_operation.signature == mock_user_operation.signature
    assert user_operation.transaction_hash == mock_user_operation.transaction_hash
    assert user_operation.status == UserOperation.Status(mock_user_operation.status)
    assert not user_operation.terminal_state
    mock_create_user_operation.assert_called_once()


@patch("cdp.Cdp.api_clients")
def test_smart_wallet_multiple_calls(
    mock_api_clients, smart_wallet_factory, account_factory, user_operation_model_factory
):
    """Test sending multiple calls in one operation."""
    account = account_factory()
    smart_wallet_address = "0x1234567890123456789012345678901234567890"
    smart_wallet = smart_wallet_factory(smart_wallet_address, account)

    calls = [
        EVMCallDict(to=account.address, value=1000000000000000000, data="0x"),
        EVMCallDict(to=account.address, value=0, data="0x123"),
        EVMCallDict(to=account.address, value=None, data=None),
    ]

    model_calls = [Call(to=c.to, value=str(c.value or 0), data=c.data or "0x") for c in calls]

    mock_user_operation = user_operation_model_factory(
        id="test-op-id",
        network_id="base-sepolia",
        calls=model_calls,
        user_op_hash="0x" + "0" * 64,
        signature="0x" + "0" * 130,
        transaction_hash="0x" + "0" * 64,
        status="pending",
    )

    mock_api_clients.smart_wallets.create_user_operation.return_value = mock_user_operation

    user_operation = smart_wallet.send_user_operation(calls=calls, chain_id=84532)

    assert user_operation.user_op_hash == mock_user_operation.user_op_hash
    assert user_operation.transaction_hash == mock_user_operation.transaction_hash
    assert user_operation.status == UserOperation.Status(mock_user_operation.status)
    assert not user_operation.terminal_state

    mock_api_clients.smart_wallets.create_user_operation.assert_called_once()


def test_network_scoped_wallet_initialization(smart_wallet_factory, account_factory):
    """Test NetworkScopedSmartWallet initialization."""
    account = account_factory()
    smart_wallet_address = "0x1234567890123456789012345678901234567890"

    network_wallet = smart_wallet_factory(smart_wallet_address, account).use_network(
        84532, "https://paymaster.com"
    )
    assert network_wallet.chain_id == 84532
    assert network_wallet.paymaster_url == "https://paymaster.com"

    network_wallet = smart_wallet_factory(smart_wallet_address, account).use_network(84532)
    assert network_wallet.chain_id == 84532
    assert network_wallet.paymaster_url is None


@patch("cdp.Cdp.api_clients")
def test_network_scoped_wallet_send_operation(
    mock_api_clients, smart_wallet_factory, user_operation_model_factory, account_factory
):
    """Test NetworkScopedSmartWallet send_user_operation method."""
    account = account_factory()
    smart_wallet_address = "0x1234567890123456789012345678901234567890"
    network_wallet = smart_wallet_factory(smart_wallet_address, account).use_network(84532)

    mock_user_operation = user_operation_model_factory(
        id="test-op-id",
        network_id="base-sepolia",
        calls=[Call(to=account.address, value="1000000000000000000", data="0x")],
        user_op_hash="0x" + "0" * 64,
        signature="0xe0a180fdd0fe38037cc878c03832861b40a29d32bd7b40b10c9e1efc8c1468a05ae06d1624896d0d29f4b31e32772ea3cb1b4d7ed4e077e5da28dcc33c0e78121c",
        transaction_hash="0x4567890123456789012345678901234567890123",
        status="pending",
    )

    mock_create_user_operation = Mock(return_value=mock_user_operation)
    mock_api_clients.smart_wallets.create_user_operation = mock_create_user_operation

    calls = [EVMCallDict(to=account.address, value=1000000000000000000, data="0x")]
    user_operation = network_wallet.send_user_operation(calls=calls)

    assert user_operation.smart_wallet_address == smart_wallet_address
    assert user_operation.user_op_hash == mock_user_operation.user_op_hash
    assert user_operation.signature == mock_user_operation.signature
    assert user_operation.transaction_hash == mock_user_operation.transaction_hash
    assert user_operation.status == UserOperation.Status(mock_user_operation.status)
    assert not user_operation.terminal_state


def test_network_scoped_wallet_string_representations(smart_wallet_factory, account_factory):
    """Test NetworkScopedSmartWallet string representations."""
    account = account_factory()
    address = "0x1234567890123456789012345678901234567890"
    network_wallet = smart_wallet_factory(address, account).use_network(84532)

    assert str(network_wallet) == f"Network Scoped Smart Wallet: {address} (Chain ID: 84532)"
    assert (
        repr(network_wallet)
        == f"Network Scoped Smart Wallet: (model=SmartWalletModel(address='{address}'), network=Network(chain_id=84532, paymaster_url=None))"
    )


def test_to_smart_wallet_creation(account_factory):
    """Test to_smart_wallet function."""
    signer = account_factory()
    address = "0x1234567890123456789012345678901234567890"

    wallet = to_smart_wallet(address, signer)
    assert wallet.address == address
    assert wallet.owners == [signer]


@patch("cdp.Cdp.api_clients")
def test_send_user_operation_with_empty_calls(
    mock_api_clients, smart_wallet_factory, account_factory
):
    """Test that sending empty calls list raises ValueError."""
    account = account_factory()
    smart_wallet_address = "0x1234567890123456789012345678901234567890"
    smart_wallet = smart_wallet_factory(smart_wallet_address, account)

    with pytest.raises(ValueError, match="Calls list cannot be empty"):
        smart_wallet.send_user_operation(calls=[], chain_id=84532)

    mock_api_clients.smart_wallets.create_user_operation.assert_not_called()
