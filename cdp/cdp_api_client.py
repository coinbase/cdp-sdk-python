import random
import time
from urllib.parse import urlparse

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from cdp.client import rest
from cdp.client.api_client import ApiClient
from cdp.client.api_response import ApiResponse
from cdp.client.api_response import T as ApiResponseT
from cdp.client.configuration import Configuration
from cdp.client.exceptions import ApiException
from cdp.errors import APIError, InvalidAPIKeyFormatError


class CdpApiClient(ApiClient):
    """CDP API Client that handles authentication and API calls for Coinbase."""

    def __init__(
        self,
        api_key: str,
        private_key: str,
        host: str = "https://api.cdp.coinbase.com/platform",
    ):
        """Initialize the CDP API Client.

        Args:
            api_key (str): The API key for authentication.
            private_key (str): The private key for authentication.
            host (str, optional): The base URL for the API. Defaults to "https://api.cdp.coinbase.com/platform".

        """
        configuration = Configuration(host=host)
        super().__init__(configuration)
        self.api_key = api_key
        self.private_key = private_key

    def call_api(
        self,
        method,
        url,
        header_params=None,
        body=None,
        post_params=None,
        _request_timeout=None,
    ) -> rest.RESTResponse:
        """Makes the HTTP request (synchronous)
        :param method: Method to call.
        :param url: Path to method endpoint.
        :param header_params: Header parameters to be
            placed in the request header.
        :param body: Request body.
        :param post_params dict: Request post form parameters,
            for `application/x-www-form-urlencoded`, `multipart/form-data`.
        :param _request_timeout: timeout setting for this request.
        :return: RESTResponse
        """
        if header_params is None:
            header_params = {}

        self._apply_headers(url, method, header_params)

        return super().call_api(method, url, header_params, body, post_params, _request_timeout)

    def response_deserialize(
        self,
        response_data: rest.RESTResponse,
        response_types_map: dict[str, ApiResponseT] | None = None,
    ) -> ApiResponse[ApiResponseT]:
        try:
            return super().response_deserialize(response_data, response_types_map)
        except ApiException as e:
            raise APIError.from_error(e)

    def _apply_headers(self, url: str, method: str, header_params: dict[str, str]) -> None:
        """Apply authentication to the configuration.

        Args:
            url (str): The URL to authenticate.
            method (str): The HTTP method to use.

        Returns:
            None

        """
        token = self._build_jwt(url, method)

        # Add the JWT token to the headers
        header_params["Authorization"] = f"Bearer {token}"

        # Add additional custom headers
        header_params["Content-Type"] = "application/json"
        header_params["Correlation-Context"] = self._get_correlation_data()

    def _build_jwt(self, url: str, method: str = "GET") -> str:
        """Build the JWT for the given API endpoint URL.

        Args:
            url (str): The URL to authenticate.
            method (str): The HTTP method to use.

        Returns:
            The JWT for the given API endpoint URL.

        """
        try:
            private_key = serialization.load_pem_private_key(
                self.private_key.encode(), password=None
            )
            if not isinstance(private_key, ec.EllipticCurvePrivateKey):
                raise InvalidAPIKeyFormatError("Invalid key type")
        except Exception as e:
            raise InvalidAPIKeyFormatError("Could not parse the private key") from e

        header = {
            "alg": "ES256",
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
            "exp": int(time.time()) + 60,  # +1 minute
            "uris": [uri],
        }

        try:
            return jwt.encode(claims, private_key, algorithm="ES256", headers=header)
        except Exception as e:
            print(f"Error during JWT signing: {e!s}")
            raise InvalidAPIKeyFormatError("Could not sign the JWT") from e

    @staticmethod
    def _nonce() -> str:
        """Generate a random nonce for the JWT.

        Returns:
            The nonce.

        """
        return "".join(random.choices("0123456789", k=16))

    @staticmethod
    def _get_correlation_data() -> str:
        """Return encoded correlation data including the SDK version and language.

        Returns:
            The correlation data.

        """
        data = {
            "sdk_version": "0.0.1",  # TODO: get version from package
            "sdk_language": "python",
        }
        return ",".join(f"{key}={value}" for key, value in data.items())
