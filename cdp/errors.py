import json
from decimal import Decimal

from cdp.client.exceptions import ApiException


class ApiError(Exception):
    """A wrapper for API exceptions to provide more context."""

    def __init__(
        self,
        err: ApiException,
        code: str | None = None,
        message: str | None = None,
        unhandled: bool = False,
    ) -> None:
        self._http_code = err.status
        self._api_code = code
        self._api_message = message
        self._handled = bool(code and message and not unhandled)
        super().__init__(str(err))

    @classmethod
    def from_error(cls, err: ApiException) -> "ApiError":
        """Create an ApiError from an ApiException.

        Args:
            err (ApiException): The ApiException to create an ApiError from.

        Returns:
            ApiError: The API Error.

        Raises:
            ValueError: If the argument is not an ApiException.

        """
        if not isinstance(err, ApiException):
            raise ValueError("argument must be an ApiException")

        if not err.body:
            return cls(err)

        try:
            body = json.loads(err.body)
        except json.JSONDecodeError:
            return cls(err)

        message = body.get("message")
        code = body.get("code")

        if code in ERROR_CODE_TO_ERROR_CLASS:
            return ERROR_CODE_TO_ERROR_CLASS[code](err, code=code, message=message)
        else:
            return cls(err, code=code, message=message, unhandled=True)

    @property
    def http_code(self) -> int:
        """Get the HTTP status code.

        Returns:
            int: The HTTP status code.

        """
        return self._http_code

    @property
    def api_code(self) -> str | None:
        """Get the API error code.

        Returns:
            str | None: The API error code.

        """
        return self._api_code

    @property
    def api_message(self) -> str | None:
        """Get the API error message.

        Returns:
            str | None: The API error message.

        """
        return self._api_message

    @property
    def handled(self) -> bool:
        """Get whether the error is handled.

        Returns:
            bool: True if the error is handled, False otherwise.

        """
        return self._handled

    def __str__(self) -> str:
        """Get a string representation of the ApiError.

        Returns:
            str: The string representation of the ApiError.

        """
        if self.handled:
            return f"ApiError(http_code={self.http_code}, api_code={self.api_code}, api_message={self.api_message})"
        else:
            return f"ApiError(http_code={self.http_code}, api_code={self.api_code}, api_message={self.api_message}, unhandled=True)"


class InvalidConfigurationError(Exception):
    """Exception raised for errors in the configuration of the Coinbase SDK."""

    def __init__(self, message: str = "Invalid configuration provided") -> None:
        """Initialize the InvalidConfigurationError.

        Args:
            message (str): The error message.

        """
        self.message = message
        super().__init__(self.message)


class InvalidAPIKeyFormatError(Exception):
    """Exception raised for errors in the format of the API key."""

    def __init__(self, message: str = "Invalid API key format") -> None:
        """Initialize the InvalidAPIKeyFormatError.

        Args:
            message (str): The error message.

        """
        self.message = message
        super().__init__(self.message)


class InsufficientFundsError(Exception):
    """An error raised when an operation is attempted with insufficient funds."""

    def __init__(self, expected: Decimal, exact: Decimal, msg: str = "Insufficient funds") -> None:
        """Initialize the InsufficientFundsError.

        Args:
            expected (Decimal): The expected amount of funds.
            exact (Decimal): The actual amount of funds available.
            msg (str): The error message prefix.

        """
        self.message = f"{msg}: have {exact}, need {expected}."
        super().__init__(self.message)


class AlreadySignedError(Exception):
    """An error raised when a resource is already signed."""

    def __init__(self, msg: str = "Resource already signed") -> None:
        """Initialize the AlreadySignedError.

        Args:
            msg (str): The error message.

        """
        self.message = msg
        super().__init__(self.message)


class TransactionNotSignedError(Exception):
    """An error raised when a transaction is not signed."""

    def __init__(self, msg: str = "Transaction must be signed") -> None:
        """Initialize the TransactionNotSignedError.

        Args:
            msg (str): The error message.

        """
        self.message = msg
        super().__init__(self.message)


class AddressCannotSignError(Exception):
    """An error raised when an address attempts to sign a transaction without a private key."""

    def __init__(
        self, msg: str = "Address cannot sign transaction without private key loaded"
    ) -> None:
        """Initialize the AddressCannotSignError.

        Args:
            msg (str): The error message.

        """
        self.message = msg
        super().__init__(self.message)


class UnimplementedError(ApiError):
    """Exception raised for unimplemented features in the Coinbase SDK."""

    pass


class UnauthorizedError(ApiError):
    """Exception raised for unauthorized access to Coinbase API endpoints."""

    pass


class InternalError(ApiError):
    """Exception raised for internal server errors."""

    pass


class NotFoundError(ApiError):
    """Exception raised when a requested resource is not found."""

    pass


class InvalidWalletIDError(ApiError):
    """Exception raised for invalid wallet ID."""

    pass


class InvalidAddressIDError(ApiError):
    """Exception raised for invalid address ID."""

    pass


class InvalidWalletError(ApiError):
    """Exception raised for invalid wallet."""

    pass


class InvalidAddressError(ApiError):
    """Exception raised for invalid address."""

    pass


class InvalidAmountError(ApiError):
    """Exception raised for invalid amount."""

    pass


class InvalidTransferIDError(ApiError):
    """Exception raised for invalid transfer ID."""

    pass


class InvalidPageError(ApiError):
    """Exception raised for invalid page token."""

    pass


class InvalidLimitError(ApiError):
    """Exception raised for invalid page limit."""

    pass


class AlreadyExistsError(ApiError):
    """Exception raised when a resource already exists."""

    pass


class MalformedRequestError(ApiError):
    """Exception raised for malformed requests."""

    pass


class UnsupportedAssetError(ApiError):
    """Exception raised for unsupported assets."""

    pass


class InvalidAssetIDError(ApiError):
    """Exception raised for invalid asset ID."""

    pass


class InvalidDestinationError(ApiError):
    """Exception raised for invalid destination."""

    pass


class InvalidNetworkIDError(ApiError):
    """Exception raised for invalid network ID."""

    pass


class ResourceExhaustedError(ApiError):
    """Exception raised when a resource is exhausted."""

    pass


class FaucetLimitReachedError(ApiError):
    """Exception raised when the faucet limit is reached."""

    pass


class InvalidSignedPayloadError(ApiError):
    """Exception raised for invalid signed payload."""

    pass


class InvalidTransferStatusError(ApiError):
    """Exception raised for invalid transfer status."""

    pass


class NetworkFeatureUnsupportedError(ApiError):
    """Exception raised when a network feature is unsupported."""

    pass


ERROR_CODE_TO_ERROR_CLASS: dict[str, type[ApiError]] = {
    "unimplemented": UnimplementedError,
    "unauthorized": UnauthorizedError,
    "internal": InternalError,
    "not_found": NotFoundError,
    "invalid_wallet_id": InvalidWalletIDError,
    "invalid_address_id": InvalidAddressIDError,
    "invalid_wallet": InvalidWalletError,
    "invalid_address": InvalidAddressError,
    "invalid_amount": InvalidAmountError,
    "invalid_transfer_id": InvalidTransferIDError,
    "invalid_page_token": InvalidPageError,
    "invalid_page_limit": InvalidLimitError,
    "already_exists": AlreadyExistsError,
    "malformed_request": MalformedRequestError,
    "unsupported_asset": UnsupportedAssetError,
    "invalid_asset_id": InvalidAssetIDError,
    "invalid_destination": InvalidDestinationError,
    "invalid_network_id": InvalidNetworkIDError,
    "resource_exhausted": ResourceExhaustedError,
    "faucet_limit_reached": FaucetLimitReachedError,
    "invalid_signed_payload": InvalidSignedPayloadError,
    "invalid_transfer_status": InvalidTransferStatusError,
    "network_feature_unsupported": NetworkFeatureUnsupportedError,
}
