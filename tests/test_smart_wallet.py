from unittest.mock import Mock, patch

from eth_account import Account

from cdp.client.models.call import Call
from cdp.client.models.create_smart_wallet_request import CreateSmartWalletRequest
from cdp.evm_call_types import EVMCallDict
from cdp.smart_wallet import SmartWallet
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
def test_smart_wallet_send_user_operation(
    mock_api_clients, smart_wallet_factory, user_operation_model_factory, account_factory
):
    """Test SmartWallet send_user_operation method."""
    account = account_factory()
    smart_wallet_address = "0x1234567890123456789012345678901234567890"
    smart_wallet = smart_wallet_factory(smart_wallet_address, account)

    # Create a mock user operation using UserOperationModel
    mock_user_operation = user_operation_model_factory(
        id="test-user-operation-id",
        network_id="base-sepolia",
        calls=[Call(to=account.address, value="1000000000000000000", data="0x")],
        unsigned_payload="0x" + "0" * 64,  # 32 bytes in hex
        signature="0xe0a180fdd0fe38037cc878c03832861b40a29d32bd7b40b10c9e1efc8c1468a05ae06d1624896d0d29f4b31e32772ea3cb1b4d7ed4e077e5da28dcc33c0e78121c",
        transaction_hash="0x4567890123456789012345678901234567890123",
        status="pending",
    )

    # Setup the mock chain
    mock_create_user_operation = Mock(return_value=mock_user_operation)
    mock_api_clients.smart_wallets.create_user_operation = mock_create_user_operation

    calls = [EVMCallDict(to=account.address, value=1000000000000000000, data="0x")]

    user_operation = smart_wallet.send_user_operation(
        calls=calls, chain_id=84532, paymaster_url="https://paymaster.com"
    )

    # Verify the mock was called with correct arguments
    mock_create_user_operation.assert_called_once()

    # Verify the user operation properties match expected values
    assert user_operation.user_operation_id == mock_user_operation.id
    assert user_operation.smart_wallet_address == smart_wallet_address
    assert user_operation.unsigned_payload == mock_user_operation.unsigned_payload
    assert user_operation.signature == mock_user_operation.signature
    assert user_operation.transaction_hash == mock_user_operation.transaction_hash
    assert user_operation.status == UserOperation.Status(mock_user_operation.status)
    assert not user_operation.terminal_state
