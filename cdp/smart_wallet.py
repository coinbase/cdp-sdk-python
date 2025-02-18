from eth_account.account import BaseAccount

from cdp.client.models.smart_wallet import SmartWallet as SmartWalletModel
from cdp.evm_call_types import Call
from cdp.network_scoped_smart_wallet import NetworkScopedSmartWallet
from cdp.user_operation import UserOperation


class SmartWallet:
    """A class representing a smart wallet."""

    def __init__(self, model: SmartWalletModel, account: BaseAccount) -> None:
        """Initialize the SmartWallet class.

        Args:
            model (SmartWalletModel): The SmartWalletModel object representing the smart wallet.
            account (Account): The owner of the smart wallet.

        """
        self._model = model
        self.owners = [account]

    @property
    def address(self) -> str:
        """Get the Smart Wallet Address.

        Returns:
            str: The Smart Wallet Address.

        """
        return self._model.address

    @property
    def owners(self) -> list[BaseAccount]:
        """Get the wallet owners.

        Returns:
            List[BaseAccount]: List of owner accounts

        """
        return self.owners

    @classmethod
    def create(
        cls,
        account: BaseAccount,
    ) -> "SmartWallet":
        """Create a new smart wallet.

        Returns:
            Wallet: The created wallet object.

        Raises:
            Exception: If there's an error creating the wallet.

        """
        # TODO: Implement

    def use_network(
        self, chain_id: int, paymaster_url: str | None = None
    ) -> NetworkScopedSmartWallet:
        """Configure the wallet for a specific network.

        Args:
            chain_id (int): The chain ID of the network to connect to
            paymaster_url (Optional[str]): Optional URL for the paymaster service

        Returns:
            NetworkScopedSmartWallet: A network-scoped version of the wallet

        """
        return NetworkScopedSmartWallet(self._model, self.owners[0], chain_id, paymaster_url)

    def send_user_operation(
        self,
        calls: list[Call],
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


def to_smart_wallet(smart_wallet_address: str, signer: BaseAccount) -> "SmartWallet":
    """Fetch a smart wallet by its address.

    Args:
        smart_wallet_address (str): The address of the smart wallet to retrieve.
        signer (Account): The signer to use for the smart wallet.

    Returns:
        SmartWallet: The retrieved smart wallet object.

    Raises:
        Exception: If there's an error retrieving the smart wallet.

    """
    # TODO implement - return object
