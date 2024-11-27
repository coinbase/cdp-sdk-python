from decimal import Decimal
from typing import TYPE_CHECKING

from cdp.asset import Asset
from cdp.cdp import Cdp
from cdp.crypto_amount import CryptoAmount
from cdp.fiat_amount import FiatAmount

if TYPE_CHECKING:
    from cdp.fund_operation import FundOperation

from cdp.client.models import FundQuote as FundQuoteModel


class FundQuote:
    """A representation of a Fund Operation Quote."""

    def __init__(self, model: FundQuoteModel) -> None:
        """Initialize the FundQuote class.

        Args:
            model (FundQuoteModel): The model representing the fund quote.

        """
        self._model = model
        self._network = None
        self._asset = None

    @classmethod
    def create(
        cls,
        wallet_id: str,
        address_id: str,
        amount: Decimal,
        asset_id: str,
        network_id: str,
    ) -> "FundQuote":
        """Create a new Fund Operation Quote.

        Args:
            wallet_id (str): The Wallet ID
            address_id (str): The Address ID
            amount (Decimal): The amount of the Asset
            asset_id (str): The Asset ID
            network_id (str): The Network ID

        Returns:
            FundQuote: The new FundQuote object

        """
        asset = Asset.fetch(network_id, asset_id)

        model = Cdp.api_clients.fund.create_fund_quote(
            wallet_id=wallet_id,
            address_id=address_id,
            create_fund_quote_request={
                "asset_id": Asset.primary_denomination(asset.asset_id),
                "amount": str(int(asset.to_atomic_amount(amount))),
            },
        )

        return cls(model)

    @property
    def id(self) -> str:
        """Get the Fund Quote ID.

        Returns:
            str: The Fund Quote ID.

        """
        return self._model.fund_quote_id

    @property
    def network_id(self) -> str:
        """Get the Network ID.

        Returns:
            str: The Network ID.

        """
        return self._model.network_id

    @property
    def wallet_id(self) -> str:
        """Get the Wallet ID.

        Returns:
            str: The Wallet ID.

        """
        return self._model.wallet_id

    @property
    def address_id(self) -> str:
        """Get the Address ID.

        Returns:
            str: The Address ID.

        """
        return self._model.address_id

    @property
    def asset(self) -> Asset:
        """Get the Asset.

        Returns:
            Asset: The Asset.

        """
        if self._asset is None:
            self._asset = Asset.from_model(self._model.crypto_amount.asset)
        return self._asset

    @property
    def amount(self) -> CryptoAmount:
        """Get the crypto amount.

        Returns:
            CryptoAmount: The crypto amount.

        """
        return CryptoAmount.from_model(self._model.crypto_amount)

    @property
    def fiat_amount(self) -> FiatAmount:
        """Get the fiat amount.

        Returns:
            Decimal: The fiat amount.

        """
        return FiatAmount.from_model(self._model.fiat_amount)

    @property
    def fiat_currency(self) -> str:
        """Get the fiat currency.

        Returns:
            str: The fiat currency.

        """
        return self._model.fiat_amount.currency

    @property
    def buy_fee(self) -> dict:
        """Get the buy fee.

        Returns:
            dict: The buy fee information.

        """
        return {
            "amount": self._model.fees.buy_fee.amount,
            "currency": self._model.fees.buy_fee.currency,
        }

    @property
    def transfer_fee(self) -> CryptoAmount:
        """Get the transfer fee.

        Returns:
            CryptoAmount: The transfer fee.

        """
        return CryptoAmount.from_model(self._model.fees.transfer_fee)

    def execute(self) -> "FundOperation":
        """Execute the fund quote to create a fund operation.

        Returns:
            FundOperation: The created fund operation.

        """
        from cdp.fund_operation import FundOperation

        return FundOperation.create(
            wallet_id=self.wallet_id,
            address_id=self.address_id,
            amount=self.amount.amount,
            asset_id=self.asset.asset_id,
            network_id=self.network_id,
            quote=self,
        )

    def __str__(self) -> str:
        """Get a string representation of the Fund Quote."""
        return (
            f"FundQuote(network_id: {self.network_id}, wallet_id: {self.wallet_id}, "
            f"address_id: {self.address_id}, crypto_amount: {self.amount.amount}, "
            f"crypto_asset: {self.asset.asset_id}, fiat_amount: {self.fiat_amount.amount}, "
            f"fiat_currency: {self.fiat_currency}, buy_fee: {{'amount': '{self.buy_fee['amount']}'}}, "
            f"transfer_fee: {{'amount': '{self.transfer_fee.amount}'}})"
        )

    def __repr__(self) -> str:
        """Get a string representation of the Fund Quote."""
        return self.__str__()
