import time
from collections.abc import Iterator
from decimal import Decimal

from eth_account.signers.local import LocalAccount

from cdp.asset import Asset
from cdp.cdp import Cdp
from cdp.client.models.broadcast_transfer_request import BroadcastTransferRequest
from cdp.client.models.create_transfer_request import CreateTransferRequest
from cdp.client.models.transfer import Transfer as TransferModel
from cdp.client.models.transfer_list import TransferList
from cdp.errors import TransactionNotSignedError
from cdp.sponsored_send import SponsoredSend
from cdp.transaction import Transaction


class Transfer:
    """A class representing a transfer."""

    def __init__(self, model: TransferModel) -> None:
        """Initialize the Transfer class.

        Args:
            model (TransferModel): The model representing the transfer.

        """
        self._model = model
        self._transaction = None
        self._sponsored_send = None
        self._asset = None

    @property
    def transfer_id(self) -> str:
        """Get the transfer ID.

        Returns:
            str: The transfer ID.

        """
        return self._model.transfer_id

    @property
    def wallet_id(self) -> str:
        """Get the wallet ID.

        Returns:
            str: The wallet ID.

        """
        return self._model.wallet_id

    @property
    def from_address_id(self) -> str:
        """Get the from address ID.

        Returns:
            str: The from address ID.

        """
        return self._model.address_id

    @property
    def destination_address_id(self) -> str:
        """Get the Destination Address ID of the Transfer."""
        return self._model.destination

    @property
    def network_id(self) -> str:
        """Get the Network ID of the Transfer."""
        return self._model.network_id

    @property
    def asset(self) -> Asset:
        """Get the Asset of the Transfer."""
        if self._asset is None:
            self._asset = Asset.from_model(self._model.asset)
        return self._asset

    @property
    def asset_id(self) -> str:
        """Get the Asset ID of the Transfer."""
        return self._model.asset_id

    @property
    def amount(self) -> Decimal:
        """Get the amount of the asset for the Transfer."""
        return Decimal(self._model.amount) / Decimal(10) ** self._model.asset.decimals

    @property
    def transaction_link(self) -> str:
        """Get the link to the transaction on the blockchain explorer."""
        return self.send_tx_delegate.transaction_link

    @property
    def transaction_hash(self) -> str:
        """Get the Transaction Hash of the Transfer."""
        return self.send_tx_delegate.transaction_hash

    @property
    def status(self) -> str:
        """Get the status.

        Returns:
            str: The status.

        """
        return self.send_tx_delegate.status

    @property
    def transaction(self) -> Transaction | None:
        """Get the Transfer transaction."""
        if self._transaction is None and self._model.transaction is not None:
            self._transaction = Transaction(self._model.transaction)
        return self._transaction

    @property
    def sponsored_send(self) -> SponsoredSend | None:
        """Get the SponsoredSend of the Transfer, if the transfer is gasless."""
        if self._sponsored_send is None and self._model.sponsored_send is not None:
            self._sponsored_send = SponsoredSend(self._model.sponsored_send)
        return self._sponsored_send

    @property
    def send_tx_delegate(self) -> SponsoredSend | Transaction | None:
        """Get the appropriate delegate for the transfer (SponsoredSend or Transaction)."""
        return self.sponsored_send or self.transaction

    @property
    def terminal_state(self) -> bool:
        """Check if the Transfer is in a terminal state."""
        return self.send_tx_delegate.terminal_state

    def _update_transaction(self, model: TransferModel) -> None:
        """Update the transaction with the new model."""
        if model.transaction is not None:
            self._transaction = Transaction(model.transaction)

    def _update_sponsored_send(self, model: TransferModel) -> None:
        """Update the sponsored send with the new model."""
        if model.sponsored_send is not None:
            self._sponsored_send = SponsoredSend(model.sponsored_send)

    @classmethod
    def create(
        cls,
        address_id: str,
        amount: Decimal,
        asset_id: str,
        destination,
        network_id: str,
        wallet_id: str,
        gasless: bool = False,
    ) -> "Transfer":
        """Create a transfer.

        Args:
            address_id (str): The address ID.
            amount (Decimal): The amount.
            asset_id (str): The asset ID.
            destination (Union[Address, Wallet, str]): The destination.
            network_id (str): The network ID.
            wallet_id (str): The wallet ID.
            gasless (bool): Whether to use gasless.

        Returns:
            Transfer: The transfer.

        """
        asset = Asset.fetch(network_id, asset_id)

        if hasattr(destination, "address_id"):
            destination = destination.address_id
        elif hasattr(destination, "default_address"):
            destination = destination.default_address.address_id
        elif isinstance(destination, str):
            destination = destination
        else:
            raise ValueError("Invalid destination type")

        create_transfer_request = CreateTransferRequest(
            amount=str(int(asset.to_atomic_amount(amount))),
            asset_id=Asset.primary_denomination(asset.asset_id),
            destination=destination,
            network_id=network_id,
            gasless=gasless,
        )

        model = Cdp.api_clients.transfers.create_transfer(
            wallet_id=wallet_id,
            address_id=address_id,
            create_transfer_request=create_transfer_request,
        )

        return cls(model)

    @classmethod
    def list(cls, wallet_id: str, address_id: str) -> Iterator["Transfer"]:
        """List transfers.

        Args:
            wallet_id (str): The wallet ID.
            address_id (str): The address ID.

        Returns:
            Iterator[Transfer]: An iterator of transfer objects.

        Raises:
            Exception: If there's an error listing the transfers.

        """
        page = None
        while True:
            response: TransferList = Cdp.api_clients.transfers.list_transfers(
                wallet_id=wallet_id, address_id=address_id, limit=100, page=page
            )

            for transfer_model in response.data:
                yield cls(transfer_model)

            if not response.has_more:
                break

            page = response.next_page

    def sign(self, key: LocalAccount) -> "Transfer":
        """Sign the Transfer with the given key.

        Args:
            key (LocalAccount): The key to sign the Transfer with.

        Returns:
            Transfer: The Transfer object.

        Raises:
            ValueError: If the key is not a LocalAccount.

        """
        if not isinstance(key, LocalAccount):
            raise ValueError("key must be a LocalAccount")

        self.send_tx_delegate.sign(key)

        return self

    def broadcast(self) -> "Transfer":
        """Broadcast the Transfer to the Network.

        Returns:
            Transfer: The Transfer object.

        Raises:
            TransactionNotSignedError: If the Transfer is not signed.

        """
        if not self.send_tx_delegate.signed:
            raise TransactionNotSignedError("Transfer is not signed")

        broadcast_transfer_request = BroadcastTransferRequest(
            signed_payload=self.send_tx_delegate.signature
        )

        model = Cdp.api_clients.transfers.broadcast_transfer(
            wallet_id=self.wallet_id,
            address_id=self.from_address_id,
            transfer_id=self.transfer_id,
            broadcast_transfer_request=broadcast_transfer_request,
        )

        self._model = model
        self._update_transaction(model)
        self._update_sponsored_send(model)

        return self

    def wait(self, interval_seconds: float = 0.2, timeout_seconds: float = 20) -> "Transfer":
        """Wait for the transfer to complete.

        Args:
            interval_seconds (float): The interval seconds.
            timeout_seconds (float): The timeout seconds.

        Returns:
            Transfer: The transfer.

        """
        start_time = time.time()

        while not self.terminal_state:
            self.reload()

            if time.time() - start_time > timeout_seconds:
                raise TimeoutError("Timed out waiting for Transfer to land onchain")

            time.sleep(interval_seconds)

        return self

    def reload(self) -> None:
        """Reload the transfer.

        Returns:
            None

        """
        model = Cdp.api_clients.transfers.get_transfer(
            self.wallet_id, self.from_address_id, self.transfer_id
        )
        self._model = model
        self._update_transaction(model)
        self._update_sponsored_send(model)
        return

    def __str__(self) -> str:
        """Get a string representation of the Transfer."""
        return (
            f"Transfer: (transfer_id: {self.transfer_id}, network_id: {self.network_id}, "
            f"from_address_id: {self.from_address_id}, destination_address_id: {self.destination_address_id}, "
            f"asset_id: {self.asset_id}, amount: {self.amount}, transaction_link: {self.transaction_link}, "
            f"status: {self.status})"
        )

    def __repr__(self) -> str:
        """Get a string representation of the Transfer."""
        return str(self)
