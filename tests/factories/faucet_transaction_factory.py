import pytest

from cdp.client.models.faucet_transaction import FaucetTransaction as FaucetTransactionModel
from cdp.faucet_transaction import FaucetTransaction


@pytest.fixture
def faucet_transaction_model_factory(transaction_model_factory):
    """Create and return a factory for creating FaucetTransactionModel fixtures."""

    def _create_faucet_tx_model(status="complete"):
        transaction_model = transaction_model_factory(status)

        if transaction_model.transaction_hash is None:
            raise ValueError("Faucet transaction must have a hash.")

        if transaction_model.transaction_link is None:
            raise ValueError("Faucet transaction must have a link.")

        return FaucetTransactionModel(
            transaction=transaction_model,
            transaction_hash=transaction_model.transaction_hash,
            transaction_link=transaction_model.transaction_link,
        )

    return _create_faucet_tx_model


@pytest.fixture
def faucet_transaction_factory(faucet_transaction_model_factory):
    """Create and return a factory for creating FaucetTransaction fixtures."""

    def _create_faucet_transaction(status="complete"):
        faucet_tx_model = faucet_transaction_model_factory(status)
        return FaucetTransaction(faucet_tx_model)

    return _create_faucet_transaction
