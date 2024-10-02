import pytest

from cdp.client.models.historical_balance import HistoricalBalance as HistoricalBalanceModel
from cdp.historical_balance import HistoricalBalance


@pytest.fixture
def historical_balance_model_factory(asset_model_factory):
    """Create and return a factory for creating HistoricalBalance fixtures."""

    def _create_historical_balance_model(
        amount="1000000000000000000",
        network_id="base-sepolia",
        asset_id="eth",
        decimals=18,
        block_hash="0xblockhash",
        block_height="12345"
    ):
        asset_model = asset_model_factory(network_id, asset_id, decimals)
        return HistoricalBalanceModel(
            amount=amount, block_hash=block_hash, block_height=block_height, asset=asset_model)

    return _create_historical_balance_model


@pytest.fixture
def historical_balance_factory(asset_factory):
    """Create and return a factory for creating HistoricalBalance fixtures."""

    def _create_historical_balance(
        amount="1000000000000000000",
        network_id="base-sepolia",
        asset_id="eth",
        decimals=18,
        block_hash="0xblockhash",
        block_height="12345"
    ):
        asset = asset_factory(network_id=network_id, asset_id=asset_id, decimals=decimals)
        return HistoricalBalance(amount, asset, block_height, block_hash)

    return _create_historical_balance
