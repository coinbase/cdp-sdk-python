import pytest

from cdp.client.models.trade import Trade as TradeModel
from cdp.trade import Trade


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
