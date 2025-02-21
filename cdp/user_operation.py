import time
from enum import Enum

from eth_account.signers.base import BaseAccount

from cdp.cdp import Cdp
from cdp.client.models.broadcast_user_operation_request import BroadcastUserOperationRequest
from cdp.client.models.call import Call
from cdp.client.models.create_user_operation_request import CreateUserOperationRequest
from cdp.client.models.user_operation import UserOperation as UserOperationModel


class UserOperation:
    """A class representing a user operation."""

    class Status(Enum):
        """Enumeration of User Operation statuses."""

        PENDING = "pending"
        SIGNED = "signed"
        BROADCAST = "broadcast"
        COMPLETE = "complete"
        FAILED = "failed"
        UNSPECIFIED = "unspecified"

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

    def __init__(self, model: UserOperationModel, smart_wallet_address: str) -> None:
        """Initialize the UserOperation class.

        Args:
            model (UserOperationModel): The model representing the user operation.
            smart_wallet_address (str): The smart wallet address that created the user operation.

        """
        self._model = model
        self._smart_wallet_address = smart_wallet_address
        self._signature = None

    @property
    def smart_wallet_address(self) -> str:
        """Get the smart wallet address of the user operation.

        Returns:
            str: The smart wallet address.

        """
        return self._smart_wallet_address

    @property
    def user_op_hash(self) -> str:
        """Get the user operation hash.

        Returns:
            str: The user operation hash.

        """
        return self._model.user_op_hash

    @property
    def signature(self) -> str:
        """Get the signature of the user operation.

        Returns:
            str: The signature of the user operation.

        """
        return self._signature

    @property
    def status(self) -> Status:
        """Get the status of the user operation.

        Returns:
            str: The status.

        """
        return self.Status(self._model.status)

    @property
    def terminal_state(self) -> bool:
        """Check if the User Operation is in a terminal state."""
        return self.status in self.Status.terminal_states()

    @property
    def transaction_hash(self) -> str:
        """Get the transaction hash of the user operation.

        Returns:
            str: The transaction hash.

        """
        return self._model.transaction_hash

    @classmethod
    def create(
        cls,
        smart_wallet_address: str,
        network_id: str,
        calls: list[Call],
        paymaster_url: str | None = None,
    ) -> "UserOperation":
        """Create a new UserOperation object.

        Args:
            smart_wallet_address (str): The smart wallet address.
            network_id (str): The Network ID.
            calls (list[Call]): The calls to send.
            paymaster_url (Optional[str]): The paymaster URL.

        Returns:
            UserOperation: The new UserOperation object.

        """
        create_user_operation_request = CreateUserOperationRequest(
            calls=calls,
            paymaster_url=paymaster_url,
        )
        model = Cdp.api_clients.smart_wallets.create_user_operation(
            smart_wallet_address, network_id, create_user_operation_request
        )
        return UserOperation(model, smart_wallet_address)

    def sign(self, account: BaseAccount) -> "UserOperation":
        """Sign the user operation.

        Returns:
            UserOperation: The signed UserOperation.

        """
        signed_message = account.unsafe_sign_hash(self.user_op_hash)
        self._signature = "0x" + signed_message.signature.hex()
        return self

    def broadcast(self) -> "UserOperation":
        """Broadcast the user operation.

        Returns:
            UserOperation: The broadcasted UserOperation.

        """
        broadcast_user_operation_request = BroadcastUserOperationRequest(
            signature=self.signature,
        )
        model = Cdp.api_clients.smart_wallets.broadcast_user_operation(
            smart_wallet_address=self.smart_wallet_address,
            user_op_hash=self.user_op_hash,
            broadcast_user_operation_request=broadcast_user_operation_request,
        )
        return UserOperation(model, self.smart_wallet_address)

    def wait(self, interval_seconds: float = 0.2, timeout_seconds: float = 20) -> "UserOperation":
        """Wait until the user operation is processed or fails by polling the server.

        Args:
            interval_seconds: The interval at which to poll the server.
            timeout_seconds: The maximum time to wait before timing out.

        Returns:
            UserOperation: The completed UserOperation.

        Raises:
            TimeoutError: If the user operation takes longer than the given timeout.

        """
        start_time = time.time()
        while not self.terminal_state:
            self.reload()

            if time.time() - start_time > timeout_seconds:
                raise TimeoutError("User Operation timed out")

            time.sleep(interval_seconds)

        return self

    def reload(self) -> "UserOperation":
        """Reload the UserOperation model with the latest version from the server.

        Returns:
            UserOperation: The updated UserOperation object.

        """
        model = Cdp.api_clients.smart_wallets.get_user_operation(
            smart_wallet_address=self.smart_wallet_address,
            user_op_hash=self.user_op_hash,
        )

        self._model = model

        return self

    def __str__(self) -> str:
        """Return a string representation of the UserOperation."""
        return f"UserOperation: (user_op_hash: {self.user_op_hash}, status: {self.status})"

    def __repr__(self) -> str:
        """Return a string representation of the UserOperation."""
        return str(self)
