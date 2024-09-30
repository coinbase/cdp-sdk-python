import time
from collections.abc import Iterator
from enum import Enum

from cdp import Cdp
from cdp.client.models.create_payload_signature_request import CreatePayloadSignatureRequest
from cdp.client.models.payload_signature import PayloadSignature as PayloadSignatureModel
from cdp.client.models.payload_signature_list import PayloadSignatureList


class PayloadSignature:
    """A representation of a Payload Signature."""

    class Status(Enum):
        """Enumeration of Payload Signature statuses."""

        PENDING = "pending"
        SIGNED = "signed"
        FAILED = "failed"

        @classmethod
        def terminal_states(cls):
            """Get the terminal states.

            Returns:
                List[str]: The terminal states.

            """
            return [cls.SIGNED, cls.FAILED]

        def __str__(self) -> str:
            """Return a string representation of the Status."""
            return self.value

        def __repr__(self) -> str:
            """Return a string representation of the Status."""
            return str(self)

    def __init__(self, model: PayloadSignatureModel) -> None:
        """Initialize the PayloadSignature class.

        Args:
            model (PayloadSignatureModel): The model representing the paylaod signature.

        """
        if not isinstance(model, PayloadSignatureModel):
            raise TypeError("model must be of type PayloadSignatureModel")

        self._model = model

    @property
    def payload_signature_id(self) -> str:
        """Get the payload signature ID.

        Returns:
            str: The payload signature ID.

        """
        return self._model.payload_signature_id

    @property
    def wallet_id(self) -> str:
        """Get the wallet ID.

        Returns:
            str: The wallet ID.

        """
        return self._model.wallet_id

    @property
    def address_id(self) -> str:
        """Get the address ID.

        Returns:
            str: The address ID.

        """
        return self._model.address_id

    @property
    def unsigned_payload(self) -> str:
        """Get the unsigned payload.

        Returns:
            str: The unsigned payload.

        """
        return self._model.unsigned_payload

    @property
    def signature(self) -> str:
        """Get the signature.

        Returns:
            str: The signature.

        """
        return self._model.signature

    @property
    def status(self) -> Status:
        """Get the status.

        Returns:
            PayloadSignature.Status: The status.

        """
        return self.Status(self._model.status)

    @property
    def terminal_state(self) -> bool:
        """Check if the Transaction is in a terminal state.

        Returns:
            bool: Whether the paylaod signature is in a terminal state.

        """
        return self.status in self.Status.terminal_states()

    def reload(self) -> None:
        """Reload the payload signature."""
        model = Cdp.api_clients.addresses.get_payload_signature(
            self.wallet_id, self.address_id, self.payload_signature_id
        )
        self._model = model

    def wait(
        self, interval_seconds: float = 0.2, timeout_seconds: float = 20
    ) -> "PayloadSignature":
        """Wait for the payload signature to complete.

        Args:
            interval_seconds (float): The interval seconds.
            timeout_seconds (float): The timeout seconds.

        Returns:
            PayloadSignature: The payload signature.

        """
        start_time = time.time()

        while not self.terminal_state:
            self.reload()

            if time.time() - start_time > timeout_seconds:
                raise TimeoutError("Timed out waiting for PayloadSignature to be signed")

            time.sleep(interval_seconds)

        return self

    @classmethod
    def create(
        cls, wallet_id: str, address_id: str, unsigned_payload: str, signature: str | None = None
    ) -> "PayloadSignature":
        """Create a payload signature.

        Args:
            wallet_id (str): The wallet ID.
            address_id (str): The address ID.
            unsigned_payload (str): The unsigned payload.
            signature (Optional[str]): The signature.

        Returns:
            PayloadSignature: The payload signature.

        Raises:
            Exception: If there's an error creating the payload signature..

        """
        create_payload_signature_request_dict = {"unsigned_payload": unsigned_payload}

        if signature is not None:
            create_payload_signature_request_dict["signature"] = signature

        create_payload_signature_request = CreatePayloadSignatureRequest.from_dict(
            create_payload_signature_request_dict
        )

        model = Cdp.api_clients.addresses.create_payload_signature(
            wallet_id=wallet_id,
            address_id=address_id,
            create_payload_signature_request=create_payload_signature_request,
        )

        return cls(model)

    @classmethod
    def list(cls, wallet_id: str, address_id: str) -> Iterator["PayloadSignature"]:
        """List payload signatures.

        Args:
            wallet_id (str): The wallet ID.
            address_id (str): The address ID.

        Returns:
            Iterator[Payload]: An iterator of payload signatures.

        Raises:
            Exception: If there's an error listing the payload signatures.

        """
        page = None
        while True:
            response: PayloadSignatureList = Cdp.api_clients.addresses.list_payload_signatures(
                wallet_id=wallet_id, address_id=address_id, limit=100, page=page
            )

            for payload_signature_model in response.data:
                yield cls(payload_signature_model)

            if not response.has_more:
                break

            page = response.next_page

    def __str__(self) -> str:
        """Get a string representation of the payload signature."""
        return (
            f"PayloadSignature: (payload_signature_id: {self.payload_signature_id}, wallet_id: {self.wallet_id}, "
            f"address_id: {self.address_id}, unsigned_payload: {self.unsigned_payload}, signature: {self.signature}, "
            f"status: {self.status})"
        )

    def __repr__(self) -> str:
        """Get a string representation of the payload signature."""
        return str(self)
