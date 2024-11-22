import pytest

from cdp.client.models.fiat_amount import FiatAmount
from cdp.client.models.fund_operation_fees import FundOperationFees
from cdp.client.models.fund_quote import FundQuote as FundQuoteModel
from cdp.fund_quote import FundQuote


@pytest.fixture
def fund_quote_model_factory(crypto_amount_model_factory):
    """Create and return a factory for creating FundQuoteModel fixtures."""

    def _create_fund_quote_model(amount="2000000000000000000", decimals=18, asset_id="eth"):
        crypto_amount_model = crypto_amount_model_factory(asset_id, decimals, amount)
        transfer_fee_crypto_amount_model = crypto_amount_model_factory(
            asset_id, 18, "10000000000000000"
        )  # 0.01 ETH
        return FundQuoteModel(
            fund_quote_id="test-quote-id",
            network_id="base-sepolia",
            wallet_id="test-wallet-id",
            address_id="test-address-id",
            crypto_amount=crypto_amount_model,
            fiat_amount=FiatAmount(amount="100", currency="USD"),
            expires_at="2024-12-31T23:59:59Z",
            fees=FundOperationFees(
                buy_fee=FiatAmount(amount="1", currency="USD"),
                transfer_fee=transfer_fee_crypto_amount_model,
            ),
        )

    return _create_fund_quote_model


@pytest.fixture
def fund_quote_factory(fund_quote_model_factory):
    """Create and return a factory for creating FundQuote fixtures."""

    def _create_fund_quote(amount="2000000000000000000", decimals=18, asset_id="eth"):
        fund_quote_model = fund_quote_model_factory(
            amount=amount, decimals=decimals, asset_id=asset_id
        )
        return FundQuote(fund_quote_model)

    return _create_fund_quote
