from decimal import Decimal

from cdp.cdp import Cdp
from cdp.client.models.asset import Asset as AssetModel

# TODO: Move to constants.py
GWEI_DECIMALS = 9


class Asset:
    """A class representing an asset."""

    def __init__(
        self, network_id: str, asset_id: str, contract_address: str, decimals: int
    ) -> None:
        """Initialize the Asset class.

        Args:
            network_id (str): The network ID.
            asset_id (str): The asset ID.
            contract_address (str): The contract address.
            decimals (int): The number of decimals.

        """
        self._network_id = network_id
        self._asset_id = asset_id
        self._contract_address = contract_address
        self._decimals = decimals

    @classmethod
    def from_model(cls, model: AssetModel, asset_id: str | None = None) -> "Asset":
        """Create an Asset instance from a model.

        Args:
            model (AssetModel): The model representing the asset.
            asset_id (Optional[str]): The asset ID.

        Returns:
            Asset: The Asset instance.

        """
        decimals = model.decimals

        if asset_id and asset_id != model.asset_id:
            match asset_id:
                case "gwei":
                    decimals = GWEI_DECIMALS
                case "wei":
                    decimals = 0
                case _:
                    raise ValueError(f"Unsupported asset ID: {asset_id}")

        return cls(
            network_id=model.network_id,
            asset_id=model.asset_id,
            contract_address=model.contract_address,
            decimals=decimals,
        )

    @classmethod
    def fetch(cls, network_id: str, asset_id: str) -> "Asset":
        """Fetch an asset from the API.

        Args:
            network_id (str): The network ID.
            asset_id (str): The asset ID.

        Returns:
            Asset: The fetched Asset instance.

        """
        primary_denomination_asset_id = cls.primary_denomination(asset_id)

        model = Cdp.api_clients.assets.get_asset(
            network_id=network_id, asset_id=primary_denomination_asset_id
        )

        return cls.from_model(model, asset_id=asset_id)

    @staticmethod
    def primary_denomination(asset_id: str) -> str:
        """Get the primary denomination for a given asset ID.

        Args:
            asset_id (str): The asset ID.

        Returns:
            str: The primary denomination of the asset.

        """
        if asset_id in ["wei", "gwei"]:
            return "eth"
        return asset_id

    @property
    def decimals(self) -> int:
        """Get the number of decimals for the asset.

        Returns:
            int: The number of decimals.

        """
        return self._decimals

    @property
    def asset_id(self) -> str:
        """Get the asset ID.

        Returns:
            str: The asset ID.

        """
        return self._asset_id

    @property
    def contract_address(self) -> str:
        """Get the contract address.

        Returns:
            str: The contract address.

        """
        return self._contract_address

    @property
    def network_id(self) -> str:
        """Get the network ID.

        Returns:
            str: The network ID.

        """
        return self._network_id

    def from_atomic_amount(self, atomic_amount: Decimal) -> Decimal:
        """Convert an atomic amount to a whole amount.

        Args:
            atomic_amount (Decimal): The atomic amount.

        Returns:
            Decimal: The whole amount.

        """
        return Decimal(atomic_amount) / Decimal(10) ** (self.decimals)

    def to_atomic_amount(self, whole_amount: Decimal) -> Decimal:
        """Convert a whole amount to an atomic amount.

        Args:
            whole_amount (Decimal): The whole amount.

        Returns:
            Decimal: The atomic amount.

        """
        return whole_amount * Decimal(10) ** (self.decimals)

    def __str__(self) -> str:
        """Return a string representation of the Asset."""
        return f"Asset: (asset_id: {self.asset_id}, network_id: {self.network_id}, contract_address: {self.contract_address}, decimals: {self.decimals})"

    def __repr__(self) -> str:
        """Return a string representation of the Asset."""
        return str(self)
