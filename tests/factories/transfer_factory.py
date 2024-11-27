import pytest

from cdp.client.models.transfer import Transfer as TransferModel
from cdp.transfer import Transfer


@pytest.fixture
def transfer_model_factory(
    asset_model_factory, sponsored_send_model_factory, transaction_model_factory
):
    """Create and return a factory for creating TransferModel fixtures."""

    def _create_transfer_model(gasless=True, status="complete", asset_id="usdc"):
        asset_model = asset_model_factory(asset_id=asset_id)
        if gasless:
            sponsored_send_model = sponsored_send_model_factory(status)
            transaction_model = None
        else:
            sponsored_send_model = None
            transaction_model = transaction_model_factory(status)

        return TransferModel(
            network_id="base-sepolia",
            wallet_id="test-wallet-id",
            address_id="0xaddressid",
            destination="0xdestination",
            amount="1000000",  # 1 USDC or 1 ETH in wei
            asset_id=asset_model.asset_id,
            transfer_id="test-transfer-id",
            asset=asset_model,
            gasless=gasless,
            sponsored_send=sponsored_send_model,
            transaction=transaction_model,
        )

    return _create_transfer_model


@pytest.fixture
def transfer_factory(transfer_model_factory):
    """Create and return a factory for creating Transfer fixtures."""

    def _create_transfer(gasless=True, status="complete", asset_id="usdc"):
        transfer_model = transfer_model_factory(gasless, status, asset_id)
        return Transfer(transfer_model)

    return _create_transfer
