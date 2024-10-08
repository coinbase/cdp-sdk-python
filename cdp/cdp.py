import json
import os

from cdp.api_clients import ApiClients
from cdp.cdp_api_client import CdpApiClient
from cdp.errors import InvalidConfigurationError


class Cdp:
    """The Cdp class is a singleton responsible for configuring and managing the Coinbase API client.

    Attributes:
        api_key_name (Optional[str]): The API key name.
        private_key (Optional[str]): The private key associated with the API key.
        use_server_signer (bool): Whether to use the server signer.
        debugging (bool): Whether debugging is enabled.
        base_path (str): The base URL for the Platform API.
        max_network_retries (int): The maximum number of network retries.
        api_clients (Optional[ApiClients]): The Platform API clients instance.

    """

    _instance = None

    api_key_name = None
    private_key = None
    use_server_signer = False
    debugging = False
    base_path = "https://api.cdp.coinbase.com/platform"
    max_network_retries = 3
    api_clients: ApiClients | None = None

    def __new__(cls):
        """Create or return the singleton instance of the Cdp class.

        This method overrides the default `__new__` behavior to implement the Singleton pattern.
        It ensures that only one instance of the Cdp class exists throughout the application's lifecycle.
        If an instance already exists, it returns the existing instance; otherwise, it creates a new one.

        Returns:
            Cdp: The singleton instance of the Cdp class.

        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def configure(
        cls,
        api_key_name: str,
        private_key: str,
        use_server_signer: bool = False,
        debugging: bool = False,
        base_path: str = "https://api.cdp.coinbase.com/platform",
        max_network_retries: int = 3,
    ) -> None:
        """Configure the CDP SDK.

        Args:
            api_key_name (str): The API key name.
            private_key (str): The private key associated with the API key.
            use_server_signer (bool): Whether to use the server signer. Defaults to False.
            debugging (bool): Whether debugging is enabled. Defaults to False.
            base_path (str): The base URL for the CDP API. Defaults to "https://api.cdp.coinbase.com/platform".
            max_network_retries (int): The maximum number of network retries. Defaults to 3.

        """
        cls.api_key_name = api_key_name
        cls.private_key = private_key
        cls.use_server_signer = use_server_signer
        cls.debugging = debugging
        cls.base_path = base_path
        cls.max_network_retries = max_network_retries

        cdp_client = CdpApiClient(
            api_key_name, private_key, base_path, debugging, max_network_retries
        )
        cls.api_clients = ApiClients(cdp_client)

    @classmethod
    def configure_from_json(
        cls,
        file_path: str = "~/Downloads/cdp_api_key.json",
        use_server_signer: bool = False,
        debugging: bool = False,
        base_path: str = "https://api.cdp.coinbase.com/platform",
        max_network_retries: int = 3,
    ) -> None:
        """Configure the CDP SDK from a JSON file.

        Args:
            file_path (str): The path to the JSON file. Defaults to "~/Downloads/cdp_api_key.json".
            use_server_signer (bool): Whether to use the server signer. Defaults to False.
            debugging (bool): Whether debugging is enabled. Defaults to False.
            base_path (str): The base URL for the CDP API. Defaults to "https://api.cdp.coinbase.com/platform".
            max_network_retries (int): The maximum number of network retries. Defaults to 3.

        Raises:
            InvalidConfigurationError: If the JSON file is missing the 'api_key_name' or 'private_key'.

        """
        with open(os.path.expanduser(file_path)) as file:
            data = json.load(file)
            api_key_name = data.get("name")
            private_key = data.get("privateKey")
            if not api_key_name:
                raise InvalidConfigurationError("Invalid JSON format: Missing 'api_key_name'")
            if not private_key:
                raise InvalidConfigurationError("Invalid JSON format: Missing 'private_key'")

            cls.configure(
                api_key_name,
                private_key,
                use_server_signer,
                debugging,
                base_path,
                max_network_retries,
            )
