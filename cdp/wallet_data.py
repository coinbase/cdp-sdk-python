class WalletData:
    """A class representing wallet data required to recreate a wallet."""

    def __init__(self, wallet_id: str, seed: str, network_id: str | None = None) -> None:
        """Initialize the WalletData class.

        Args:
            wallet_id (str): The ID of the wallet.
            seed (str): The seed of the wallet.
            network_id (str | None): The network ID of the wallet. Defaults to None.

        """
        self._wallet_id = wallet_id
        self._seed = seed
        self._network_id = network_id

    @property
    def wallet_id(self) -> str:
        """Get the ID of the wallet.

        Returns:
            str: The ID of the wallet.

        """
        return self._wallet_id

    @property
    def seed(self) -> str:
        """Get the seed of the wallet.

        Returns:
            str: The seed of the wallet.

        """
        return self._seed

    @property
    def network_id(self) -> str | None:
        """Get the network ID of the wallet.

        Returns:
            str: The network ID of the wallet.

        """
        return self._network_id

    def to_dict(self) -> dict[str, str]:
        """Convert the wallet data to a dictionary.

        Returns:
            dict[str, str]: The dictionary representation of the wallet data.

        """
        result = {"wallet_id": self.wallet_id, "seed": self.seed}
        if self._network_id is not None:
            result["network_id"] = self.network_id
        return result

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "WalletData":
        """Create a WalletData class instance from the given dictionary.

        Args:
            data (dict[str, str]): The data to create the WalletData object from.

        Returns:
            WalletData: The wallet data.

        """
        return cls(
            data["wallet_id"],
            data["seed"],
            data.get("network_id")
        )

    def __str__(self) -> str:
        """Return a string representation of the WalletData object.

        Returns:
            str: A string representation of the wallet data.

        """
        return f"WalletData: (wallet_id: {self.wallet_id}, seed: {self.seed}, network_id: {self.network_id})"

    def __repr__(self) -> str:
        """Return a string representation of the WalletData object.

        Returns:
            str: A string representation of the wallet data.

        """
        return str(self)
