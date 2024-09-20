from enum import Enum

from eth_account.signers.local import LocalAccount
from eth_utils import to_bytes, to_hex

from cdp.client.models import SponsoredSend as SponsoredSendModel


class SponsoredSend:
    """A representation of an onchain Sponsored Send."""

    def __init__(self, model: SponsoredSendModel):
        """Initialize a new SponsoredSend object.

        Args:
            model (SponsoredSendModel): The underlying SponsoredSend object.

        Raises:
            TypeError: If model is not of type SponsoredSendModel.

        """
        if not isinstance(model, SponsoredSendModel):
            raise TypeError("model must be of type SponsoredSendModel")
        self._model = model
        self._signature: str | None = None

    class Status(Enum):
        """Enumeration of SponsoredSend statuses."""

        PENDING = "pending"
        SIGNED = "signed"
        SUBMITTED = "submitted"
        COMPLETE = "complete"
        FAILED = "failed"

        @classmethod
        def terminal_states(cls):
            """Get the terminal states.

            Returns:
                List[str]: The terminal states.

            """
            return [cls.COMPLETE, cls.FAILED]

        def __str__(self) -> str:
            """Return a string representation of the Status."""
            return self.value

        def __repr__(self) -> str:
            """Return a string representation of the Status."""
            return str(self)

    @property
    def typed_data_hash(self) -> str:
        """Get the Keccak256 hash of the typed data.

        Returns:
            str: The Keccak256 hash of the typed data.

        """
        return self._model.typed_data_hash

    @property
    def signature(self) -> str | None:
        """Get the signature of the typed data.

        Returns:
            Optional[str]: The signature, if available.

        """
        return self._signature or self._model.signature

    def sign(self, key: LocalAccount) -> str:
        """Sign the Transaction with the provided key.

        Args:
            key (LocalAccount): The Ethereum account to sign with.

        Returns:
            str: The hex-encoded signed payload.

        Raises:
            ValueError: If the transaction is already signed.

        """
        if self.signed:
            raise ValueError("Transaction is already signed")

        signed_message = key.unsafe_sign_hash(to_bytes(hexstr=self.typed_data_hash))
        self._signature = to_hex(signed_message.signature)
        return self._signature

    @property
    def signed(self) -> bool:
        """Check if the Transaction has been signed.

        Returns:
            bool: True if signed, False otherwise.

        """
        return self.signature is not None

    @property
    def status(self) -> Status:
        """Get the status of the Transaction.

        Returns:
            Status: The current status.

        """
        return self.Status(self._model.status)

    @property
    def terminal_state(self) -> bool:
        """Check if the Sponsored Send is in a terminal state.

        Returns:
            bool: True if in a terminal state, False otherwise.

        """
        return self.status in self.Status.terminal_states()

    @property
    def transaction_hash(self) -> str:
        """Get the Transaction Hash of the Transaction.

        Returns:
            str: The Transaction Hash.

        """
        return self._model.transaction_hash

    @property
    def transaction_link(self) -> str:
        """Get the link to the transaction on the blockchain explorer.

        Returns:
            str: The link to the transaction.

        """
        return self._model.transaction_link

    def __str__(self) -> str:
        """Get a string representation of the SponsoredSend.

        Returns:
            str: A string representation of the SponsoredSend.

        """
        return (
            f"SponsoredSend: (status: {self.status.value}, "
            f"transaction_hash: {self.transaction_hash}, "
            f"transaction_link: {self.transaction_link})"
        )

    def __repr__(self) -> str:
        """Get a string representation of the SponsoredSend.

        Returns:
            str: A string representation of the SponsoredSend.

        """
        return str(self)
