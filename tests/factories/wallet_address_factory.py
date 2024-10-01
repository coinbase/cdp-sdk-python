from unittest.mock import Mock

import pytest
from eth_account.signers.local import LocalAccount

from cdp.client.models.address import Address as AddressModel
from cdp.wallet_address import WalletAddress


@pytest.fixture
def address_model_factory():
    """Create and return a factory for AddressModel fixtures."""

    def _create_address_model(
        network_id="base-sepolia",
        address_id="0x1234567890123456789012345678901234567890",
        wallet_id="test-wallet-id",
        public_key="0xpublickey",
        index=0,
    ):
        return AddressModel(
            network_id=network_id,
            address_id=address_id,
            wallet_id=wallet_id,
            public_key=public_key,
            index=index,
        )

    return _create_address_model


@pytest.fixture
def wallet_address_factory(address_model_factory):
    """Create and return a factory for WalletAddress fixtures."""

    def _create_wallet_address(key=False, **kwargs):
        model = address_model_factory(**kwargs)

        _key = None
        if key:
            _key = Mock(spec=LocalAccount)

        return WalletAddress(model, _key)

    return _create_wallet_address
