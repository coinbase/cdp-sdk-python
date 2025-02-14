from typing import Any, Dict, List, NotRequired, TypedDict, Union

from eth_account import Account

from cdp.call_types import Call
from cdp.client.models.smart_wallet import SmartWallet as SmartWalletModel
from cdp.user_operation import UserOperation


class SmartWallet:
    """A class representing a smart wallet."""

    def __init__(self, model: SmartWalletModel) -> None:
        """Initialize the SmartWallet class.

        Args:
            model (SmartWalletModel): The SmartWalletModel object representing the smart wallet.

        """
        self._model = model
      
    @property
    def address(self) -> str:
        """Get the Smart Wallet Address.

        Returns:
            str: The Smart Wallet Address.

        """
        return self._model.address

    @classmethod
    def create(
        cls,
        account: Account,
    ) -> "SmartWallet":
        """Create a new smart wallet.

        Returns:
            Wallet: The created wallet object.

        Raises:
            Exception: If there's an error creating the wallet.

        """
        # TODO: Implement
        
        
    @classmethod
    def to_smart_wallet(cls, smart_wallet_address: str, signer: Account) -> "SmartWallet":
        """Fetch a smart wallet by its ID.

        Args:
            smart_wallet_address (str): The address of the smart wallet to retrieve.
            signer (Account): The signer to use for the smart wallet.

        Returns:
            SmartWallet: The retrieved smart wallet object.

        Raises:
            Exception: If there's an error retrieving the smart wallet.

        """
        # TODO implement - return object


    def send_user_operation(
        self,
        calls: List[Call],
        chain_id: int,
        paymaster_url: str,
    ) -> UserOperation:
        """Send a user operation.

        Args:
            calls (List[Call]): The calls to send.
            chain_id (int): The chain ID.
            paymaster_url (str): The paymaster URL.

        Returns:
            UserOperation: The user operation object.

        Raises:
            ValueError: If the default address does not exist.

        """
        # TODO implement


    def __str__(self) -> str:
        """Return a string representation of the SmartWallet object.

        Returns:
            str: A string representation of the SmartWallet.

        """
        return f"Smart Wallet Address: (id: {self.id})"

    def __repr__(self) -> str:
        """Return a string representation of the Wallet object.

        Returns:
            str: A string representation of the Wallet.

        """
        return str(self)
