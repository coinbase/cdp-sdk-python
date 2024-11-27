import pytest
from bip_utils import Bip32Slip10Secp256k1

from cdp.client.models.feature_set import FeatureSet
from cdp.client.models.wallet import Wallet as WalletModel
from cdp.wallet import Wallet


@pytest.fixture
def wallet_model_factory(address_model_factory):
    """Create and return a factory for WalletModel fixtures."""

    def _create_wallet_model(
        id="test-wallet-id",
        network_id="base-sepolia",
        default_address=None,
        feature_set=None,
        server_signer_status="active_seed",
    ):
        if default_address is None:
            default_address = address_model_factory()
        if feature_set is None:
            feature_set = FeatureSet(
                faucet=True,
                server_signer=True,
                transfer=True,
                trade=True,
                stake=True,
                gasless_send=True,
            )
        return WalletModel(
            id=id,
            network_id=network_id,
            default_address=default_address,
            feature_set=feature_set,
            server_signer_status=server_signer_status,
        )

    return _create_wallet_model


@pytest.fixture
def master_key_factory():
    """Create and return a factory for master key fixtures."""

    def _create_master_key(seed=b"\x00" * 64):
        return Bip32Slip10Secp256k1.FromSeed(seed)

    return _create_master_key


@pytest.fixture
def wallet_factory(wallet_model_factory):
    """Create and return a factory for Wallet fixtures."""

    def _create_wallet(seed=None, **kwargs):
        model = wallet_model_factory(**kwargs)
        return Wallet(model, seed)

    return _create_wallet
