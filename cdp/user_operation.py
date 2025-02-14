from decimal import Decimal
import time

from cdp.call_types import Call
from cdp.client.models.user_operation import UserOperation as UserOperationModel
from cdp.smart_wallet import SmartWallet


class UserOperation:
    """A class representing a user operation."""

    def __init__(self, model: UserOperationModel) -> None:
        """Initialize the UserOperation class.

        Args:
            model (UserOperationModel): The model representing the user operation.

        """
        self._model = model

    @property
    def user_operation_id(self) -> str:
        """Get the user operation ID.

        Returns:
            str: The user operation ID.

        """
        return self._model.user_operation_id

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
        # TODO: Implement


    def wait(
        self, interval_seconds: float = 0.2, timeout_seconds: float = 20
    ) -> "UserOperation":
        """Wait until the user operation is processed or fails by polling the server.

        Args:
            interval_seconds: The interval at which to poll the server.
            timeout_seconds: The maximum time to wait before timing out.

        Returns:
            UserOperation: The completed user operation.

        Raises:
            TimeoutError: If the user operation takes longer than the given timeout.

        """
        # TODO: implement. Note: Will not have a reload function - will simply have the logic here.


    def __str__(self) -> str:
        """Return a string representation of the user operation."""
        return (
            f"UserOperation: (user_operation_id: {self.user_operation_id}, smart_wallet_address: {self.smart_wallet_address}, status: {self.status})"
        )

    def __repr__(self) -> str:
        """Return a string representation of the user operation."""
        return str(self)
