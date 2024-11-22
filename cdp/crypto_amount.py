from decimal import Decimal

from cdp.asset import Asset
from cdp.client.models.crypto_amount import CryptoAmount as CryptoAmountModel


class CryptoAmount:
    """A representation of a CryptoAmount that includes the amount and asset."""

    def __init__(self, amount: Decimal, asset: Asset, asset_id: str | None = None) -> None:
        """Initialize a new CryptoAmount. Do not use this directly, use the from_model or from_model_and_asset_id methods instead.

        Args:
            amount (Decimal): The amount of the Asset
            asset (Asset): The Asset
            asset_id (Optional[str]): The Asset ID

        """
        self._amount = amount
        self._asset = asset
        self._asset_id = asset_id or asset.asset_id

    @classmethod
    def from_model(cls, crypto_amount_model: CryptoAmountModel) -> "CryptoAmount":
        """Convert a CryptoAmount model to a CryptoAmount.

        Args:
            crypto_amount_model (CryptoAmountModel): The crypto amount from the API.

        Returns:
            CryptoAmount: The converted CryptoAmount object.

        """
        asset = Asset.from_model(crypto_amount_model.asset)
        return cls(amount=asset.from_atomic_amount(crypto_amount_model.amount), asset=asset)

    @classmethod
    def from_model_and_asset_id(
        cls, crypto_amount_model: CryptoAmountModel, asset_id: str
    ) -> "CryptoAmount":
        """Convert a CryptoAmount model and asset ID to a CryptoAmount.

        This can be used to specify a non-primary denomination that we want the amount
        to be converted to.

        Args:
            crypto_amount_model (CryptoAmountModel): The crypto amount from the API.
            asset_id (str): The Asset ID of the denomination we want returned.

        Returns:
            CryptoAmount: The converted CryptoAmount object.

        """
        asset = Asset.from_model(crypto_amount_model.asset, asset_id=asset_id)
        return cls(
            amount=asset.from_atomic_amount(crypto_amount_model.amount),
            asset=asset,
            asset_id=asset_id,
        )

    @property
    def amount(self) -> Decimal:
        """Get the amount of the Asset.

        Returns:
            Decimal: The amount of the Asset.

        """
        return self._amount

    @property
    def asset(self) -> Asset:
        """Get the Asset.

        Returns:
            Asset: The Asset.

        """
        return self._asset

    @property
    def asset_id(self) -> str:
        """Get the Asset ID.

        Returns:
            str: The Asset ID.

        """
        return self._asset_id

    def to_atomic_amount(self) -> Decimal:
        """Convert the amount to atomic units.

        Returns:
            Decimal: The amount in atomic units.

        """
        return self.asset.to_atomic_amount(self.amount)

    def __str__(self) -> str:
        """Get a string representation of the CryptoAmount.

        Returns:
            str: A string representation of the CryptoAmount.

        """
        return f"CryptoAmount(amount: '{int(self.amount)}', asset_id: '{self.asset_id}')"

    def __repr__(self) -> str:
        """Get a string representation of the CryptoAmount.

        Returns:
            str: A string representation of the CryptoAmount.

        """
        return self.__str__()
