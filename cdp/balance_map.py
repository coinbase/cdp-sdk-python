import json
from decimal import Decimal

from cdp.balance import Balance
from cdp.client.models.balance import Balance as BalanceModel


class BalanceMap(dict[str, Decimal]):
    """A class representing asset balances.

    This class extends the built-in dict class, where keys are asset IDs (str)
    and values are balance amounts (Decimal).
    """

    @classmethod
    def from_models(cls, models: list[BalanceModel]) -> "BalanceMap":
        """Create a BalanceMap instance from a list of BalanceModel objects.

        Args:
            models (List[BalanceModel]): A list of BalanceModel objects.

        Returns:
            BalanceMap: A new BalanceMap instance populated with the given models.

        """
        balance_map = cls()

        for model in models:
            balance = Balance.from_model(model)
            balance_map.add(balance)

        return balance_map

    def add(self, balance: Balance) -> None:
        """Add a Balance object to the BalanceMap.

        Args:
            balance (Balance): The Balance object to add.

        Raises:
            ValueError: If the provided balance is not a Balance instance.

        """
        if not isinstance(balance, Balance):
            raise ValueError("balance must be a Balance instance")

        self[balance.asset_id] = balance.amount

    def __str__(self) -> str:
        """Return a JSON string representation of the BalanceMap.

        Returns:
            str: A JSON string with asset IDs as keys and formatted balance amounts as values.

        """
        result: dict[str, str] = {}

        for asset_id, amount in self.items():
            amount_str = format(amount, "f")

            if amount == amount.to_integral():
                amount_str = str(int(amount))

            result[asset_id] = amount_str

        return json.dumps(result, separators=(",", ":"))

    def __repr__(self) -> str:
        """Return a string representation of the BalanceMap.

        Returns:
            str: The string representation of the BalanceMap.

        """
        return str(self)
