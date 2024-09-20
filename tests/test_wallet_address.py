from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from eth_account.signers.local import LocalAccount

from cdp.client.models.address import Address as AddressModel
from cdp.client.models.asset import Asset as AssetModel
from cdp.client.models.balance import Balance as BalanceModel
from cdp.errors import InsufficientFundsError
from cdp.trade import Trade
from cdp.transfer import Transfer
from cdp.wallet_address import WalletAddress


@pytest.fixture
def address_model():
    """Fixture for an AddressModel."""
    return AddressModel(
        network_id="base-sepolia",
        address_id="0x1234567890123456789012345678901234567890",
        wallet_id="test-wallet-id-1",
        public_key="0x1234567890123456789012345678901234567890",
        index=0,
    )


@pytest.fixture
def wallet_address(address_model):
    """Fixture for a WalletAddress."""
    return WalletAddress(address_model)


@pytest.fixture
def wallet_address_with_key(address_model):
    """Fixture for a WalletAddress with a key."""
    key = Mock(spec=LocalAccount)
    return WalletAddress(address_model, key)


@pytest.fixture
def asset_model():
    """Fixture for an AssetModel."""
    return AssetModel(network_id="base-sepolia", asset_id="eth", decimals=18)


@pytest.fixture
def balance_model(asset_model):
    """Fixture for a BalanceModel."""
    return BalanceModel(amount="5000000000000000000", asset=asset_model)


def test_wallet_address_initialization(wallet_address):
    """Test the initialization of a WalletAddress."""
    assert wallet_address.network_id == "base-sepolia"
    assert wallet_address.address_id == "0x1234567890123456789012345678901234567890"
    assert wallet_address.wallet_id == "test-wallet-id-1"
    assert wallet_address.key is None
    assert not wallet_address.can_sign


def test_wallet_address_initialization_with_key(wallet_address_with_key):
    """Test the initialization of a WalletAddress with a key."""
    assert wallet_address_with_key.network_id == "base-sepolia"
    assert wallet_address_with_key.address_id == "0x1234567890123456789012345678901234567890"
    assert wallet_address_with_key.wallet_id == "test-wallet-id-1"
    assert wallet_address_with_key.key is not None
    assert wallet_address_with_key.can_sign


def test_wallet_id_property(wallet_address):
    """Test the wallet_id property of a WalletAddress."""
    assert wallet_address.wallet_id == "test-wallet-id-1"


def test_key_property(wallet_address, wallet_address_with_key):
    """Test the key property of a WalletAddress."""
    assert wallet_address.key is None
    assert wallet_address_with_key.key is not None


def test_key_setter(wallet_address):
    """Test the key setter of a WalletAddress."""
    new_key = Mock(spec=LocalAccount)
    wallet_address.key = new_key
    assert wallet_address.key == new_key


def test_can_sign_property(wallet_address, wallet_address_with_key):
    """Test the can_sign property of a WalletAddress."""
    assert not wallet_address.can_sign
    assert wallet_address_with_key.can_sign


def test_key_setter_raises_error_when_already_set(wallet_address_with_key):
    """Test the key setter raises an error when already set."""
    new_key = Mock(spec=LocalAccount)
    with pytest.raises(ValueError, match="Private key is already set"):
        wallet_address_with_key.key = new_key


@patch("cdp.wallet_address.Transfer")
@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", True)
def test_transfer_with_server_signer(
    mock_api_clients, mock_transfer, wallet_address, balance_model
):
    """Test the transfer method with a server signer."""
    mock_transfer_instance = Mock(spec=Transfer)
    mock_transfer.create.return_value = mock_transfer_instance

    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    transfer = wallet_address.transfer(amount="1.0", asset_id="eth", destination="0xdestination")

    assert isinstance(transfer, Transfer)
    mock_get_balance.assert_called_once_with(
        network_id=wallet_address.network_id, address_id=wallet_address.address_id, asset_id="eth"
    )
    mock_transfer.create.assert_called_once_with(
        address_id=wallet_address.address_id,
        amount=Decimal("1.0"),
        asset_id="eth",
        destination="0xdestination",
        network_id=wallet_address.network_id,
        wallet_id=wallet_address.wallet_id,
        gasless=False,
    )
    mock_transfer_instance.sign.assert_not_called()
    mock_transfer_instance.broadcast.assert_not_called()


@patch("cdp.wallet_address.Transfer")
@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", False)
def test_transfer(mock_api_clients, mock_transfer, wallet_address_with_key, balance_model):
    """Test the transfer method."""
    mock_transfer_instance = Mock(spec=Transfer)
    mock_transfer.create.return_value = mock_transfer_instance

    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    transfer = wallet_address_with_key.transfer(
        amount="1.0", asset_id="eth", destination="0xdestination"
    )

    assert isinstance(transfer, Transfer)
    mock_get_balance.assert_called_once_with(
        network_id=wallet_address_with_key.network_id,
        address_id=wallet_address_with_key.address_id,
        asset_id="eth",
    )
    mock_transfer.create.assert_called_once_with(
        address_id=wallet_address_with_key.address_id,
        amount=Decimal("1.0"),
        asset_id="eth",
        destination="0xdestination",
        network_id=wallet_address_with_key.network_id,
        wallet_id=wallet_address_with_key.wallet_id,
        gasless=False,
    )
    mock_transfer_instance.sign.assert_called_once_with(wallet_address_with_key.key)
    mock_transfer_instance.broadcast.assert_called_once()


@patch("cdp.wallet_address.Transfer")
@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", False)
def test_transfer_create_api_error(
    mock_api_clients, mock_transfer, wallet_address_with_key, balance_model
):
    """Test the transfer method raises an error when the create API call fails."""
    mock_transfer.create.side_effect = Exception("API Error")

    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    with pytest.raises(Exception, match="API Error"):
        wallet_address_with_key.transfer(amount="1.0", asset_id="eth", destination="0xdestination")

    mock_get_balance.assert_called_once_with(
        network_id=wallet_address_with_key.network_id,
        address_id=wallet_address_with_key.address_id,
        asset_id="eth",
    )
    mock_transfer.create.assert_called_once_with(
        address_id=wallet_address_with_key.address_id,
        amount=Decimal("1.0"),
        asset_id="eth",
        destination="0xdestination",
        network_id=wallet_address_with_key.network_id,
        wallet_id=wallet_address_with_key.wallet_id,
        gasless=False,
    )


@patch("cdp.wallet_address.Transfer")
@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", False)
def test_transfer_broadcast_api_error(
    mock_api_clients, mock_transfer, wallet_address_with_key, balance_model
):
    """Test the transfer method raises an error when the broadcast API call fails."""
    mock_transfer_instance = Mock(spec=Transfer)
    mock_transfer_instance.broadcast.side_effect = Exception("API Error")
    mock_transfer.create.return_value = mock_transfer_instance

    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    with pytest.raises(Exception, match="API Error"):
        wallet_address_with_key.transfer(amount="1.0", asset_id="eth", destination="0xdestination")

    mock_get_balance.assert_called_once_with(
        network_id=wallet_address_with_key.network_id,
        address_id=wallet_address_with_key.address_id,
        asset_id="eth",
    )
    mock_transfer.createassert_called_once_with(
        address_id=wallet_address_with_key.address_id,
        amount=Decimal("1.0"),
        asset_id="eth",
        destination="0xdestination",
        network_id=wallet_address_with_key.network_id,
        wallet_id=wallet_address_with_key.wallet_id,
        gasless=False,
    )
    mock_transfer_instance.sign.assert_called_once_with(wallet_address_with_key.key)
    mock_transfer_instance.broadcast.assert_called_once()


@patch("cdp.wallet_address.Trade")
@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", True)
def test_trade(mock_api_clients, mock_trade, wallet_address, balance_model):
    """Test the trade method with a server signer."""
    mock_trade.create.return_value = Mock(spec=Trade)

    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    trade = wallet_address.trade(amount="1.0", from_asset_id="eth", to_asset_id="usdc")

    assert isinstance(trade, Trade)
    mock_trade.create.assert_called_once_with(
        address_id=wallet_address.address_id,
        from_asset_id="eth",
        to_asset_id="usdc",
        amount=Decimal("1.0"),
        network_id=wallet_address.network_id,
        wallet_id=wallet_address.wallet_id,
    )


@patch("cdp.wallet_address.Trade")
@patch("cdp.Cdp.api_clients")
@patch("cdp.Cdp.use_server_signer", False)
def test_trade_with_client_signer(
    mock_api_clients, mock_trade, wallet_address_with_key, balance_model
):
    """Test the trade method."""
    mock_trade_instance = Mock(spec=Trade)
    mock_trade.create.return_value = mock_trade_instance

    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    trade = wallet_address_with_key.trade(amount="1.0", from_asset_id="eth", to_asset_id="usdc")

    assert isinstance(trade, Trade)
    mock_get_balance.assert_called_once_with(
        network_id=wallet_address_with_key.network_id,
        address_id=wallet_address_with_key.address_id,
        asset_id="eth",
    )
    mock_trade_instance.transaction.sign.assert_called_once_with(wallet_address_with_key.key)
    mock_trade_instance.approve_transaction.sign.assert_called_once_with(
        wallet_address_with_key.key
    )
    mock_trade_instance.broadcast.assert_called_once()


@patch("cdp.wallet_address.Transfer")
def test_transfers(mock_transfer, wallet_address):
    """Test the transfers method."""
    mock_transfer.list.return_value = iter([Mock(spec=Transfer), Mock(spec=Transfer)])

    transfers = wallet_address.transfers()

    assert len(list(transfers)) == 2
    assert all(isinstance(t, Transfer) for t in transfers)
    mock_transfer.list.assert_called_once_with(
        wallet_id=wallet_address.wallet_id, address_id=wallet_address.address_id
    )


@patch("cdp.wallet_address.Transfer")
def test_transfers_api_error(mock_transfer, wallet_address):
    """Test the transfers method raises an error when the API call fails."""
    mock_transfer.list.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        wallet_address.transfers()


@patch("cdp.wallet_address.Trade")
def test_trades(mock_trade, wallet_address):
    """Test the trades method."""
    mock_trade.list.return_value = iter([Mock(spec=Trade), Mock(spec=Trade)])

    trades = wallet_address.trades()

    assert len(list(trades)) == 2
    assert all(isinstance(t, Trade) for t in trades)
    mock_trade.list.assert_called_once_with(
        wallet_id=wallet_address.wallet_id, address_id=wallet_address.address_id
    )


@patch("cdp.wallet_address.Trade")
def test_trades_api_error(mock_trade, wallet_address):
    """Test the trades method raises an error when the API call fails."""
    mock_trade.list.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        wallet_address.trades()


@patch("cdp.Cdp.api_clients")
def test_ensure_sufficient_balance_sufficient(mock_api_clients, wallet_address, balance_model):
    """Test the ensure_sufficient_balance method with sufficient balance."""
    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    wallet_address._ensure_sufficient_balance(Decimal("1.5"), "eth")

    mock_get_balance.assert_called_once_with(
        network_id=wallet_address.network_id, address_id=wallet_address.address_id, asset_id="eth"
    )


@patch("cdp.Cdp.api_clients")
def test_ensure_sufficient_balance_insufficient(mock_api_clients, wallet_address, balance_model):
    """Test the ensure_sufficient_balance method with insufficient balance."""
    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    with pytest.raises(InsufficientFundsError):
        wallet_address._ensure_sufficient_balance(Decimal("100.0"), "eth")

    mock_get_balance.assert_called_once_with(
        network_id=wallet_address.network_id, address_id=wallet_address.address_id, asset_id="eth"
    )


def test_str_representation(wallet_address):
    """Test the str representation of a WalletAddress."""
    expected_str = "WalletAddress: (address_id: 0x1234567890123456789012345678901234567890, wallet_id: test-wallet-id-1, network_id: base-sepolia)"
    assert str(wallet_address) == expected_str


def test_repr(wallet_address):
    """Test the repr representation of a WalletAddress."""
    expected_repr = "WalletAddress: (address_id: 0x1234567890123456789012345678901234567890, wallet_id: test-wallet-id-1, network_id: base-sepolia)"
    assert repr(wallet_address) == expected_repr
