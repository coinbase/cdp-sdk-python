from decimal import Decimal
from unittest.mock import ANY, Mock, call, patch

import pytest

from cdp.asset import Asset
from cdp.client.models.asset import Asset as AssetModel
from cdp.client.models.trade import Trade as TradeModel
from cdp.client.models.transaction import Transaction as TransactionModel
from cdp.errors import TransactionNotSignedError
from cdp.trade import Trade
from cdp.transaction import Transaction


@pytest.fixture
def asset_model_factory():
    """Create and return a factory for creating AssetModel fixtures."""

    def _create_asset_model(network_id="base-sepolia", asset_id="usdc", decimals=6):
        return AssetModel(network_id=network_id, asset_id=asset_id, decimals=decimals)

    return _create_asset_model


@pytest.fixture
def asset_factory(asset_model_factory):
    """Create and return a factory for creating Asset fixtures."""

    def _create_asset(network_id="base-sepolia", asset_id="usdc", decimals=6):
        asset_model = asset_model_factory(network_id, asset_id, decimals)
        return Asset.from_model(asset_model)

    return _create_asset


@pytest.fixture
def transaction_model_factory():
    """Create and return a factory for creating TransactionModel fixtures."""

    def _create_transaction_model(status="complete"):
        return TransactionModel(
            network_id="base-sepolia",
            transaction_hash="0xtransactionhash",
            from_address_id="0xaddressid",
            to_address_id="0xdestination",
            unsigned_payload="0xunsignedpayload",
            signed_payload="0xsignedpayload"
            if status in ["signed", "broadcast", "complete"]
            else None,
            status=status,
            transaction_link="https://sepolia.basescan.org/tx/0xtransactionlink"
            if status == "complete"
            else None,
        )

    return _create_transaction_model


@pytest.fixture
def trade_model_factory(asset_model_factory, transaction_model_factory):
    """Create and return a factory for creating TradeModel fixtures."""

    def _create_trade_model(
        status="complete",
        from_asset_id="usdc",
        to_asset_id="eth",
        from_asset_decimals=6,
        to_asset_decimals=18,
    ):
        from_asset_model = asset_model_factory(asset_id=from_asset_id, decimals=from_asset_decimals)
        to_asset_model = asset_model_factory(asset_id=to_asset_id, decimals=to_asset_decimals)
        transaction_model = transaction_model_factory(status)
        approve_transaction_model = transaction_model_factory(status)

        return TradeModel(
            network_id="base-sepolia",
            wallet_id="test-wallet-id",
            address_id="0xaddressid",
            trade_id="test-trade-id",
            from_asset=from_asset_model,
            to_asset=to_asset_model,
            from_amount="1000000",  # 1 USDC
            to_amount="500000000000000000",  # 0.5 ETH
            transaction=transaction_model,
            approve_transaction=approve_transaction_model,
        )

    return _create_trade_model


@pytest.fixture
def trade_factory(trade_model_factory):
    """Create and return a factory for creating Trade fixtures."""

    def _create_trade(status="complete", from_asset_id="usdc", to_asset_id="eth"):
        trade_model = trade_model_factory(status, from_asset_id, to_asset_id)
        return Trade(trade_model)

    return _create_trade


def test_trade_initialization(trade_factory):
    """Test the initialization of a Trade object."""
    trade = trade_factory()
    assert isinstance(trade, Trade)
    assert isinstance(trade.transaction, Transaction)
    assert isinstance(trade.approve_transaction, Transaction)


def test_trade_properties(trade_factory):
    """Test the properties of a Trade object."""
    trade = trade_factory()
    assert trade.trade_id == "test-trade-id"
    assert trade.network_id == "base-sepolia"
    assert trade.wallet_id == "test-wallet-id"
    assert trade.address_id == "0xaddressid"
    assert trade.from_asset_id == "usdc"
    assert trade.to_asset_id == "eth"
    assert trade.from_amount == Decimal("1")
    assert trade.to_amount == Decimal("0.5")
    assert isinstance(trade.transaction, Transaction)
    assert isinstance(trade.approve_transaction, Transaction)


@patch("cdp.Cdp.api_clients")
@patch("cdp.trade.Asset")
def test_create_trade(mock_asset, mock_api_clients, trade_factory, asset_factory):
    """Test the creation of a Trade object."""
    mock_fetch = Mock()
    mock_fetch.side_effect = [asset_factory(asset_id="usdc"), asset_factory(asset_id="eth")]
    mock_asset.fetch = mock_fetch

    mock_primary_denomination = Mock()
    mock_primary_denomination.side_effect = ["usdc", "eth"]
    mock_asset.primary_denomination = mock_primary_denomination

    mock_create_trade = Mock()
    mock_create_trade.return_value = trade_factory()._model
    mock_api_clients.trades.create_trade = mock_create_trade

    trade = Trade.create(
        address_id="0xaddressid",
        from_asset_id="usdc",
        to_asset_id="eth",
        amount=Decimal("1"),
        network_id="base-sepolia",
        wallet_id="test-wallet-id",
    )

    assert isinstance(trade, Trade)
    mock_fetch.assert_has_calls([call("base-sepolia", "usdc"), call("base-sepolia", "eth")])
    mock_primary_denomination.assert_has_calls([call("usdc"), call("eth")])
    mock_create_trade.assert_called_once_with(
        wallet_id="test-wallet-id", address_id="0xaddressid", create_trade_request=ANY
    )

    create_trade_request = mock_create_trade.call_args[1]["create_trade_request"]
    assert create_trade_request.amount == "1000000"  # 1 USDC in atomic units
    assert create_trade_request.from_asset_id == "usdc"
    assert create_trade_request.to_asset_id == "eth"


@patch("cdp.Cdp.api_clients")
def test_list_trades(mock_api_clients, trade_factory):
    """Test the listing of trades."""
    mock_list_trades = Mock()
    mock_list_trades.return_value = Mock(data=[trade_factory()._model], has_more=False)
    mock_api_clients.trades.list_trades = mock_list_trades

    trades = Trade.list("test-wallet-id", "0xaddressid")

    assert len(list(trades)) == 1
    assert all(isinstance(t, Trade) for t in trades)
    mock_list_trades.assert_called_once_with(
        wallet_id="test-wallet-id", address_id="0xaddressid", limit=100, page=None
    )


@patch("cdp.Cdp.api_clients")
def test_broadcast_trade(mock_api_clients, trade_factory):
    """Test the broadcasting of a Trade object."""
    trade = trade_factory(status="signed")
    broadcast_trade = trade_factory(status="broadcast")
    mock_broadcast = Mock(return_value=broadcast_trade._model)
    mock_api_clients.trades.broadcast_trade = mock_broadcast

    response = trade.broadcast()

    mock_broadcast.assert_called_once_with(
        wallet_id=trade.wallet_id,
        address_id=trade.address_id,
        trade_id=trade.trade_id,
        broadcast_trade_request=ANY,
    )
    assert isinstance(response, Trade)
    assert response.status.value == "broadcast"
    broadcast_trade_request = mock_broadcast.call_args[1]["broadcast_trade_request"]
    assert broadcast_trade_request.signed_payload == trade.transaction.signature
    assert (
        broadcast_trade_request.approve_transaction_signed_payload
        == trade.approve_transaction.signature
    )


def test_broadcast_unsigned_trade(trade_factory):
    """Test the broadcasting of an unsigned Trade object."""
    trade = trade_factory(status="pending")
    with pytest.raises(TransactionNotSignedError, match="Trade is not signed"):
        trade.broadcast()


@patch("cdp.Cdp.api_clients")
@patch("cdp.trade.time.sleep")
@patch("cdp.trade.time.time")
def test_wait_for_trade(mock_time, mock_sleep, mock_api_clients, trade_factory):
    """Test the waiting for a Trade object to complete."""
    pending_trade = trade_factory(status="pending")
    complete_trade = trade_factory(status="complete")
    mock_get_trade = Mock()
    mock_api_clients.trades.get_trade = mock_get_trade
    mock_get_trade.side_effect = [pending_trade._model, complete_trade._model]

    mock_time.side_effect = [0, 0.2, 0.4]

    result = pending_trade.wait(interval_seconds=0.2, timeout_seconds=1)

    assert result.status.value == "complete"
    mock_get_trade.assert_called_with(
        wallet_id=pending_trade.wallet_id,
        address_id=pending_trade.address_id,
        trade_id=pending_trade.trade_id,
    )
    assert mock_get_trade.call_count == 2
    mock_sleep.assert_has_calls([call(0.2)] * 2)
    assert mock_time.call_count == 3


@patch("cdp.Cdp.api_clients")
@patch("cdp.trade.time.sleep")
@patch("cdp.trade.time.time")
def test_wait_for_trade_timeout(mock_time, mock_sleep, mock_api_clients, trade_factory):
    """Test the waiting for a Trade object to complete with a timeout."""
    pending_trade = trade_factory(status="pending")
    mock_get_trade = Mock(return_value=pending_trade._model)
    mock_api_clients.trades.get_trade = mock_get_trade

    mock_time.side_effect = [0, 0.5, 1.0, 1.5, 2.0, 2.5]

    with pytest.raises(TimeoutError, match="Timed out waiting for Trade to land onchain"):
        pending_trade.wait(interval_seconds=0.5, timeout_seconds=2)

    assert mock_get_trade.call_count == 5
    mock_sleep.assert_called_with(0.5)
    assert mock_time.call_count == 6


def test_trade_str_representation(trade_factory):
    """Test the string representation of a Trade object."""
    trade = trade_factory()
    expected_str = f"Trade: (trade_id: {trade.trade_id}, address_id: {trade.address_id}, wallet_id: {trade.wallet_id}, network_id: {trade.network_id})"
    assert str(trade) == expected_str


def test_trade_repr(trade_factory):
    """Test the representation of a Trade object."""
    trade = trade_factory()
    assert repr(trade) == str(trade)
