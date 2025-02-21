import pytest
from eth_account import Account


@pytest.fixture
def account_factory():
    """Create and return a factory for test accounts."""

    def _create_account(private_key="0x" + "1" * 64):
        return Account.from_key(private_key)

    return _create_account
