import json
from decimal import Decimal

import pytest

from cdp.client.exceptions import ApiException
from cdp.errors import (
    ERROR_CODE_TO_ERROR_CLASS,
    AddressCannotSignError,
    AlreadySignedError,
    ApiError,
    InsufficientFundsError,
    InvalidAPIKeyFormatError,
    InvalidConfigurationError,
    TransactionNotSignedError,
)


def test_api_error_init():
    """Test API error initialization."""
    err = ApiException(400, "Bad Request")
    api_error = ApiError(err, code="test_code", message="Test message")

    assert api_error.http_code == 400
    assert api_error.api_code == "test_code"
    assert api_error.api_message == "Test message"
    assert api_error.handled is True


def test_api_error_from_error_with_valid_json():
    """Test API error from error with valid JSON."""
    err = ApiException(400, "Bad Request")
    err.body = json.dumps({"code": "invalid_wallet_id", "message": "Invalid wallet ID"})
    api_error = ApiError.from_error(err)

    assert isinstance(api_error, ERROR_CODE_TO_ERROR_CLASS["invalid_wallet_id"])
    assert api_error.api_code == "invalid_wallet_id"
    assert api_error.api_message == "Invalid wallet ID"


def test_api_error_from_error_with_invalid_json():
    """Test API error from error with invalid JSON."""
    err = ApiException(400, "Bad Request")
    err.body = "Invalid JSON"
    api_error = ApiError.from_error(err)

    assert isinstance(api_error, ApiError)
    assert api_error.api_code is None
    assert api_error.api_message is None


def test_api_error_from_error_with_unknown_code():
    """Test API error from error with unknown code."""
    err = ApiException(400, "Bad Request")
    err.body = json.dumps({"code": "unknown_code", "message": "Unknown error"})
    api_error = ApiError.from_error(err)

    assert isinstance(api_error, ApiError)
    assert api_error.api_code == "unknown_code"
    assert api_error.api_message == "Unknown error"
    assert api_error.handled is False


def test_api_error_str_representation():
    """Test API error string representation."""
    err = ApiException(400, "Bad Request")
    api_error = ApiError(err, code="test_code", message="Test message")

    assert str(api_error) == "ApiError(http_code=400, api_code=test_code, api_message=Test message)"


def test_invalid_configuration_error():
    """Test invalid configuration error."""
    with pytest.raises(InvalidConfigurationError, match="Custom configuration error"):
        raise InvalidConfigurationError("Custom configuration error")


def test_invalid_api_key_format_error():
    """Test invalid API key format error."""
    with pytest.raises(InvalidAPIKeyFormatError, match="Invalid API key format"):
        raise InvalidAPIKeyFormatError()


def test_insufficient_funds_error():
    """Test insufficient funds error."""
    with pytest.raises(InsufficientFundsError, match="Insufficient funds: have 50, need 100"):
        raise InsufficientFundsError(Decimal(100), Decimal(50))


def test_already_signed_error():
    """Test already signed error."""
    with pytest.raises(AlreadySignedError, match="Resource already signed"):
        raise AlreadySignedError()


def test_transaction_not_signed_error():
    """Test transaction not signed error."""
    with pytest.raises(TransactionNotSignedError, match="Transaction must be signed"):
        raise TransactionNotSignedError()


def test_address_cannot_sign_error():
    """Test address cannot sign error."""
    with pytest.raises(
        AddressCannotSignError, match="Address cannot sign transaction without private key loaded"
    ):
        raise AddressCannotSignError()


@pytest.mark.parametrize(
    "error_code, expected_class",
    [
        ("unimplemented", "UnimplementedError"),
        ("unauthorized", "UnauthorizedError"),
        ("internal", "InternalError"),
        ("not_found", "NotFoundError"),
        ("invalid_wallet_id", "InvalidWalletIDError"),
        ("invalid_address_id", "InvalidAddressIDError"),
        ("invalid_wallet", "InvalidWalletError"),
        ("invalid_address", "InvalidAddressError"),
        ("invalid_amount", "InvalidAmountError"),
        ("invalid_transfer_id", "InvalidTransferIDError"),
        ("invalid_page_token", "InvalidPageError"),
        ("invalid_page_limit", "InvalidLimitError"),
        ("already_exists", "AlreadyExistsError"),
        ("malformed_request", "MalformedRequestError"),
        ("unsupported_asset", "UnsupportedAssetError"),
        ("invalid_asset_id", "InvalidAssetIDError"),
        ("invalid_destination", "InvalidDestinationError"),
        ("invalid_network_id", "InvalidNetworkIDError"),
        ("resource_exhausted", "ResourceExhaustedError"),
        ("faucet_limit_reached", "FaucetLimitReachedError"),
        ("invalid_signed_payload", "InvalidSignedPayloadError"),
        ("invalid_transfer_status", "InvalidTransferStatusError"),
        ("network_feature_unsupported", "NetworkFeatureUnsupportedError"),
    ],
)
def test_error_code_mapping(error_code, expected_class):
    """Test error code mapping."""
    assert ERROR_CODE_TO_ERROR_CLASS[error_code].__name__ == expected_class
