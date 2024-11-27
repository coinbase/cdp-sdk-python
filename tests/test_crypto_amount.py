from decimal import Decimal

from cdp.crypto_amount import CryptoAmount


def test_crypto_amount_initialization(crypto_amount_factory):
    """Test crypto amount initialization."""
    crypto_amount = crypto_amount_factory("USDC", 6, "1")
    assert isinstance(crypto_amount, CryptoAmount)
    assert crypto_amount.amount == Decimal("1")
    assert crypto_amount.asset.asset_id == "USDC"
    assert crypto_amount.asset.network_id == "base-sepolia"
    assert crypto_amount.asset.decimals == 6


def test_crypto_amount_from_model(crypto_amount_model_factory):
    """Test crypto amount from model."""
    crypto_amount_model = crypto_amount_model_factory("USDC", 6, "1")
    crypto_amount = CryptoAmount.from_model(crypto_amount_model)
    assert isinstance(crypto_amount, CryptoAmount)
    assert crypto_amount.amount == (
        Decimal(crypto_amount_model.amount) / Decimal(10) ** crypto_amount_model.asset.decimals
    )
    assert crypto_amount.asset.asset_id == "USDC"
    assert crypto_amount.asset.network_id == "base-sepolia"
    assert crypto_amount.asset.decimals == 6


def test_crypto_amount_from_model_and_asset_id_with_gwei(crypto_amount_model_factory):
    """Test crypto amount from model with gwei."""
    crypto_amount_model = crypto_amount_model_factory("eth", 18, "1")
    crypto_amount = CryptoAmount.from_model_and_asset_id(crypto_amount_model, "gwei")
    assert isinstance(crypto_amount, CryptoAmount)
    assert crypto_amount.amount == (Decimal(crypto_amount_model.amount) / Decimal(10) ** 9)
    assert crypto_amount.asset.asset_id == "gwei"
    assert crypto_amount.asset.network_id == "base-sepolia"
    assert crypto_amount.asset.decimals == 9


def test_crypto_amount_from_model_and_asset_id_with_wei(crypto_amount_model_factory):
    """Test crypto amount from model with wei."""
    crypto_amount_model = crypto_amount_model_factory("eth", 18, "1")
    crypto_amount = CryptoAmount.from_model_and_asset_id(crypto_amount_model, "wei")
    assert isinstance(crypto_amount, CryptoAmount)
    assert crypto_amount.amount == Decimal(crypto_amount_model.amount)
    assert crypto_amount.asset.asset_id == "wei"
    assert crypto_amount.asset.network_id == "base-sepolia"
    assert crypto_amount.asset.decimals == 0


def test_crypto_amount_to_atomic_amount(crypto_amount_factory):
    """Test crypto amount to atomic amount."""
    crypto_amount = crypto_amount_factory()
    assert crypto_amount.to_atomic_amount() == (
        Decimal(crypto_amount.amount) * Decimal(10) ** crypto_amount.asset.decimals
    )


def test_crypto_amount_str_representation(crypto_amount_factory):
    """Test crypto amount string representation."""
    crypto_amount = crypto_amount_factory()
    assert (
        str(crypto_amount)
        == f"CryptoAmount(amount: '{int(crypto_amount.amount)}', asset_id: '{crypto_amount.asset.asset_id}')"
    )


def test_crypto_amount_repr(crypto_amount_factory):
    """Test crypto amount repr."""
    crypto_amount = crypto_amount_factory()
    assert (
        repr(crypto_amount)
        == f"CryptoAmount(amount: '{int(crypto_amount.amount)}', asset_id: '{crypto_amount.asset.asset_id}')"
    )
