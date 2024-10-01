from decimal import Decimal

from cdp.asset import Asset
from cdp.balance import Balance


def test_balance_initialization(asset_factory):
    """Test balance initialization."""
    asset = asset_factory(asset_id="eth", decimals=18)

    balance = Balance(Decimal("1"), asset)
    assert balance.amount == Decimal("1")
    assert balance.asset == asset
    assert balance.asset_id == "eth"


def test_balance_initialization_with_asset_id(asset_factory):
    """Test balance initialization with asset ID."""
    asset = asset_factory(asset_id="eth", decimals=18)

    balance = Balance(Decimal("10"), asset, asset_id="gwei")
    assert balance.amount == Decimal("10")
    assert balance.asset == asset
    assert balance.asset_id == "gwei"


def test_balance_from_model(balance_model_factory):
    """Test balance from model."""
    balance_model = balance_model_factory()

    balance = Balance.from_model(balance_model)
    assert balance.amount == Decimal("1")
    assert isinstance(balance.asset, Asset)
    assert balance.asset.asset_id == "eth"
    assert balance.asset_id == "eth"


def test_balance_from_model_with_asset_id(balance_model_factory):
    """Test balance from model with asset ID."""
    balance_model = balance_model_factory()

    balance = Balance.from_model(balance_model, asset_id="gwei")
    assert balance.amount == Decimal("1000000000")
    assert isinstance(balance.asset, Asset)
    assert balance.asset.asset_id == "eth"
    assert balance.asset_id == "gwei"


def test_balance_amount(balance_factory):
    """Test balance amount."""
    balance = balance_factory(amount=1.5)

    assert balance.amount == Decimal("1.5")


def test_balance_str_representation(balance_factory):
    """Test balance string representation."""
    balance = balance_factory(amount=1.5)
    assert (
        str(balance)
        == "Balance: (amount: 1.5, asset: Asset: (asset_id: eth, network_id: base-sepolia, contract_address: None, decimals: 18))"
    )


def test_balance_repr(balance_factory):
    """Test balance repr."""
    balance = balance_factory(amount=1.5)
    assert (
        repr(balance)
        == "Balance: (amount: 1.5, asset: Asset: (asset_id: eth, network_id: base-sepolia, contract_address: None, decimals: 18))"
    )
