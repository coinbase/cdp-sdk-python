from collections.abc import Iterator
from decimal import Decimal

from cdp.asset import Asset
from cdp.cdp import Cdp
from cdp.client.models.address_historical_balance_list import AddressHistoricalBalanceList
from cdp.client.models.historical_balance import HistoricalBalance as HistoricalBalanceModel


class HistoricalBalance:
    """A class representing a balance."""

    def __init__(self, amount: Decimal, asset: Asset, block_height: str, block_hash: str):
        """Initialize the Balance class.

        Args:
            amount (Decimal): The amount.
            asset (Asset): The asset.
            block_height (str): the block height where the balance is in.
            block_hash (str): the block hash where the balance is in.

        """
        self._amount = amount
        self._asset = asset
        self._block_height = block_height
        self._block_hash = block_hash

    @classmethod
    def from_model(cls, model: HistoricalBalanceModel) -> "HistoricalBalance":
        """Create a Balance instance from a model.

        Args:
            model (BalanceModel): The model representing the balance.
            asset_id (Optional[str]): The asset ID.

        Returns:
            Balance: The Balance instance.

        """
        asset = Asset.from_model(model.asset)

        return cls(
            amount=asset.from_atomic_amount(model.amount),
            asset=asset,
            block_height=model.block_height,
            block_hash=model.block_hash
        )

    @classmethod
    def list(cls, network_id: str, address_id: str, asset_id: str) -> Iterator["HistoricalBalance"]:
        """List historical balances of an address of an asset.

        Args:
            network_id (str): The ID of the network to list historical balance for.
            address_id (str): The ID of the address to list historical balance for.
            asset_id(str): The asset ID to list historical balance.

        Returns:
            Iterator[Transaction]: An iterator of HistoricalBalance objects.

        Raises:
            Exception: If there's an error listing the historical_balances.

        """
        page = None
        while True:
            response: AddressHistoricalBalanceList = Cdp.api_clients.balance_history.list_address_historical_balance(
                network_id=network_id,
                address_id=address_id,
                asset_id=Asset.primary_denomination(asset_id),
                limit=100,
                page=page,
            )

            for model in response.data:
                yield cls.from_model(model)

            if not response.has_more:
                break

            page = response.next_page

    @property
    def amount(self) -> Decimal:
        """Get the amount.

        Returns:
            Decimal: The amount.

        """
        return self._amount

    @property
    def asset(self) -> Asset:
        """Get the asset.

        Returns:
            Asset: The asset.

        """
        return self._asset

    @property
    def block_height(self) -> str:
        """Get the block height.

        Returns:
            str: The block height.

        """
        return self._block_height

    @property
    def block_hash(self) -> str:
        """Get the block hash.

        Returns:
            str: The block hash.

        """
        return self._block_hash

    def __str__(self) -> str:
        """Return a string representation of the Balance."""
        return f"HistoricalBalance: (amount: {self.amount}, asset: {self.asset}, block_height: {self.block_height}, block_hash: {self.block_hash})"

    def __repr__(self) -> str:
        """Return a string representation of the Balance."""
        return str(self)
