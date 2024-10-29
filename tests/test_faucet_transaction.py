from unittest.mock import Mock, patch

import pytest

from cdp.client.exceptions import ApiException
from cdp.errors import ApiError
from cdp.faucet_transaction import FaucetTransaction
from cdp.transaction import Transaction


def test_faucet_tx_initialization(faucet_transaction_factory):
    """Test the initialization of a FaucetTransaction."""
    faucet_transaction = faucet_transaction_factory()

    assert isinstance(faucet_transaction, FaucetTransaction)
    assert faucet_transaction.transaction_hash == "0xtransactionhash"
    assert faucet_transaction.network_id == "base-sepolia"
    assert faucet_transaction.address_id == "0xdestination"
