import pytest

from cdp.client.models.fund_operation import FundOperation as FundOperationModel
from cdp.fund_operation import FundOperation


@pytest.fixture
def fund_operation_model_factory(
    asset_model_factory, transaction_model_factory, fund_quote_model_factory
):
    """Create and return a factory for creating FundOperationModel fixtures."""

    def _create_fund_operation_model(
        status="complete", operation_type="deposit", asset_id="usdc", amount="1000000"
    ):
        asset_model = asset_model_factory(asset_id=asset_id)
        transaction_model = transaction_model_factory(status)
        fund_quote_model = fund_quote_model_factory(
            operation_type=operation_type, asset_id=asset_id, amount=amount
        )

        return FundOperationModel(
            network_id="base-sepolia",
            wallet_id="test-wallet-id",
            operation_id="test-operation-id",
            operation_type=operation_type,
            status=status,
            amount=amount,
            asset_id=asset_model.asset_id,
            asset=asset_model,
            transaction=transaction_model,
            fund_quote=fund_quote_model,
        )

    return _create_fund_operation_model


@pytest.fixture
def fund_operation_factory(fund_operation_model_factory):
    """Create and return a factory for creating FundOperation fixtures."""

    def _create_fund_operation(
        status="complete", operation_type="deposit", asset_id="usdc", amount="1000000"
    ):
        fund_operation_model = fund_operation_model_factory(
            status=status, operation_type=operation_type, asset_id=asset_id, amount=amount
        )
        return FundOperation(fund_operation_model)

    return _create_fund_operation
