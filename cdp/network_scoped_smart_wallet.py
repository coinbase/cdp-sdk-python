from eth_account.signers.base import BaseAccount

from cdp.evm_call_types import EVMCall
from cdp.smart_wallet import SmartWallet
from cdp.user_operation import UserOperation


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
        self.chain_id = chain_id
        self.paymaster_url = paymaster_url

    def send_user_operation(
        self,
        calls: list[EVMCall],
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
