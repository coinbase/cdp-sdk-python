from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from cdp.asset import Asset
from cdp.client.models.asset import Asset as AssetModel


@pytest.fixture
def asset_model():
    """Create and return a fixture for asset model."""
    return AssetModel(network_id="ethereum-goerli", asset_id="eth", decimals=18)


@pytest.fixture
def asset(asset_model):
    """Create and return a fixture for asset."""
    return Asset.from_model(asset_model)


def test_asset_initialization(asset):
    """Test asset initialization."""
    assert asset.network_id == "ethereum-goerli"
    assert asset.asset_id == "eth"
    assert asset.decimals == 18


def test_asset_from_model(asset_model):
    """Test asset from model."""
    asset = Asset.from_model(asset_model)
    assert isinstance(asset, Asset)
    assert asset.network_id == asset_model.network_id
    assert asset.asset_id == asset_model.asset_id
    assert asset.decimals == asset_model.decimals


def test_asset_from_model_with_gwei(asset_model):
    """Test asset from model with gwei."""
    asset = Asset.from_model(asset_model, asset_id="gwei")
    assert asset.decimals == 9


def test_asset_from_model_with_wei(asset_model):
    """Test asset from model with wei."""
    asset = Asset.from_model(asset_model, asset_id="wei")
    assert asset.decimals == 0


def test_asset_from_model_with_invalid_asset_id(asset_model):
    """Test asset from model with invalid asset ID."""
    with pytest.raises(ValueError, match="Unsupported asset ID: invalid"):
        Asset.from_model(asset_model, asset_id="invalid")


@patch("cdp.Cdp.api_clients")
def test_asset_fetch(mock_api_clients, asset_model):
    """Test asset fetch."""
    mock_get_asset = Mock()
    mock_get_asset.return_value = asset_model
    mock_api_clients.assets.get_asset = mock_get_asset

    asset = Asset.fetch("ethereum-goerli", "eth")
    assert isinstance(asset, Asset)
    assert asset.network_id == "ethereum-goerli"
    assert asset.asset_id == "eth"
    mock_get_asset.assert_called_once_with(network_id="ethereum-goerli", asset_id="eth")


@patch("cdp.Cdp.api_clients")
def test_asset_fetch_api_error(mock_api_clients):
    """Test asset fetch API error."""
    mock_get_asset = Mock()
    mock_get_asset.side_effect = Exception("API error")
    mock_api_clients.assets.get_asset = mock_get_asset

    with pytest.raises(Exception, match="API error"):
        Asset.fetch("ethereum-goerli", "eth")


@pytest.mark.parametrize(
    "input_asset_id, expected_output",
    [
        ("eth", "eth"),
        ("wei", "eth"),
        ("gwei", "eth"),
        ("usdc", "usdc"),
    ],
)
def test_primary_denomination(input_asset_id, expected_output):
    """Test primary denomination."""
    assert Asset.primary_denomination(input_asset_id) == expected_output


def test_from_atomic_amount(asset):
    """Test from atomic amount."""
    assert asset.from_atomic_amount(Decimal("1000000000000000000")) == Decimal("1")
    assert asset.from_atomic_amount(Decimal("500000000000000000")) == Decimal("0.5")


def test_to_atomic_amount(asset):
    """Test to atomic amount."""
    assert asset.to_atomic_amount(Decimal("1")) == Decimal("1000000000000000000")
    assert asset.to_atomic_amount(Decimal("0.5")) == Decimal("500000000000000000")


def test_asset_str_representation(asset):
    """Test asset string representation."""
    expected_str = (
        "Asset: (asset_id: eth, network_id: ethereum-goerli, contract_address: None, decimals: 18)"
    )
    assert str(asset) == expected_str


def test_asset_repr(asset):
    """Test asset repr."""
    expected_repr = (
        "Asset: (asset_id: eth, network_id: ethereum-goerli, contract_address: None, decimals: 18)"
    )
    assert repr(asset) == expected_repr
