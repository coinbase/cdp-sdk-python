import pytest

from cdp.asset import Asset
from cdp.client.models.asset import Asset as AssetModel


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
