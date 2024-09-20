from decimal import Decimal

import pytest

from cdp.asset import Asset
from cdp.balance import Balance
from cdp.client.models.asset import Asset as AssetModel
from cdp.client.models.balance import Balance as BalanceModel


@pytest.fixture
def asset_model():
    """Create and return a fixture for an AssetModel."""
    return AssetModel(network_id="ethereum-goerli", asset_id="eth", decimals=18)


@pytest.fixture
def asset(asset_model):
    """Create and return a fixture for an Asset."""
    return Asset.from_model(asset_model)


@pytest.fixture
def balance_model(asset_model):
    """Create and return a fixture for a BalanceModel."""
    return BalanceModel(amount="1000000000000000000", asset=asset_model)


@pytest.fixture
def balance(asset):
    """Create and return a fixture for a Balance."""
    return Balance(Decimal("1.5"), asset)


def test_balance_initialization(asset):
    """Test balance initialization."""
    balance = Balance(Decimal("1"), asset)
    assert balance.amount == Decimal("1")
    assert balance.asset == asset
    assert balance.asset_id == "eth"


def test_balance_initialization_with_asset_id(asset):
    """Test balance initialization with asset ID."""
    balance = Balance(Decimal("10"), asset, asset_id="gwei")
    assert balance.amount == Decimal("10")
    assert balance.asset == asset
    assert balance.asset_id == "gwei"


def test_balance_from_model(balance_model):
    """Test balance from model."""
    balance = Balance.from_model(balance_model)
    assert balance.amount == Decimal("1")
    assert isinstance(balance.asset, Asset)
    assert balance.asset.asset_id == "eth"
    assert balance.asset_id == "eth"


def test_balance_from_model_with_asset_id(balance_model):
    """Test balance from model with asset ID."""
    balance = Balance.from_model(balance_model, asset_id="gwei")
    assert balance.amount == Decimal("1000000000")
    assert isinstance(balance.asset, Asset)
    assert balance.asset.asset_id == "eth"
    assert balance.asset_id == "gwei"


def test_balance_amount(balance):
    """Test balance amount."""
    assert balance.amount == Decimal("1.5")


def test_balance_asset(balance, asset):
    """Test balance asset."""
    assert balance.asset == asset


def test_balance_asset_id(balance, asset):
    """Test balance asset ID."""
    assert balance.asset_id == asset.asset_id


def test_balance_str_representation(asset):
    """Test balance string representation."""
    balance = Balance(Decimal("1.5"), asset)
    assert (
        str(balance)
        == "Balance: (amount: 1.5, asset: Asset: (asset_id: eth, network_id: ethereum-goerli, contract_address: None, decimals: 18))"
    )


def test_balance_repr(asset):
    """Test balance repr."""
    balance = Balance(Decimal("1.5"), asset)
    assert (
        repr(balance)
        == "Balance: (amount: 1.5, asset: Asset: (asset_id: eth, network_id: ethereum-goerli, contract_address: None, decimals: 18))"
    )
