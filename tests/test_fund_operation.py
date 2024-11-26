from decimal import Decimal
from unittest.mock import Mock, call, patch

import pytest

from cdp.asset import Asset
from cdp.fund_operation import FundOperation


def test_fund_operation_initialization(fund_operation_factory):
    """Test the initialization of a FundOperation object."""
    fund_operation = fund_operation_factory()
    assert isinstance(fund_operation, FundOperation)


def test_fund_operation_properties(fund_operation_factory):
    """Test the properties of a FundOperation object."""
    fund_operation = fund_operation_factory()
    assert fund_operation.amount.amount == Decimal("2")
    assert fund_operation.fiat_amount.amount == Decimal("100")
    assert fund_operation.buy_fee["amount"] == "1"
    assert fund_operation.transfer_fee.amount == Decimal("0.01")
    assert fund_operation.status.value == "complete"
    assert isinstance(fund_operation.asset, Asset)


@patch("cdp.Cdp.api_clients")
@patch("cdp.fund_operation.Asset")
def test_fund_operation_create(mock_asset, mock_api_clients, asset_factory, fund_operation_factory):
    """Test the creation of a FundOperation object without a quote."""
    mock_fetch = Mock()
    mock_fetch.return_value = asset_factory(asset_id="eth", decimals=18)
    mock_asset.fetch = mock_fetch

    mock_primary_denomination = Mock()
    mock_primary_denomination.return_value = "eth"
    mock_asset.primary_denomination = mock_primary_denomination

    mock_create_fund_operation = Mock()
    mock_create_fund_operation.return_value = fund_operation_factory()._model
    mock_api_clients.fund.create_fund_operation = mock_create_fund_operation

    fund_operation = FundOperation.create(
        wallet_id="test-wallet-id",
        address_id="test-address-id",
        amount=Decimal("2"),
        asset_id="eth",
        network_id="base-sepolia",
    )
    assert isinstance(fund_operation, FundOperation)
    mock_fetch.assert_called_once_with("base-sepolia", "eth")
    mock_primary_denomination.assert_called_once_with("eth")
    mock_create_fund_operation.assert_called_once_with(
        wallet_id="test-wallet-id",
        address_id="test-address-id",
        create_fund_operation_request={
            "amount": "2000000000000000000",
            "asset_id": "eth",
        },
    )


@patch("cdp.Cdp.api_clients")
@patch("cdp.fund_operation.Asset")
def test_fund_operation_create_with_quote(
    mock_asset, mock_api_clients, asset_factory, fund_operation_factory, fund_quote_factory
):
    """Test the creation of a FundOperation object with a quote."""
    mock_fetch = Mock()
    mock_fetch.return_value = asset_factory(asset_id="eth", decimals=18)
    mock_asset.fetch = mock_fetch

    mock_primary_denomination = Mock()
    mock_primary_denomination.return_value = "eth"
    mock_asset.primary_denomination = mock_primary_denomination

    mock_create_fund_operation = Mock()
    mock_create_fund_operation.return_value = fund_operation_factory()._model
    mock_api_clients.fund.create_fund_operation = mock_create_fund_operation

    fund_operation = FundOperation.create(
        wallet_id="test-wallet-id",
        address_id="test-address-id",
        amount=Decimal("2"),
        asset_id="eth",
        network_id="base-sepolia",
        quote=fund_quote_factory(),
    )
    assert isinstance(fund_operation, FundOperation)
    mock_fetch.assert_called_once_with("base-sepolia", "eth")
    mock_primary_denomination.assert_called_once_with("eth")
    mock_create_fund_operation.assert_called_once_with(
        wallet_id="test-wallet-id",
        address_id="test-address-id",
        create_fund_operation_request={
            "amount": "2000000000000000000",
            "asset_id": "eth",
            "fund_quote_id": "test-quote-id",
        },
    )


@patch("cdp.Cdp.api_clients")
def test_list_fund_operations(mock_api_clients, fund_operation_factory):
    """Test the listing of fund operations."""
    mock_list_fund_operations = Mock()
    mock_list_fund_operations.return_value = Mock(
        data=[fund_operation_factory()._model], has_more=False
    )
    mock_api_clients.fund.list_fund_operations = mock_list_fund_operations
    fund_operations = FundOperation.list("test-wallet-id", "0xaddressid")
    assert len(list(fund_operations)) == 1
    assert all(isinstance(f, FundOperation) for f in fund_operations)
    mock_list_fund_operations.assert_called_once_with(
        wallet_id="test-wallet-id", address_id="0xaddressid", limit=100, page=None
    )


@patch("cdp.Cdp.api_clients")
def test_fund_operation_reload(mock_api_clients, fund_operation_factory):
    """Test the reloading of a FundOperation object."""
    mock_reload_fund_operation = Mock()
    mock_reload_fund_operation.return_value = fund_operation_factory()._model
    mock_api_clients.fund.get_fund_operation = mock_reload_fund_operation

    fund_operation = fund_operation_factory()
    fund_operation.reload()
    mock_reload_fund_operation.assert_called_once_with(
        fund_operation.wallet_id, fund_operation.address_id, fund_operation.id
    )
    assert fund_operation.status.value == "complete"


@patch("cdp.Cdp.api_clients")
@patch("cdp.fund_operation.time.sleep")
@patch("cdp.fund_operation.time.time")
def test_fund_operation_wait(mock_time, mock_sleep, mock_api_clients, fund_operation_factory):
    """Test the waiting for a FundOperation object to complete."""
    pending_fund_operation = fund_operation_factory(status="pending")
    complete_fund_operation = fund_operation_factory(status="complete")
    mock_get_fund_operation = Mock()
    mock_api_clients.fund.get_fund_operation = mock_get_fund_operation
    mock_get_fund_operation.side_effect = [
        pending_fund_operation._model,
        complete_fund_operation._model,
    ]

    mock_time.side_effect = [0, 0.2, 0.4]

    result = pending_fund_operation.wait(interval_seconds=0.2, timeout_seconds=1)

    assert result.status.value == "complete"
    mock_get_fund_operation.assert_called_with(
        pending_fund_operation.wallet_id,
        pending_fund_operation.address_id,
        pending_fund_operation.id,
    )
    assert mock_get_fund_operation.call_count == 2
    mock_sleep.assert_has_calls([call(0.2)] * 2)
    assert mock_time.call_count == 3


@patch("cdp.Cdp.api_clients")
@patch("cdp.fund_operation.time.sleep")
@patch("cdp.fund_operation.time.time")
def test_wait_for_fund_operation_timeout(
    mock_time, mock_sleep, mock_api_clients, fund_operation_factory
):
    """Test the waiting for a FundOperation object to complete with a timeout."""
    pending_fund_operation = fund_operation_factory(status="pending")
    mock_get_fund_operation = Mock(return_value=pending_fund_operation._model)
    mock_api_clients.fund.get_fund_operation = mock_get_fund_operation

    mock_time.side_effect = [0, 0.5, 1.0, 1.5, 2.0, 2.5]

    with pytest.raises(TimeoutError, match="Fund operation timed out"):
        pending_fund_operation.wait(interval_seconds=0.5, timeout_seconds=2)

    mock_get_fund_operation.assert_called_with(
        pending_fund_operation.wallet_id,
        pending_fund_operation.address_id,
        pending_fund_operation.id,
    )
    assert mock_get_fund_operation.call_count == 5
    mock_sleep.assert_has_calls([call(0.5)] * 4)
    assert mock_time.call_count == 6


@pytest.mark.parametrize("status", ["pending", "complete", "failed"])
def test_fund_operation_str_representation(fund_operation_factory, status):
    """Test the string representation of a FundOperation object."""
    fund_operation = fund_operation_factory(status=status)
    expected_str = (
        f"FundOperation(id: {fund_operation.id}, network_id: {fund_operation.network_id}, "
        f"wallet_id: {fund_operation.wallet_id}, address_id: {fund_operation.address_id}, "
        f"amount: {fund_operation.amount}, asset_id: {fund_operation.asset.asset_id}, "
        f"status: {fund_operation.status.value})"
    )
    assert str(fund_operation) == expected_str


@pytest.mark.parametrize("status", ["pending", "complete", "failed"])
def test_fund_operation_repr(fund_operation_factory, status):
    """Test the representation of a FundOperation object."""
    fund_operation = fund_operation_factory(status=status)
    assert repr(fund_operation) == str(fund_operation)
