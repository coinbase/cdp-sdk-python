import base64
import random
import time
from urllib.parse import urlparse

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519
from urllib3.util import Retry

from cdp import __version__
from cdp.client import rest
from cdp.client.api_client import ApiClient
from cdp.client.api_response import ApiResponse
from cdp.client.api_response import T as ApiResponseT  # noqa: N811
from cdp.client.configuration import Configuration
from cdp.client.exceptions import ApiException
from cdp.constants import SDK_DEFAULT_SOURCE
from cdp.errors import ApiError, InvalidAPIKeyFormatError


class CdpApiClient(ApiClient):
    """CDP API Client that handles authentication and API calls for Coinbase."""

    def __init__(
        self,
        api_key: str,
        private_key: str,
        host: str = "https://api.cdp.coinbase.com/platform",
        debugging: bool = False,
        max_network_retries: int = 3,
        source: str = SDK_DEFAULT_SOURCE,
        source_version: str = __version__,
    ):
        """Initialize the CDP API Client.

        Args:
            api_key (str): The API key for authentication.
            private_key (str): The private key for authentication.
                For ECDSA keys, this should be a PEM-encoded string.
                For Ed25519 keys, this should be a base64-encoded string representing
                either the raw 32-byte seed or a 64-byte key (private+public), in which
                case only the first 32 bytes are used.
            host (str, optional): The base URL for the API. Defaults to "https://api.cdp.coinbase.com/platform".
            debugging (bool): Whether debugging is enabled.
            max_network_retries (int): The maximum number of network retries. Defaults to 3.
            source (str): Specifies whether the SDK is being used directly or if it's an Agentkit extension.
            source_version (str): The version of the source package.
        """
        retry_strategy = self._get_retry_strategy(max_network_retries)
        configuration = Configuration(host=host, retries=retry_strategy)
        super().__init__(configuration)
        self._api_key = api_key
        self._private_key = private_key
        self._debugging = debugging
        self._source = source
        self._source_version = source_version

    @property
    def api_key(self) -> str:
        """The API key for authentication.

        Returns:
            str: The API key.
        """
        return self._api_key

    @property
    def private_key(self) -> str:
        """The private key for authentication.

        Returns:
            str: The private key.
        """
        return self._private_key

    @property
    def debugging(self) -> bool:
        """Whether debugging is enabled.

        Returns:
            bool: Whether debugging is enabled.
        """
        return self._debugging

    def call_api(
        self,
        method,
        url,
        header_params=None,
        body=None,
        post_params=None,
        _request_timeout=None,
    ) -> rest.RESTResponse:
        """Make the HTTP request (synchronous).

        Args:
            method: Method to call.
            url: Path to method endpoint.
            header_params: Header parameters to be placed in the request header.
            body: Request body.
            post_params (dict): Request post form parameters.
            _request_timeout: Timeout setting for this request.

        Returns:
            RESTResponse
        """
        if self.debugging:
            print(f"CDP API REQUEST: {method} {url}")

        if header_params is None:
            header_params = {}

        self._apply_headers(url, method, header_params)

        return super().call_api(method, url, header_params, body, post_params, _request_timeout)

    def response_deserialize(
        self,
        response_data: rest.RESTResponse,
        response_types_map: dict[str, ApiResponseT] | None = None,
    ) -> ApiResponse[ApiResponseT]:
        """Deserialize the API response.

        Args:
            response_data: REST response data.
            response_types_map: Map of response types.

        Returns:
            ApiResponse[ApiResponseT]
        """
        if self.debugging:
            print(f"CDP API RESPONSE: Status: {response_data.status}, Data: {response_data.data}")

        try:
            return super().response_deserialize(response_data, response_types_map)
        except ApiException as e:
            raise ApiError.from_error(e) from None

    def _apply_headers(self, url: str, method: str, header_params: dict[str, str]) -> None:
        """Apply authentication headers.

        Args:
            url (str): The URL to authenticate.
            method (str): The HTTP method to use.
            header_params (dict[str, str]): The header parameters.
        """
        token = self._build_jwt(url, method)
        header_params["Authorization"] = f"Bearer {token}"
        header_params["Content-Type"] = "application/json"
        header_params["Correlation-Context"] = self._get_correlation_data()

    def _build_jwt(self, url: str, method: str = "GET") -> str:
        """Build the JWT for the given API endpoint URL.

        Args:
            url (str): The URL to authenticate.
            method (str): The HTTP method to use.

        Returns:
            str: The JWT for the given API endpoint URL.
        """
        private_key_obj = None
        key_data = self.private_key.encode()
        # Business change: Support both ECDSA and Ed25519 keys.
        try:
            # Try loading as a PEM-encoded key (typically for ECDSA keys).
            private_key_obj = serialization.load_pem_private_key(key_data, password=None)
        except Exception:
            # If PEM loading fails, assume the key is provided as base64-encoded raw bytes (Ed25519).
            try:
                decoded_key = base64.b64decode(self.private_key)
                if len(decoded_key) == 32:
                    private_key_obj = ed25519.Ed25519PrivateKey.from_private_bytes(decoded_key)
                elif len(decoded_key) == 64:
                    private_key_obj = ed25519.Ed25519PrivateKey.from_private_bytes(decoded_key[:32])
                else:
                    raise InvalidAPIKeyFormatError(
                        "Ed25519 private key must be 32 or 64 bytes after base64 decoding"
                    )
            except Exception as e2:
                raise InvalidAPIKeyFormatError("Could not parse the private key") from e2

        # Determine signing algorithm based on the key type.
        if isinstance(private_key_obj, ec.EllipticCurvePrivateKey):
            alg = "ES256"
        elif isinstance(private_key_obj, ed25519.Ed25519PrivateKey):
            alg = "EdDSA"
        else:
            raise InvalidAPIKeyFormatError("Unsupported key type")

        header = {
            "alg": alg,
            "kid": self.api_key,
            "typ": "JWT",
            "nonce": self._nonce(),
        }

        parsed_url = urlparse(url)
        uri = f"{method} {parsed_url.netloc}{parsed_url.path}"
        claims = {
            "sub": self.api_key,
            "iss": "cdp",
            "aud": ["cdp_service"],
            "nbf": int(time.time()),
            "exp": int(time.time()) + 60,  # Token valid for 1 minute
            "uris": [uri],
        }

        try:
            return jwt.encode(claims, private_key_obj, algorithm=alg, headers=header)
        except Exception as e:
            print(f"Error during JWT signing: {e!s}")
            raise InvalidAPIKeyFormatError("Could not sign the JWT") from e

    def _nonce(self) -> str:
        """Generate a random nonce.

        Returns:
            str: The nonce.
        """
        return "".join(random.choices("0123456789", k=16))

    def _get_correlation_data(self) -> str:
        """Return correlation data including SDK version, language, and source.

        Returns:
            str: The correlation data.
        """
        data = {
            "sdk_version": __version__,
            "sdk_language": "python",
            "source": self._source,
            "source_version": self._source_version,
        }
        return ",".join(f"{key}={value}" for key, value in data.items())

    def _get_retry_strategy(self, max_network_retries: int) -> Retry:
        """Return the retry strategy.

        Args:
            max_network_retries (int): The maximum number of network retries.

        Returns:
            Retry: The retry strategy.
        """
        return Retry(
            total=max_network_retries,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"],
            backoff_factor=1,
        )
