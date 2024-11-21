import pytest

from cdp.client.models.crypto_amount import CryptoAmount as CryptoAmountModel
from cdp.client.models.asset import Asset as AssetModel
from cdp.crypto_amount import CryptoAmount

@pytest.fixture
def crypto_amount_model_factory(asset_model_factory):
    """Create and return a factory for creating CryptoAmountModel fixtures."""

    def _create_crypto_amount_model(network_id="base-sepolia", asset_id="USDC", decimals=6, amount="1"):
        asset_model = asset_model_factory(network_id, asset_id, decimals)
        return CryptoAmountModel(amount=amount, asset=asset_model)

    return _create_crypto_amount_model


@pytest.fixture
def crypto_amount_factory(crypto_amount_model_factory):
    """Create and return a factory for creating CryptoAmount fixtures."""

    def _create_crypto_amount(network_id="base-sepolia", asset_id="USDC", decimals=6, amount="1"):
        crypto_amount_model = crypto_amount_model_factory(network_id, asset_id, decimals, amount)
        return CryptoAmount.from_model(crypto_amount_model)

    return _create_crypto_amount
