from eth_account.account import BaseAccount

from cdp.client.models.smart_wallet import SmartWallet as SmartWalletModel
from cdp.evm_call_types import EVMCall
from cdp.evm_network_scoped_smart_wallet import EVMNetworkScopedSmartWallet
from cdp.evm_user_operation import EVMUserOperation


class EVMSmartWallet:
    """A class representing an EVM smart wallet."""

    def __init__(self, model: SmartWalletModel, account: BaseAccount) -> None:
        """Initialize the EVMSmartWallet class.

        Args:
            model (SmartWalletModel): The SmartWalletModel object representing the smart wallet.
            account (BaseAccount): The owner of the smart wallet.

        """
        self._model = model
        self.owners = [account]

    @property
    def address(self) -> str:
        """Get the EVM Smart Wallet Address.

        Returns:
            str: The EVM Smart Wallet Address.

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
    ) -> "EVMSmartWallet":
        """Create a new EVM smart wallet.

        Returns:
            EVMSmartWallet: The created EVM smart wallet object.

        Raises:
            Exception: If there's an error creating the EVM smart wallet.

        """
        # TODO: Implement

    def use_network(
        self, chain_id: int, paymaster_url: str | None = None
    ) -> EVMNetworkScopedSmartWallet:
        """Configure the wallet for a specific network.

        Args:
            chain_id (int): The chain ID of the network to connect to
            paymaster_url (Optional[str]): Optional URL for the paymaster service

        Returns:
            NetworkScopedSmartWallet: A network-scoped version of the wallet

        """
        return EVMNetworkScopedSmartWallet(self._model, self.owners[0], chain_id, paymaster_url)

    def send_user_operation(
        self,
        calls: list[EVMCall],
        chain_id: int,
        paymaster_url: str,
    ) -> EVMUserOperation:
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


def to_smart_wallet(smart_wallet_address: str, signer: BaseAccount) -> "EVMSmartWallet":
    """Construct an existing EVM smart wallet by its address and the signer.

    Args:
        smart_wallet_address (str): The address of the smart wallet to retrieve.
        signer (BaseAccount): The signer to use for the smart wallet.

    Returns:
        EVMSmartWallet: The retrieved EVM smart wallet object.

    Raises:
        Exception: If there's an error retrieving the EVM smart wallet.

    """
    # TODO implement - return object
