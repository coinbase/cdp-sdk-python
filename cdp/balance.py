from decimal import Decimal

from cdp.asset import Asset
from cdp.client.models.balance import Balance as BalanceModel


class Balance:
    """A class representing a balance."""

    def __init__(self, amount: Decimal, asset: Asset, asset_id: str | None = None):
        """Initialize the Balance class.

        Args:
            amount (Decimal): The amount.
            asset (Asset): The asset.
            asset_id (Optional[str]): The asset ID.

        """
        self._amount = amount
        self._asset = asset
        self._asset_id = asset_id if asset_id is not None else asset.asset_id

    @staticmethod
    def from_model(model: BalanceModel, asset_id: str | None = None) -> "Balance":
        """Create a Balance instance from a model.

        Args:
            model (BalanceModel): The model representing the balance.
            asset_id (Optional[str]): The asset ID.

        Returns:
            Balance: The Balance instance.

        """
        asset = Asset.from_model(model.asset, asset_id=asset_id)

        return Balance(
            amount=asset.from_atomic_amount(model.amount),
            asset=asset,
            asset_id=asset_id,
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
    def asset_id(self) -> str:
        """Get the asset ID.

        Returns:
            str: The asset ID.

        """
        return self._asset_id

    def __str__(self) -> str:
        """Return a string representation of the Balance."""
        return f"Balance: (amount: {self.amount}, asset: {self.asset})"

    def __repr__(self) -> str:
        """Return a string representation of the Balance."""
        return str(self)
