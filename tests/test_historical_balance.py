from decimal import Decimal
from unittest.mock import Mock, patch

from cdp.asset import Asset
from cdp.historical_balance import HistoricalBalance


def test_historical_balance_initialization(asset_factory):
    """Test historical_balance initialization."""
    asset = asset_factory(asset_id="eth", decimals=18)

    historical_balance = HistoricalBalance(Decimal("1"), asset, "12345", "0xblockhash")
    assert historical_balance.amount == Decimal("1")
    assert historical_balance.asset == asset


def test_historical_balance_from_model(historical_balance_model_factory):
    """Test historical_balance from model."""
    historical_balance_model = historical_balance_model_factory()

    balance = HistoricalBalance.from_model(historical_balance_model)
    assert balance.amount == Decimal("1")
    assert isinstance(balance.asset, Asset)
    assert balance.asset.asset_id == "eth"


def test_historical_balance_amount(historical_balance_factory):
    """Test historical balance amount."""
    historical_balance = historical_balance_factory(amount=1.5)

    assert historical_balance.amount == Decimal("1.5")


def test_historical_balance_str_representation(historical_balance_factory):
    """Test historical balance string representation."""
    historical_balance = historical_balance_factory(amount=1.5)
    assert (
        str(historical_balance)
        == "HistoricalBalance: (amount: 1.5, asset: Asset: (asset_id: eth, network_id: base-sepolia, contract_address: None, decimals: 18), block_height: 12345, block_hash: 0xblockhash)"
    )


def test_historical_balance_repr(historical_balance_factory):
    """Test historical balance repr."""
    historical_balance = historical_balance_factory(amount=1.5)
    assert (
        repr(historical_balance)
        == "HistoricalBalance: (amount: 1.5, asset: Asset: (asset_id: eth, network_id: base-sepolia, contract_address: None, decimals: 18), block_height: 12345, block_hash: 0xblockhash)"
    )


@patch("cdp.Cdp.api_clients")
def test_list_historical_balances(mock_api_clients, historical_balance_model_factory):
    """Test the historical_balances method."""
    mock_list_historical_balances = Mock()
    mock_list_historical_balances.return_value = Mock(data=[historical_balance_model_factory()], has_more=False)
    mock_api_clients.balance_history.list_address_historical_balance = mock_list_historical_balances

    historical_balances = HistoricalBalance.list(network_id="test-network-id", address_id="0xaddressid", asset_id="eth")

    assert len(list(historical_balances)) == 1
    assert all(isinstance(h, HistoricalBalance) for h in historical_balances)
    mock_list_historical_balances.assert_called_once_with(
        network_id="test-network-id",
        address_id="0xaddressid",
        asset_id="eth",
        limit=100,
        page=None
    )
