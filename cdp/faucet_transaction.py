from cdp.client.models.faucet_transaction import (
    FaucetTransaction as FaucetTransactionModel,
)
from cdp.transaction import Transaction


class FaucetTransaction:
    """A class representing a faucet transaction."""

    def __init__(self, model: FaucetTransactionModel) -> None:
        """Initialize the FaucetTransaction class.

        Args:
            model: The model representing the faucet transaction.

        """
        self._model = model

        if self._model.transaction is None:
            raise ValueError("Faucet transaction is required.")

        self._transaction = Transaction(self._model.transaction)

    @property
    def transaction(self) -> Transaction:
        """Get the Faucet transaction."""
        return self._transaction

    @property
    def network_id(self) -> str:
        """Get the network ID.

        Returns:
            str: The network ID.

        """
        return self.transaction.network_id

    @property
    def address_id(self) -> str:
        """Get the address.

        Returns:
            str: The address.

        """
        return self.transaction.to_address_id

    @property
    def transaction_hash(self) -> str:
        """Get the transaction hash.

        Returns:
            str: The transaction hash.

        """
        return self.transaction.transaction_hash

    @property
    def transaction_link(self) -> str:
        """Get the transaction link.

        Returns:
            str: The transaction link.

        """
        return self.transaction.transaction_hash

    @property
    def status(self) -> str:
        """Get the faucet transaction status.

        Returns:
            str: The facuet transaction status.

        """
        return self.transaction.status


    def __str__(self) -> str:
        """Return a string representation of the FaucetTransaction."""
        return f"FaucetTransaction: (transaction_hash: {self.transaction_hash}, transaction_link: {self.transaction_link})"

    def __repr__(self) -> str:
        """Return a string representation of the FaucetTransaction."""
        return str(self)
