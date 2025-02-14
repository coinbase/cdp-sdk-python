
from eth_account import Account

from cdp.call_types import Call
from cdp.client.models.smart_wallet import SmartWallet as SmartWalletModel
from cdp.smart_wallet import SmartWallet
from cdp.user_operation import UserOperation


class NetworkScopedSmartWallet(SmartWallet):
    """A smart wallet that's configured for a specific network."""

    def __init__(
        self,
        model: SmartWalletModel,
        account: Account,
        chain_id: int,
        paymaster_url: str | None = None,
    ) -> None:
        """Initialize the NetworkScopedSmartWallet.

        Args:
            model (SmartWalletModel): The smart wallet model
            account (Account): The account that owns the smart wallet
            chain_id (int): The chain ID
            paymaster_url (Optional[str]): The paymaster URL

        """
        super().__init__(model, account)
        self.chain_id = chain_id
        self.paymaster_url = paymaster_url

    def send_user_operation(
        self,
        calls: list[Call],
    ) -> UserOperation:
        """Send a user operation on the configured network.

        Args:
            calls (List[Call]): The calls to send.

        Returns:
            UserOperation: The user operation object.

        Raises:
            ValueError: If there's an error sending the operation.

        """
        return super().send_user_operation(
            calls=calls, chain_id=self.network.chain_id, paymaster_url=self.network.paymaster_url
        )

    def __str__(self) -> str:
        """Return a string representation of the NetworkScopedSmartWallet.

        Returns:
            str: A string representation of the wallet.

        """
        return f"Network Scoped Smart Wallet: {self.address} (Chain ID: {self.network.chain_id})"

    def __repr__(self) -> str:
        """Return a detailed string representation of the NetworkScopedSmartWallet.

        Returns:
            str: A detailed string representation of the wallet.

        """
        return f"NetworkScopedSmartWallet(model=SmartWalletModel(address='{self.address}'), network=Network(chain_id={self.network.chain_id}, paymaster_url={self.network.paymaster_url!r}))"
