import pytest

from cdp.address import Address


@pytest.fixture
def address_factory():
    """Create and return a factory for Address fixtures."""

    def _create_address(
        network_id="base-sepolia",
        address_id="0x1234567890123456789012345678901234567890",
    ):
        return Address(network_id, address_id)

    return _create_address
