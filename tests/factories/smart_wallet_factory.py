import pytest

from cdp.client.models.smart_wallet import SmartWallet as SmartWalletModel
from cdp.smart_wallet import SmartWallet


@pytest.fixture
def smart_wallet_model_factory(account_factory):
    """Create and return a factory for WalletModel fixtures."""

    def _create_smart_wallet_model(
        address="0x1234567890123456789012345678901234567890",
        owner=None,
    ):
        if owner is None:
            owner = account_factory()
        return SmartWalletModel(address=address, owners=[owner])

    return _create_smart_wallet_model


@pytest.fixture
def smart_wallet_factory(smart_wallet_model_factory, account_factory):
    """Create and return a factory for SmartWallet fixtures."""

    def _create_smart_wallet(smart_wallet_address, account=account_factory):
        smart_wallet_model = smart_wallet_model_factory(
            address=smart_wallet_address, owner=account.address
        )
        return SmartWallet(smart_wallet_model.address, account)

    return _create_smart_wallet
