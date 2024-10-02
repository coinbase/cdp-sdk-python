from decimal import Decimal

from cdp.asset import Asset
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

    @staticmethod
    def from_model(model: HistoricalBalanceModel) -> "HistoricalBalance":
        """Create a Balance instance from a model.

        Args:
            model (BalanceModel): The model representing the balance.
            asset_id (Optional[str]): The asset ID.

        Returns:
            Balance: The Balance instance.

        """
        asset = Asset.from_model(model.asset)

        return HistoricalBalance(
            amount=asset.from_atomic_amount(model.amount),
            asset=asset,
            block_height=model.block_height,
            block_hash=model.block_hash
        )

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
