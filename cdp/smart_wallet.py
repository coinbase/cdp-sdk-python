from eth_account.signers.base import BaseAccount
from web3 import Web3

from cdp.cdp import Cdp
from cdp.client.models.call import Call
from cdp.client.models.create_smart_wallet_request import CreateSmartWalletRequest
from cdp.evm_call_types import ContractCall, FunctionCall
from cdp.network import Network
from cdp.user_operation import UserOperation


class SmartWallet:
    """A class representing a smart wallet."""

    def __init__(self, address: str, account: BaseAccount) -> None:
        """Initialize the SmartWallet class.

        Args:
            address (str): The smart wallet address.
            account (BaseAccount): The owner of the smart wallet.

        """
        self.__address = address
        self.__owners = [account]

    @property
    def address(self) -> str:
        """Get the Smart Wallet Address.

        Returns:
            str: The Smart Wallet Address.

        """
        return self.__address

    @property
    def owners(self) -> list[BaseAccount]:
        """Get the wallet owners.

        Returns:
            List[BaseAccount]: List of owner accounts

        """
        return self.__owners

    @classmethod
    def create(
        cls,
        account: BaseAccount,
    ) -> "SmartWallet":
        """Create a new smart wallet.

        Returns:
            SmartWallet: The created smart wallet object.

        Raises:
            Exception: If there's an error creating the EVM smart wallet.

        """
        create_smart_wallet_request = CreateSmartWalletRequest(owner=account.address)
        model = Cdp.api_clients.smart_wallets.create_smart_wallet(create_smart_wallet_request)
        return SmartWallet(model.address, account)

    def use_network(
        self, chain_id: int, paymaster_url: str | None = None
    ) -> "NetworkScopedSmartWallet":
        """Configure the wallet for a specific network.

        Args:
            chain_id (int): The chain ID of the network to connect to
            paymaster_url (Optional[str]): Optional URL for the paymaster service

        Returns:
            NetworkScopedSmartWallet: A network-scoped version of the wallet

        """
        return NetworkScopedSmartWallet(self.__address, self.owners[0], chain_id, paymaster_url)

    def send_user_operation(
        self, calls: list[ContractCall], chain_id: int, paymaster_url: str | None = None
    ) -> UserOperation:
        """Send a user operation.

        Args:
            calls (List[EVMCall]): The calls to send.
            chain_id (int): The chain ID.
            paymaster_url (str): The paymaster URL.

        Returns:
            UserOperation: The user operation object.

        Raises:
            ValueError: If the default address does not exist.

        """
        network = Network.from_chain_id(chain_id)

        if not calls:
            raise ValueError("Calls list cannot be empty")

        encoded_calls = []
        for call in calls:
            if isinstance(call, FunctionCall):
                contract = Web3().eth.contract(address=call.to, abi=call.abi)
                data = contract.encode_abi(call.function_name, args=call.args)
                value = "0" if call.value is None else str(call.value)
                encoded_calls.append(Call(to=str(call.to), data=data, value=value))
            else:
                value = "0" if call.value is None else str(call.value)
                data = "0x" if call.data is None else call.data
                encoded_calls.append(Call(to=str(call.to), data=data, value=value))

        user_operation = UserOperation.create(
            self.__address,
            network.network_id,
            encoded_calls,
            paymaster_url,
        )

        owner = self.owners[0]
        user_operation.sign(owner)
        user_operation.broadcast()
        return user_operation

    def __str__(self) -> str:
        """Return a string representation of the SmartWallet object.

        Returns:
            str: A string representation of the SmartWallet.

        """
        return f"Smart Wallet Address: {self.address}"

    def __repr__(self) -> str:
        """Return a string representation of the Wallet object.

        Returns:
            str: A string representation of the Wallet.

        """
        return str(self)


class NetworkScopedSmartWallet(SmartWallet):
    """A smart wallet that's configured for a specific network."""

    def __init__(
        self,
        smart_wallet_address: str,
        account: BaseAccount,
        chain_id: int,
        paymaster_url: str | None = None,
    ) -> None:
        """Initialize the NetworkScopedSmartWallet.

        Args:
            smart_wallet_address (str): The smart wallet address
            account (BaseAccount): The account that owns the smart wallet
            chain_id (int): The chain ID
            paymaster_url (Optional[str]): The paymaster URL

        """
        super().__init__(smart_wallet_address, account)
        self.__chain_id = chain_id
        self.__paymaster_url = paymaster_url

    @property
    def chain_id(self) -> int:
        """Get the chain ID.

        Returns:
            int: The chain ID.

        """
        return self.__chain_id

    @property
    def paymaster_url(self) -> str | None:
        """Get the paymaster URL.

        Returns:
            str | None: The paymaster URL.

        """
        return self.__paymaster_url

    def send_user_operation(
        self,
        calls: list[ContractCall],
    ) -> UserOperation:
        """Send a user operation on the configured network.

        Args:
            calls (List[EVMCall]): The calls to send.

        Returns:
            UserOperation: The user operation object.

        Raises:
            ValueError: If there's an error sending the operation.

        """
        return super().send_user_operation(
            calls=calls, chain_id=self.chain_id, paymaster_url=self.paymaster_url
        )

    def __str__(self) -> str:
        """Return a string representation of the NetworkScopedSmartWallet.

        Returns:
            str: A string representation of the smart wallet.

        """
        return f"Network Scoped Smart Wallet: {self.address} (Chain ID: {self.chain_id})"

    def __repr__(self) -> str:
        """Return a detailed string representation of the NetworkScopedSmartWallet.

        Returns:
            str: A detailed string representation of the smart wallet.

        """
        return f"Network Scoped Smart Wallet: (model=SmartWalletModel(address='{self.address}'), network=Network(chain_id={self.chain_id}, paymaster_url={self.paymaster_url!r}))"


def to_smart_wallet(smart_wallet_address: str, signer: BaseAccount) -> "SmartWallet":
    """Construct an existing smart wallet by its address and the signer.

    Args:
        smart_wallet_address (str): The address of the smart wallet to retrieve.
        signer (BaseAccount): The signer to use for the smart wallet.

    Returns:
        SmartWallet: The retrieved smart wallet object.

    Raises:
        Exception: If there's an error retrieving the smart wallet.

    """
    return SmartWallet(smart_wallet_address, signer)
