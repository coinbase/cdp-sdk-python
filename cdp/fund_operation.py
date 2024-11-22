import time
from collections.abc import Iterator
from decimal import Decimal
from enum import Enum

from cdp.asset import Asset
from cdp.cdp import Cdp
from cdp.client.models import FundOperation as FundOperationModel
from cdp.crypto_amount import CryptoAmount
from cdp.fiat_amount import FiatAmount
from cdp.fund_quote import FundQuote


class FundOperation:
    """A representation of a Fund Operation."""

    class Status(Enum):
        """Fund Operation status constants."""

        PENDING = "pending"
        COMPLETE = "complete"
        FAILED = "failed"

        @classmethod
        def terminal_states(cls):
            """Get the terminal states.

            Returns:
                List[Status]: The terminal states.

            """
            return [cls.COMPLETE, cls.FAILED]

        def __str__(self) -> str:
            """Return a string representation of the Status."""
            return self.value

        def __repr__(self) -> str:
            """Return a string representation of the Status."""
            return str(self)

    def __init__(self, model: FundOperationModel) -> None:
        """Initialize the FundOperation class.

        Args:
            model (FundOperationModel): The model representing the fund operation.

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
        quote: FundQuote | None = None,
    ) -> "FundOperation":
        """Create a new Fund Operation.

        Args:
            wallet_id (str): The Wallet ID
            address_id (str): The Address ID
            amount (Decimal): The amount of the Asset
            asset_id (str): The Asset ID
            network_id (str): The Network ID
            quote (Optional[FundQuote]): The optional Fund Quote

        Returns:
            FundOperation: The new FundOperation object

        """
        asset = Asset.fetch(network_id, asset_id)

        create_request = {
            "amount": str(int(asset.to_atomic_amount(amount))),
            "asset_id": Asset.primary_denomination(asset.asset_id),
        }

        if quote:
            create_request["fund_quote_id"] = quote.id

        model = Cdp.api_clients.fund.create_fund_operation(
            wallet_id=wallet_id,
            address_id=address_id,
            create_fund_operation_request=create_request,
        )

        return cls(model)

    @classmethod
    def list(cls, wallet_id: str, address_id: str) -> Iterator["FundOperation"]:
        """List fund operations.

        Args:
            wallet_id (str): The wallet ID
            address_id (str): The address ID

        Returns:
            Iterator[FundOperation]: An iterator of fund operation objects

        """
        page = None
        while True:
            response = Cdp.api_clients.fund.list_fund_operations(
                wallet_id=wallet_id,
                address_id=address_id,
                limit=100,
                page=page,
            )

            for operation_model in response.data:
                yield cls(operation_model)

            if not response.has_more:
                break

            page = response.next_page

    @property
    def id(self) -> str:
        """Get the Fund Operation ID."""
        return self._model.fund_operation_id

    @property
    def network_id(self) -> str:
        """Get the Network ID."""
        return self._model.network_id

    @property
    def wallet_id(self) -> str:
        """Get the Wallet ID."""
        return self._model.wallet_id

    @property
    def address_id(self) -> str:
        """Get the Address ID."""
        return self._model.address_id

    @property
    def asset(self) -> Asset:
        """Get the Asset."""
        if self._asset is None:
            self._asset = Asset.from_model(self._model.crypto_amount.asset)
        return self._asset

    @property
    def amount(self) -> CryptoAmount:
        """Get the crypto amount."""
        return CryptoAmount.from_model(self._model.crypto_amount)

    @property
    def fiat_amount(self) -> FiatAmount:
        """Get the fiat amount."""
        return FiatAmount.from_model(self._model.fiat_amount)

    @property
    def fiat_currency(self) -> str:
        """Get the fiat currency."""
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

    @property
    def status(self) -> Status:
        """Get the status."""
        return self.Status(self._model.status)

    def reload(self) -> "FundOperation":
        """Reload the fund operation from the server.

        Returns:
            FundOperation: The updated fund operation.

        """
        self._model = Cdp.api_clients.fund.get_fund_operation(
            self.wallet_id, self.address_id, self.id
        )
        return self

    def wait(self, interval_seconds: float = 0.2, timeout_seconds: float = 20) -> "FundOperation":
        """Wait for the fund operation to complete.

        Args:
            interval_seconds (float): The interval between checks
            timeout_seconds (float): The maximum time to wait

        Returns:
            FundOperation: The completed fund operation

        Raises:
            TimeoutError: If the operation takes too long

        """
        start_time = time.time()

        while not self.terminal_state():
            self.reload()

            if time.time() - start_time > timeout_seconds:
                raise TimeoutError("Fund operation timed out")

            time.sleep(interval_seconds)

        return self

    def terminal_state(self) -> bool:
        """Check if the operation is in a terminal state."""
        return self.status in self.Status.terminal_states()

    def __str__(self) -> str:
        """Get a string representation of the Fund Operation."""
        return (
            f"FundOperation(id: {self.id}, network_id: {self.network_id}, "
            f"wallet_id: {self.wallet_id}, address_id: {self.address_id}, "
            f"amount: {self.amount}, asset_id: {self.asset.asset_id}, "
            f"status: {self.status.value})"
        )

    def __repr__(self) -> str:
        """Get a string representation of the Fund Operation."""
        return self.__str__()
