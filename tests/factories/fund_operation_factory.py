import pytest

from cdp.client.models.fiat_amount import FiatAmount
from cdp.client.models.fund_operation import FundOperation as FundOperationModel
from cdp.client.models.fund_operation_fees import FundOperationFees
from cdp.fund_operation import FundOperation


@pytest.fixture
def fund_operation_model_factory(
    crypto_amount_model_factory, transaction_model_factory, fund_quote_model_factory
):
    """Create and return a factory for creating FundOperationModel fixtures."""

    def _create_fund_operation_model(
        status="complete", asset_id="eth", amount="2000000000000000000", decimals=18
    ):
        crypto_amount_model = crypto_amount_model_factory(asset_id, decimals, amount)
        transfer_fee_crypto_amount_model = crypto_amount_model_factory(
            asset_id, 18, "10000000000000000"
        )  # 0.01 ETH
        return FundOperationModel(
            fund_operation_id="test-operation-id",
            network_id="base-sepolia",
            wallet_id="test-wallet-id",
            address_id="test-address-id",
            crypto_amount=crypto_amount_model,
            fiat_amount=FiatAmount(amount="100", currency="USD"),
            fees=FundOperationFees(
                buy_fee=FiatAmount(amount="1", currency="USD"),
                transfer_fee=transfer_fee_crypto_amount_model,
            ),
            status=status,
        )

    return _create_fund_operation_model


@pytest.fixture
def fund_operation_factory(fund_operation_model_factory):
    """Create and return a factory for creating FundOperation fixtures."""

    def _create_fund_operation(
        status="complete", asset_id="eth", amount="2000000000000000000", decimals=18
    ):
        fund_operation_model = fund_operation_model_factory(
            status=status, asset_id=asset_id, amount=amount, decimals=decimals
        )
        return FundOperation(fund_operation_model)

    return _create_fund_operation
