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
    def walletId(self) -> str | None:
        """Get the ID of the wallet (camelCase alias).

        Returns:
            str | None: The ID of the wallet.

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
            str | None: The network ID of the wallet.

        """
        return self._network_id

    @property
    def networkId(self) -> str | None:
        """Get the network ID of the wallet (camelCase alias).

        Returns:
            str | None: The network ID of the wallet.

        """
        return self._network_id

    def to_dict(self, camel_case: bool = False) -> dict[str, str]:
        """Convert the wallet data to a dictionary.

        Args:
            camel_case (bool): Whether to use camelCase keys. Defaults to False.

        Returns:
            dict[str, str]: The dictionary representation of the wallet data.

        """
        if camel_case:
            result = {"walletId": self.walletId, "seed": self.seed}
            if self._network_id is not None:
                result["networkId"] = self.networkId
            return result
        else:
            result = {"wallet_id": self.wallet_id, "seed": self.seed}
            if self._network_id is not None:
                result["network_id"] = self.network_id
            return result

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "WalletData":
        """Create a WalletData class instance from the given dictionary.

        Args:
            data (dict[str, str]): The data to create the WalletData object from.
                Must contain exactly one of ('wallet_id' or 'walletId'), and a seed.
                May optionally contain exactly one of ('network_id' or 'networkId').

        Returns:
            WalletData: The wallet data.

        Raises:
            ValueError:
            - If both 'wallet_id' and 'walletId' are present, or if neither is present.
            - If both 'network_id' and 'networkId' are present, or if neither is present.

        """
        has_snake_case_wallet = "wallet_id" in data
        has_camel_case_wallet = "walletId" in data

        if has_snake_case_wallet and has_camel_case_wallet:
            raise ValueError("Data cannot contain both 'wallet_id' and 'walletId' keys")

        wallet_id = data.get("wallet_id") if has_snake_case_wallet else data.get("walletId")
        if wallet_id is None:
            raise ValueError("Data must contain either 'wallet_id' or 'walletId'")

        seed = data.get("seed")
        if seed is None:
            raise ValueError("Data must contain 'seed'")

        has_snake_case_network = "network_id" in data
        has_camel_case_network = "networkId" in data

        if has_snake_case_network and has_camel_case_network:
            raise ValueError("Data cannot contain both 'network_id' and 'networkId' keys")

        network_id = data.get("network_id") if has_snake_case_network else data.get("networkId")

        return cls(wallet_id, seed, network_id)

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
