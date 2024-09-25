import time
from collections.abc import Iterator
from decimal import Decimal
from numbers import Number

from cdp.asset import Asset
from cdp.cdp import Cdp
from cdp.client.models.broadcast_trade_request import BroadcastTradeRequest
from cdp.client.models.create_trade_request import CreateTradeRequest
from cdp.client.models.trade import Trade as TradeModel
from cdp.errors import TransactionNotSignedError
from cdp.transaction import Transaction


class Trade:
    """A class representing a trade."""

    def __init__(self, model: TradeModel) -> None:
        """Initialize the Trade class."""
        self._model = model
        self._transaction = None
        self._approve_transaction = None

    @staticmethod
    def create(
        address_id: str,
        from_asset_id: str,
        to_asset_id: str,
        amount: Number | Decimal | str,
        network_id: str,
        wallet_id: str,
    ) -> "Trade":
        """Create a new trade.

        Args:
            address_id (str): The ID of the address to use for the trade.
            from_asset_id (str): The ID of the asset to trade.
            to_asset_id (str): The ID of the asset to receive from the trade.
            amount (Decimal): The amount to trade.
            network_id (str): The ID of the network to use for the trade.
            wallet_id (str): The ID of the wallet to use for the trade.

        Returns:
            Trade: The created trade.

        """
        from_asset = Asset.fetch(network_id, from_asset_id)
        to_asset = Asset.fetch(network_id, to_asset_id)

        create_trade_request = CreateTradeRequest(
            amount=str(int(from_asset.to_atomic_amount(amount))),
            from_asset_id=Asset.primary_denomination(from_asset.asset_id),
            to_asset_id=Asset.primary_denomination(to_asset.asset_id),
        )

        model = Cdp.api_clients.trades.create_trade(
            wallet_id=wallet_id,
            address_id=address_id,
            create_trade_request=create_trade_request,
        )

        return Trade(model)

    @classmethod
    def list(cls, wallet_id: str, address_id: str) -> Iterator["Trade"]:
        """List all trades for an address.

        Args:
            wallet_id (str): The ID of the wallet to list trades for.
            address_id (str): The ID of the address to list trades for.

        Returns:
            Iterator[Trade]: An iterator of trade objects.

        """
        page = None
        while True:
            response = Cdp.api_clients.trades.list_trades(
                wallet_id=wallet_id, address_id=address_id, limit=100, page=page
            )

            for trade_model in response.data:
                yield cls(trade_model)

            if not response.has_more:
                break

            page = response.next_page

    def broadcast(self) -> "Trade":
        """Broadcast the trade.

        Returns:
            Trade: The broadcasted trade.

        Raises:
            TransactionNotSignedError: If the trade is not signed.

        """
        if not self.transaction.signed:
            raise TransactionNotSignedError("Trade is not signed")

        if self.approve_transaction and not self.approve_transaction.signed:
            raise TransactionNotSignedError("Trade is not signed")

        broadcast_trade_request = BroadcastTradeRequest(
            signed_payload=self.transaction.signature,
        )

        if self.approve_transaction is not None:
            broadcast_trade_request.approve_transaction_signed_payload = (
                self.approve_transaction.signature
            )

        model = Cdp.api_clients.trades.broadcast_trade(
            wallet_id=self.wallet_id,
            address_id=self.address_id,
            trade_id=self.trade_id,
            broadcast_trade_request=broadcast_trade_request,
        )

        self._model = model
        self._update_transactions(model)

        return self

    def wait(self, interval_seconds: float = 0.2, timeout_seconds: float = 20) -> "Trade":
        """Wait for the trade to complete.

        Args:
            interval_seconds (float): The interval seconds.
            timeout_seconds (float): The timeout seconds.

        Returns:
            Trade: The trade.

        """
        start_time = time.time()

        while not self.transaction.terminal_state:
            self.reload()

            if time.time() - start_time > timeout_seconds:
                raise TimeoutError("Timed out waiting for Trade to land onchain")

            time.sleep(interval_seconds)

        return self

    @property
    def trade_id(self) -> str:
        """Get the trade ID.

        Returns:
            str: The trade ID.

        """
        return self._model.trade_id

    @property
    def network_id(self) -> str:
        """Get the network ID.

        Returns:
            str: The network ID.

        """
        return self._model.network_id

    @property
    def wallet_id(self) -> str:
        """Get the wallet ID.

        Returns:
            str: The wallet ID.

        """
        return self._model.wallet_id

    @property
    def address_id(self) -> str:
        """Get the address ID.

        Returns:
            str: The address ID.

        """
        return self._model.address_id

    @property
    def from_asset_id(self) -> str:
        """Get the from asset ID.

        Returns:
            str: The from asset ID.

        """
        return self._model.from_asset.asset_id

    @property
    def to_asset_id(self) -> str:
        """Get the to asset ID.

        Returns:
            str: The to asset ID.

        """
        return self._model.to_asset.asset_id

    @property
    def from_amount(self) -> Decimal:
        """Get the from amount.

        Returns:
            Decimal: The from amount.

        """
        return Decimal(self._model.from_amount) / Decimal(10) ** self._model.from_asset.decimals

    @property
    def to_amount(self) -> Decimal:
        """Get the to amount.

        Returns:
            Decimal: The to amount.

        """
        return Decimal(self._model.to_amount) / Decimal(10) ** self._model.to_asset.decimals

    @property
    def status(self) -> str:
        """Get the status.

        Returns:
            str: The status.

        """
        return self.transaction.status

    @property
    def transaction(self) -> Transaction:
        """Get the trade transaction."""
        if self._transaction is None:
            self._transaction = Transaction(self._model.transaction)
        return self._transaction

    @property
    def approve_transaction(self) -> Transaction | None:
        """Get the approve transaction."""
        if self._approve_transaction is None and self._model.approve_transaction is not None:
            self._approve_transaction = Transaction(self._model.approve_transaction)
        return self._approve_transaction

    def reload(self) -> None:
        """Reload the trade."""
        model = Cdp.api_clients.trades.get_trade(
            wallet_id=self.wallet_id, address_id=self.address_id, trade_id=self.trade_id
        )
        self._model = model
        self._update_transactions(model)

    def _update_transactions(self, model: TradeModel) -> None:
        """Update the transactions with the new model."""
        if model.transaction is not None:
            self._transaction = Transaction(model.transaction)

        if model.approve_transaction is not None:
            self._approve_transaction = Transaction(model.approve_transaction)

    def __str__(self):
        """Return a string representation of the Trade."""
        return f"Trade: (trade_id: {self.trade_id}, address_id: {self.address_id}, wallet_id: {self.wallet_id}, network_id: {self.network_id})"

    def __repr__(self) -> str:
        """Return a string representation of the Trade."""
        return str(self)
