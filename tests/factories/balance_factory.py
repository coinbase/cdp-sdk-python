import pytest

from cdp.balance import Balance
from cdp.client.models.balance import Balance as BalanceModel


@pytest.fixture
def balance_model_factory(asset_model_factory):
    """Create and return a factory for creating BalanceModel fixtures."""

    def _create_balance_model(
        amount="1000000000000000000", network_id="base-sepolia", asset_id="eth", decimals=18
    ):
        asset_model = asset_model_factory(network_id, asset_id, decimals)
        return BalanceModel(amount=amount, asset=asset_model)

    return _create_balance_model


@pytest.fixture
def balance_factory(asset_factory):
    """Create and return a factory for creating Balance fixtures."""

    def _create_balance(
        amount="1000000000000000000", network_id="base-sepolia", asset_id="eth", decimals=18
    ):
        asset = asset_factory(network_id="base-sepolia", asset_id="eth", decimals=18)
        return Balance(amount, asset)

    return _create_balance
