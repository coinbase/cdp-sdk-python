from decimal import Decimal

import pytest

from cdp.client.models.crypto_amount import CryptoAmount as CryptoAmountModel
from cdp.crypto_amount import CryptoAmount


@pytest.fixture
def crypto_amount_model_factory(asset_model_factory):
    """Create and return a factory for creating CryptoAmountModel fixtures."""

    def _create_crypto_amount_model(asset_id="USDC", decimals=6, amount="1"):
        asset_model = asset_model_factory("base-sepolia", asset_id, decimals)
        return CryptoAmountModel(amount=amount, asset=asset_model)

    return _create_crypto_amount_model


@pytest.fixture
def crypto_amount_factory(asset_factory):
    """Create and return a factory for creating CryptoAmount fixtures."""

    def _create_crypto_amount(asset_id="USDC", decimals=6, amount="1"):
        asset = asset_factory("base-sepolia", asset_id, decimals)
        return CryptoAmount(Decimal(amount), asset)

    return _create_crypto_amount
