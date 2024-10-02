import pytest

from cdp.client.models.transaction import Transaction as TransactionModel
from cdp.transaction import Transaction


@pytest.fixture
def transaction_model_factory():
    """Create and return a factory for creating TransactionModel fixtures."""

    def _create_transaction_model(status="complete"):
        return TransactionModel(
            network_id="base-sepolia",
            transaction_hash="0xtransactionhash",
            from_address_id="0xaddressid",
            to_address_id="0xdestination",
            unsigned_payload="0xunsignedpayload",
            signed_payload="0xsignedpayload"
            if status in ["signed", "broadcast", "complete"]
            else None,
            status=status,
            transaction_link="https://sepolia.basescan.org/tx/0xtransactionlink"
            if status == "complete"
            else None,
            block_hash="0xblockhash" if status == "complete" else None,
            block_height="123456" if status == "complete" else None,
        )

    return _create_transaction_model


@pytest.fixture
def transaction_factory(transaction_model_factory):
    """Create and return a factory for creating Transaction fixtures."""

    def _create_transaction(status="complete"):
        model = transaction_model_factory(status)
        return Transaction(model)

    return _create_transaction
