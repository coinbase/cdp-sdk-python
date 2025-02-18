import time

from eth_account.signers.base import BaseAccount

from cdp.cdp import Cdp
from cdp.client.models.broadcast_user_operation_request import BroadcastUserOperationRequest
from cdp.client.models.create_user_operation_request import CreateUserOperationRequest
from cdp.client.models.user_operation import UserOperation as UserOperationModel
from cdp.evm_call_types import EVMCall


class EVMUserOperation:
    """A class representing an EVM user operation."""

    def __init__(self, model: UserOperationModel) -> None:
        """Initialize the EVMUserOperation class.

        Args:
            model (UserOperationModel): The model representing the user operation.

        """
        self._model = model
        self._signature = None

    @property
    def user_operation_id(self) -> str:
        """Get the user operation ID.

        Returns:
            str: The user operation ID.

        """
        return self._model.user_operation_id

    @property
    def unsigned_payload(self) -> str:
        """Get the unsigned payload of the user operation.

        Returns:
            str: The unsigned payload.

        """
        return self._model.unsigned_payload

    @property
    def smart_wallet_address(self) -> str:
        """Get the smart wallet address of the user operation.

        Returns:
            str: The smart wallet address.

        """
        return self._model.smart_wallet_address

    @property
    def status(self) -> str:
        """Get the status of the contract invocation.

        Returns:
            str: The status.

        """
        return self.transaction.status if self.transaction else None

    @classmethod
    def create(
        cls,
        smart_wallet_address: str,
        network_id: str,
        calls: list[EVMCall],
        paymaster_url: str | None = None,
    ) -> "EVMUserOperation":
        """Create a new EVMUserOperation object.

        Args:
            smart_wallet_address (str): The smart wallet address.
            network_id (str): The Network ID.
            calls (list[EVMCall]): The calls to send.
            paymaster_url (Optional[str]): The paymaster URL.

        Returns:
            EVMUserOperation: The new EVMUserOperation object.

        """
        create_user_operation_request = CreateUserOperationRequest(
            user_operation=CreateUserOperationRequest(
                smart_wallet_address=smart_wallet_address,
                network_id=network_id,
                calls=calls,
                paymaster_url=paymaster_url,
            )
        )
        model = Cdp.api_clients.smart_wallets.create_user_operation(create_user_operation_request)
        return EVMUserOperation(model)

    def sign(self, account: BaseAccount) -> "EVMUserOperation":
        """Sign the user operation.

        Returns:
            EVMUserOperation: The signed EVM user operation.

        """
        self._signature = account.unsafe_sign_hash(self.unsigned_payload)
        return self

    def broadcast(self) -> "EVMUserOperation":
        """Broadcast the user operation.

        Returns:
            EVMUserOperation: The broadcasted EVM user operation.

        """
        broadcast_user_operation_request = BroadcastUserOperationRequest(
            user_operation_id=self.user_operation_id,
            signature=self._signature,
        )
        model = Cdp.api_clients.smart_wallets.broadcast_user_operation(
            broadcast_user_operation_request
        )
        return EVMUserOperation(model)

    def wait(
        self, interval_seconds: float = 0.2, timeout_seconds: float = 20
    ) -> "EVMUserOperation":
        """Wait until the user operation is processed or fails by polling the server.

        Args:
            interval_seconds: The interval at which to poll the server.
            timeout_seconds: The maximum time to wait before timing out.

        Returns:
            EVMUserOperation: The completed EVM user operation.

        Raises:
            TimeoutError: If the EVM user operation takes longer than the given timeout.

        """
        start_time = time.time()
        while not self.status:
            self.reload()

            if time.time() - start_time > timeout_seconds:
                raise TimeoutError("Contract Invocation timed out")

            time.sleep(interval_seconds)

        return self

    def reload(self) -> "EVMUserOperation":
        """Reload the EVMUserOperation model with the latest version from the server.

        Returns:
            EVMUserOperation: The updated EVMUserOperation object.

        """
        model = Cdp.api_clients.smart_wallets.get_user_operation(
            user_operation_id=self.user_operation_id,
        )

        self._model = model

        return self

    def __str__(self) -> str:
        """Return a string representation of the EVM user operation."""
        return f"EVMUserOperation: (user_operation_id: {self.user_operation_id}, smart_wallet_address: {self.smart_wallet_address}, status: {self.status})"

    def __repr__(self) -> str:
        """Return a string representation of the EVM user operation."""
        return str(self)
