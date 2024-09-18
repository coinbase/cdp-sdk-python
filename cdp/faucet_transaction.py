from cdp.client.models.faucet_transaction import (
    FaucetTransaction as FaucetTransactionModel,
)


class FaucetTransaction:
    """A class representing a faucet transaction."""

    def __init__(self, model: FaucetTransactionModel) -> None:
        """Initialize the FaucetTransaction class.

        Args:
            model: The model representing the faucet transaction.

        """
        self._model = model

    @property
    def transaction_hash(self) -> str:
        """Get the transaction hash.

        Returns:
            str: The transaction hash.

        """
        return self._model.transaction_hash

    @property
    def transaction_link(self) -> str:
        """Get the transaction link.

        Returns:
            str: The transaction link.

        """
        return self._model.transaction_link

    def __str__(self) -> str:
        """Return a string representation of the FaucetTransaction."""
        return f"FaucetTransaction: (transaction_hash: {self.transaction_hash}, transaction_link: {self.transaction_link})"

    def __repr__(self) -> str:
        """Return a string representation of the FaucetTransaction."""
        return str(self)
