from eth_account.signers.base import BaseAccount
from web3 import Web3

from cdp.cdp import Cdp
from cdp.client.models.create_smart_wallet_request import CreateSmartWalletRequest
from cdp.evm_call_types import EVMAbiCallDict, EVMCall, EVMCallDict
from cdp.evm_network_scoped_smart_wallet import EVMNetworkScopedSmartWallet
from cdp.evm_user_operation import EVMUserOperation
from cdp.network import Network


class EVMSmartWallet:
    """A class representing an EVM smart wallet."""

    def __init__(self, smart_wallet_address: str, account: BaseAccount) -> None:
        """Initialize the EVMSmartWallet class.

        Args:
            smart_wallet_address (str): The smart wallet address.
            account (BaseAccount): The owner of the smart wallet.

        """
        self._smart_wallet_address = smart_wallet_address
        self.owners = [account]

    @property
    def address(self) -> str:
        """Get the EVM Smart Wallet Address.

        Returns:
            str: The EVM Smart Wallet Address.

        """
        return self._smart_wallet_address

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
        create_smart_wallet_request = CreateSmartWalletRequest(
            smart_wallet=CreateSmartWalletRequest(owner=account.address)
        )
        model = Cdp.api_clients.smart_wallets.create_smart_wallet(create_smart_wallet_request)
        return EVMSmartWallet(model.address, [account])

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
        return EVMNetworkScopedSmartWallet(
            self._smart_wallet_address, self.owners[0], chain_id, paymaster_url
        )

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
        network = Network.from_chain_id(chain_id)

        encoded_calls = []
        for call in calls:
            if isinstance(call, EVMAbiCallDict):
                contract = Web3().eth.contract(address=call.to, abi=call.abi)

                encoded_data = contract.encode_abi(call.function_name, args=call.args)

                encoded_call = EVMCallDict(data=encoded_data, to=call.to, value=call.value)
            else:
                encoded_call = EVMCallDict(data=call.data, to=call.to, value=call.value)
            encoded_calls.append(encoded_call)

        user_operation = EVMUserOperation.create(
            smart_wallet_address=self._smart_wallet_address,
            network_id=network.id,
            calls=encoded_calls,
            paymaster_url=paymaster_url,
        )

        # sign time
        owner = self.owners[0]
        user_operation.sign(owner)
        user_operation.broadcast()
        return user_operation

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
    return EVMSmartWallet(smart_wallet_address, [signer])
