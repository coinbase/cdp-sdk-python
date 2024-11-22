from decimal import Decimal
from unittest.mock import Mock, patch

from cdp.asset import Asset
from cdp.fund_quote import FundQuote


def test_fund_quote_initialization(fund_quote_factory):
    """Test the initialization of a FundQuote object."""
    fund_quote = fund_quote_factory()
    assert isinstance(fund_quote, FundQuote)


def test_fund_quote_properties(fund_quote_factory):
    """Test the properties of a FundQuote object."""
    fund_quote = fund_quote_factory()
    assert fund_quote.amount.amount == Decimal("2")
    assert fund_quote.fiat_amount == Decimal("100")
    assert fund_quote.buy_fee["amount"] == "1"
    assert fund_quote.transfer_fee.amount == Decimal("0.01")
    assert isinstance(fund_quote.asset, Asset)


@patch("cdp.Cdp.api_clients")
@patch("cdp.fund_quote.Asset")
def test_fund_quote_create(mock_asset, mock_api_clients, asset_factory, fund_quote_factory):
    """Test the creation of a FundQuote object."""
    mock_fetch = Mock()
    mock_fetch.return_value = asset_factory(asset_id="eth", decimals=18)
    mock_asset.fetch = mock_fetch

    mock_primary_denomination = Mock()
    mock_primary_denomination.return_value = "eth"
    mock_asset.primary_denomination = mock_primary_denomination

    mock_create_fund_quote = Mock()
    mock_create_fund_quote.return_value = fund_quote_factory()._model
    mock_api_clients.fund.create_fund_quote = mock_create_fund_quote

    fund_quote = FundQuote.create(
        wallet_id="test-wallet-id",
        address_id="test-address-id",
        amount=Decimal("2"),
        asset_id="eth",
        network_id="base-sepolia",
    )
    assert isinstance(fund_quote, FundQuote)
    mock_fetch.assert_called_once_with("base-sepolia", "eth")
    mock_primary_denomination.assert_called_once_with("eth")
    mock_create_fund_quote.assert_called_once_with(
        wallet_id="test-wallet-id",
        address_id="test-address-id",
        create_fund_quote_request={
            "asset_id": "eth",
            "amount": "2000000000000000000",
        },
    )


@patch("cdp.fund_operation.FundOperation")
def test_fund_quote_execute(mock_fund_operation, fund_quote_factory):
    """Test the execution of a FundQuote object."""
    mock_create = Mock()
    mock_fund_operation.create = mock_create

    fund_quote = fund_quote_factory()
    fund_quote.execute()
    mock_create.assert_called_once_with(
        wallet_id=fund_quote.wallet_id,
        address_id=fund_quote.address_id,
        amount=fund_quote.amount.amount,
        asset_id=fund_quote.asset.asset_id,
        network_id=fund_quote.network_id,
        quote=fund_quote,
    )


def test_fund_quote_str(fund_quote_factory):
    """Test the string representation of a FundQuote object."""
    fund_quote = fund_quote_factory()
    assert (
        str(fund_quote)
        == "FundQuote(network_id: base-sepolia, wallet_id: test-wallet-id, address_id: test-address-id, crypto_amount: 2, crypto_asset: eth, fiat_amount: 100, fiat_currency: USD, buy_fee: {'amount': '1'}, transfer_fee: {'amount': '0.01'})"
    )


def test_fund_quote_repr(fund_quote_factory):
    """Test the string representation of a FundQuote object."""
    fund_quote = fund_quote_factory()
    assert (
        repr(fund_quote)
        == "FundQuote(network_id: base-sepolia, wallet_id: test-wallet-id, address_id: test-address-id, crypto_amount: 2, crypto_asset: eth, fiat_amount: 100, fiat_currency: USD, buy_fee: {'amount': '1'}, transfer_fee: {'amount': '0.01'})"
    )
