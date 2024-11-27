from decimal import Decimal

from cdp.client.models.fiat_amount import FiatAmount as FiatAmountModel


class FiatAmount:
    """A representation of a FiatAmount that includes the amount and currency."""

    def __init__(self, amount: Decimal, currency: str) -> None:
        """Initialize a new FiatAmount. Do not use this directly, use the from_model method instead.

        Args:
            amount (Decimal): The amount in the fiat currency
            currency (str): The currency code (e.g. 'USD')

        """
        self._amount = amount
        self._currency = currency

    @classmethod
    def from_model(cls, fiat_amount_model: FiatAmountModel) -> "FiatAmount":
        """Convert a FiatAmount model to a FiatAmount.

        Args:
            fiat_amount_model (FiatAmountModel): The fiat amount from the API.

        Returns:
            FiatAmount: The converted FiatAmount object.

        """
        return cls(amount=Decimal(fiat_amount_model.amount), currency=fiat_amount_model.currency)

    @property
    def amount(self) -> Decimal:
        """Get the amount in the fiat currency.

        Returns:
            Decimal: The amount in the fiat currency.

        """
        return self._amount

    @property
    def currency(self) -> str:
        """Get the currency code.

        Returns:
            str: The currency code.

        """
        return self._currency

    def __str__(self) -> str:
        """Get a string representation of the FiatAmount.

        Returns:
            str: A string representation of the FiatAmount.

        """
        return f"FiatAmount(amount: '{int(self.amount)}', currency: '{self.currency}')"

    def __repr__(self) -> str:
        """Get a string representation of the FiatAmount.

        Returns:
            str: A string representation of the FiatAmount.

        """
        return self.__str__()
