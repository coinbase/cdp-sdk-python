from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from cdp.address import Address
from cdp.balance_map import BalanceMap
from cdp.client.exceptions import ApiException
from cdp.errors import ApiError
from cdp.faucet_transaction import FaucetTransaction
from cdp.historical_balance import HistoricalBalance
from cdp.transaction import Transaction


def test_address_initialization(address_factory):
    """Test the initialization of an Address."""
    address = address_factory()

    assert isinstance(address, Address)
    assert address.network_id == "base-sepolia"
    assert address.address_id == "0x1234567890123456789012345678901234567890"


def test_address_can_sign(address_factory):
    """Test the can_sign property of an Address."""
    address = address_factory()

    assert not address.can_sign


@patch("cdp.Cdp.api_clients")
def test_address_faucet(mock_api_clients, address_factory):
    """Test the faucet method of an Address."""
    address = address_factory()

    mock_request_faucet = Mock()
    mock_request_faucet.return_value = Mock(spec=FaucetTransaction)
    mock_api_clients.external_addresses.request_external_faucet_funds = mock_request_faucet

    faucet_tx = address.faucet()

    assert isinstance(faucet_tx, FaucetTransaction)
    mock_request_faucet.assert_called_once_with(
        network_id=address.network_id, address_id=address.address_id, asset_id=None
    )


@patch("cdp.Cdp.api_clients")
def test_address_faucet_with_asset_id(mock_api_clients, address_factory):
    """Test the faucet method of an Address with an asset_id."""
    address = address_factory()

    mock_request_faucet = Mock()
    mock_request_faucet.return_value = Mock(spec=FaucetTransaction)
    mock_api_clients.external_addresses.request_external_faucet_funds = mock_request_faucet

    faucet_tx = address.faucet(asset_id="usdc")

    assert isinstance(faucet_tx, FaucetTransaction)
    mock_request_faucet.assert_called_once_with(
        network_id=address.network_id, address_id=address.address_id, asset_id="usdc"
    )


@patch("cdp.Cdp.api_clients")
def test_address_faucet_api_error(mock_api_clients, address_factory):
    """Test the faucet method of an Address raises an error when the API call fails."""
    address = address_factory()

    mock_request_faucet = Mock()
    err = ApiException(500, "boom")
    mock_request_faucet.side_effect = ApiError(err, code="boom", message="boom")
    mock_api_clients.external_addresses.request_external_faucet_funds = mock_request_faucet

    with pytest.raises(ApiError):
        address.faucet()


@patch("cdp.Cdp.api_clients")
def test_address_balance(mock_api_clients, address_factory, balance_model_factory):
    """Test the balance method of an Address."""
    address = address_factory()
    balance_model = balance_model_factory()

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
def test_address_balance_zero(mock_api_clients, address_factory):
    """Test the balance method of an Address returns 0 when the balance is not found."""
    address = address_factory()

    mock_get_balance = Mock()
    mock_get_balance.return_value = None
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    balance = address.balance("eth")

    assert isinstance(balance, Decimal)
    assert balance == Decimal("0")


@patch("cdp.Cdp.api_clients")
def test_address_balance_api_error(mock_api_clients, address_factory):
    """Test the balance method of an Address raises an error when the API call fails."""
    address = address_factory()

    mock_get_balance = Mock()
    err = ApiException(500, "boom")
    mock_get_balance.side_effect = ApiError(err, code="boom", message="boom")
    mock_api_clients.external_addresses.get_external_address_balance = mock_get_balance

    with pytest.raises(ApiError):
        address.balance("eth")


@patch("cdp.Cdp.api_clients")
def test_address_balances(mock_api_clients, address_factory, balance_model_factory):
    """Test the balances method of an Address."""
    address = address_factory()
    balance_model = balance_model_factory()

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
def test_address_balances_api_error(mock_api_clients, address_factory):
    """Test the balances method of an Address raises an error when the API call fails."""
    address = address_factory()

    mock_list_balances = Mock()
    err = ApiException(500, "boom")
    mock_list_balances.side_effect = ApiError(err, code="boom", message="boom")
    mock_api_clients.external_addresses.list_external_address_balances = mock_list_balances

    with pytest.raises(ApiError):
        address.balances()


@patch("cdp.Cdp.api_clients")
def test_address_historical_balances(
    mock_api_clients, address_factory, historical_balance_model_factory
):
    """Test the historical_balances method of an Address."""
    address = address_factory()
    historical_balance_model = historical_balance_model_factory()

    mock_list_historical_balances = Mock()
    mock_list_historical_balances.return_value = Mock(
        data=[historical_balance_model], has_more=False
    )
    mock_api_clients.balance_history.list_address_historical_balance = mock_list_historical_balances

    historical_balances = address.historical_balances("eth")

    assert len(list(historical_balances)) == 1
    assert all(isinstance(h, HistoricalBalance) for h in historical_balances)
    mock_list_historical_balances.assert_called_once_with(
        network_id=address.network_id,
        address_id=address.address_id,
        asset_id="eth",
        limit=100,
        page=None,
    )


@patch("cdp.Cdp.api_clients")
def test_address_historical_balances_error(mock_api_clients, address_factory):
    """Test the historical_balances method of an Address raises an error when the API call fails."""
    address = address_factory()

    mock_list_historical_balances = Mock()
    err = ApiException(500, "boom")
    mock_list_historical_balances.side_effect = ApiError(err, code="boom", message="boom")
    mock_api_clients.balance_history.list_address_historical_balance = mock_list_historical_balances

    with pytest.raises(ApiError):
        historical_balances = address.historical_balances("eth")
        next(historical_balances)


@patch("cdp.Cdp.api_clients")
def test_address_transactions(mock_api_clients, address_factory, transaction_model_factory):
    """Test the list transactions method of an Address."""
    address = address_factory()
    onchain_transaction_model = transaction_model_factory()

    mock_list_transactions = Mock()
    mock_list_transactions.return_value = Mock(data=[onchain_transaction_model], has_more=False)
    mock_api_clients.transaction_history.list_address_transactions = mock_list_transactions

    transactions = address.transactions()

    assert len(list(transactions)) == 1
    assert all(isinstance(t, Transaction) for t in transactions)
    mock_list_transactions.assert_called_once_with(
        network_id=address.network_id, address_id=address.address_id, limit=1, page=None
    )


@patch("cdp.Cdp.api_clients")
def test_address_transactions_error(mock_api_clients, address_factory):
    """Test the list transactions method of an Address raises an error when the API call fails."""
    address = address_factory()

    mock_list_transactions = Mock()
    err = ApiException(500, "boom")
    mock_list_transactions.side_effect = ApiError(err, code="boom", message="boom")
    mock_api_clients.transaction_history.list_address_transactions = mock_list_transactions

    with pytest.raises(ApiError):
        transactions = address.transactions()
        next(transactions)


def test_address_str_representation(address_factory):
    """Test the str representation of an Address."""
    address = address_factory()

    expected_str = f"Address: (address_id: {address.address_id}, network_id: {address.network_id})"
    assert str(address) == expected_str


def test_address_repr(address_factory):
    """Test the repr representation of an Address."""
    address = address_factory()

    expected_repr = f"Address: (address_id: {address.address_id}, network_id: {address.network_id})"
    assert repr(address) == expected_repr
