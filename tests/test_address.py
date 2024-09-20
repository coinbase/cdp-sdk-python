from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from cdp.address import Address
from cdp.balance_map import BalanceMap
from cdp.client.exceptions import ApiException
from cdp.client.models.asset import Asset as AssetModel
from cdp.client.models.balance import Balance as BalanceModel
from cdp.errors import ApiError
from cdp.faucet_transaction import FaucetTransaction


@pytest.fixture
def address():
    """Create and return a fixture for an Address."""
    return Address(
        network_id="base-sepolia", address_id="0x1234567890123456789012345678901234567890"
    )


@pytest.fixture
def asset_model():
    """Create and return a fixture for an AssetModel."""
    return AssetModel(network_id="base-sepolia", asset_id="eth", decimals=18)


@pytest.fixture
def balance_model(asset_model):
    """Create and return a fixture for a BalanceModel."""
    return BalanceModel(amount="1000000000000000000", asset=asset_model)


def test_address_initialization(address):
    """Test the initialization of an Address."""
    assert address.network_id == "base-sepolia"
    assert address.address_id == "0x1234567890123456789012345678901234567890"


def test_address_can_sign(address):
    """Test the can_sign property of an Address."""
    assert not address.can_sign


@patch("cdp.Cdp.api_clients")
def test_address_faucet(mock_api_clients, address):
    """Test the faucet method of an Address."""
    mock_request_faucet = Mock()
    mock_request_faucet.return_value = Mock(spec=FaucetTransaction)
    mock_api_clients.external_addresses.request_external_faucet_funds = mock_request_faucet

    faucet_tx = address.faucet()

    assert isinstance(faucet_tx, FaucetTransaction)
    mock_request_faucet.assert_called_once_with(
        network_id=address.network_id, address_id=address.address_id, asset_id=None
    )


@patch("cdp.Cdp.api_clients")
def test_address_faucet_with_asset_id(mock_api_clients, address):
    """Test the faucet method of an Address with an asset_id."""
    mock_request_faucet = Mock()
    mock_request_faucet.return_value = Mock(spec=FaucetTransaction)
    mock_api_clients.external_addresses.request_external_faucet_funds = mock_request_faucet

    faucet_tx = address.faucet(asset_id="usdc")

    assert isinstance(faucet_tx, FaucetTransaction)
    mock_request_faucet.assert_called_once_with(
        network_id=address.network_id, address_id=address.address_id, asset_id="usdc"
    )


@patch("cdp.Cdp.api_clients")
def test_address_faucet_api_error(mock_api_clients, address):
    """Test the faucet method of an Address raises an error when the API call fails."""
    mock_request_faucet = Mock()
    err = ApiException(500, "boom")
    mock_request_faucet.side_effect = ApiError(err, code="boom", message="boom")
    mock_api_clients.external_addresses.request_external_faucet_funds = mock_request_faucet

    with pytest.raises(ApiError):
        address.faucet()


@patch("cdp.Cdp.api_clients")
def test_address_balance(mock_api_clients, address, balance_model):
    """Test the balance method of an Address."""
    mock_get_balance = Mock()
    mock_get_balance.return_value = balance_model
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    balance = address.balance("eth")

    assert isinstance(balance, Decimal)
    assert balance == Decimal("1")
    mock_get_balance.assert_called_once_with(
        network_id=address.network_id, address_id=address.address_id, asset_id="eth"
    )


@patch("cdp.Cdp.api_clients")
def test_address_balance_zero(mock_api_clients, address):
    """Test the balance method of an Address returns 0 when the balance is not found."""
    mock_get_balance = Mock()
    mock_get_balance.return_value = None
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    balance = address.balance("eth")

    assert isinstance(balance, Decimal)
    assert balance == Decimal("0")


@patch("cdp.Cdp.api_clients")
def test_address_balance_api_error(mock_api_clients, address):
    """Test the balance method of an Address raises an error when the API call fails."""
    mock_get_balance = Mock()
    err = ApiException(500, "boom")
    mock_get_balance.side_effect = ApiError(err, code="boom", message="boom")
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    with pytest.raises(ApiError):
        address.balance("eth")


@patch("cdp.Cdp.api_clients")
def test_address_balances(mock_api_clients, address, balance_model):
    """Test the balances method of an Address."""
    mock_list_balances = Mock()
    mock_list_balances.return_value = Mock(data=[balance_model])
    mock_api_clients.external_addresses.list_external_address_balances = mock_list_balances

    balances = address.balances()

    assert isinstance(balances, BalanceMap)
    assert len(balances) == 1
    assert "eth" in balances
    assert balances["eth"] == Decimal("1")
    mock_list_balances.assert_called_once_with(
        network_id=address.network_id, address_id=address.address_id
    )


@patch("cdp.Cdp.api_clients")
def test_address_balances_api_error(mock_api_clients, address):
    """Test the balances method of an Address raises an error when the API call fails."""
    mock_list_balances = Mock()
    err = ApiException(500, "boom")
    mock_list_balances.side_effect = ApiError(err, code="boom", message="boom")
    mock_api_clients.external_addresses.list_external_address_balances = mock_list_balances

    with pytest.raises(ApiError):
        address.balances()


def test_address_str_representation(address):
    """Test the str representation of an Address."""
    expected_str = f"Address: (address_id: {address.address_id}, network_id: {address.network_id})"
    assert str(address) == expected_str


def test_address_repr(address):
    """Test the repr representation of an Address."""
    expected_repr = f"Address: (address_id: {address.address_id}, network_id: {address.network_id})"
    assert repr(address) == expected_repr
