from decimal import Decimal
from cdp.cdp import Cdp
from cdp.faucet_transaction import FaucetTransaction
from cdp.asset import Asset
from cdp.balance import Balance


class Address:
    """
    A class representing an address.
    """

    def __init__(self, network_id: str, address_id: str) -> None:
        """
        Initialize the Address class.

        Args:
            network_id (str): The network ID.
            address_id (str): The address ID.
        """
        self._network_id = network_id
        self._id = address_id

    @property
    def address_id(self) -> str:
        """
        Get the address ID.

        Returns:
            str: The address ID.
        """
        return self._id

    @property
    def network_id(self) -> str:
        """
        Get the network ID.

        Returns:
            str: The network ID.
        """
        return self._network_id

    @property
    def can_sign(self) -> bool:
        """
        Get whether the address can sign.

        Returns:
            bool: Whether the address can sign.
        """
        return False

    def faucet(self, asset_id=None):
        """
        Request faucet funds.

        Args:
            asset_id (str): The asset ID.

        Returns:
            FaucetTransaction: The faucet transaction object.
        """
        model = Cdp.api_clients.external_addresses.request_external_faucet_funds(
            network_id=self.network_id, address_id=self.address_id, asset_id=asset_id
        )

        return FaucetTransaction(model)

    def balance(self, asset_id):
        """
        Get the balance of the address.

        Args:
            asset_id (str): The asset ID.

        Returns:
            Decimal: The balance of the address.
        """
        model = Cdp.api_clients.external_addresses.get_external_address_balance(
            network_id=self.network_id,
            address_id=self.address_id,
            asset_id=Asset.primary_denomination(asset_id),
        )

        return Decimal(0) if model is None else Balance.from_model(model, asset_id).amount

    def __str__(self) -> str:
        """Return a string representation of the Address."""
        return f"Address: (address_id: {self.address_id}, network_id: {self.network_id})"

    def __repr__(self) -> str:
        """Return a string representation of the Address."""
        return str(self)
