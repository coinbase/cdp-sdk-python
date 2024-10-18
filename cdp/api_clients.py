from cdp.cdp_api_client import CdpApiClient
from cdp.client.api.addresses_api import AddressesApi
from cdp.client.api.assets_api import AssetsApi
from cdp.client.api.balance_history_api import BalanceHistoryApi
from cdp.client.api.contract_invocations_api import ContractInvocationsApi
from cdp.client.api.external_addresses_api import ExternalAddressesApi
from cdp.client.api.networks_api import NetworksApi
from cdp.client.api.smart_contracts_api import SmartContractsApi
from cdp.client.api.trades_api import TradesApi
from cdp.client.api.transaction_history_api import TransactionHistoryApi
from cdp.client.api.transfers_api import TransfersApi
from cdp.client.api.wallets_api import WalletsApi
from cdp.client.api.webhooks_api import WebhooksApi


class ApiClients:
    """A container class for all API clients used in the Coinbase SDK.

    This class provides lazy-loaded access to various API clients, ensuring
    that each client is only instantiated when it's first accessed.

    Attributes:
        _cdp_client (CdpApiClient): The CDP API client used to initialize individual API clients.
        _wallets (Optional[WalletsApi]): The WalletsApi client instance.
        _webhooks (Optional[WebhooksApi]): The WebhooksApi client instance.
        _addresses (Optional[AddressesApi]): The AddressesApi client instance.
        _external_addresses (Optional[ExternalAddressesApi]): The ExternalAddressesApi client instance.
        _transfers (Optional[TransfersApi]): The TransfersApi client instance.
        _networks (Optional[NetworksApi]): The NetworksApi client instance.
        _assets (Optional[AssetsApi]): The AssetsApi client instance.
        _trades (Optional[TradesApi]): The TradesApi client instance.
        _contract_invocations (Optional[ContractInvocationsApi]): The ContractInvocationsApi client instance.

    """

    def __init__(self, cdp_client: CdpApiClient) -> None:
        """Initialize the ApiClients instance.

        Args:
            cdp_client (CdpApiClient): The CDP API client to use for initializing individual API clients.

        """
        self._cdp_client: CdpApiClient = cdp_client
        self._wallets: WalletsApi | None = None
        self._webhooks: WebhooksApi | None = None
        self._addresses: AddressesApi | None = None
        self._external_addresses: ExternalAddressesApi | None = None
        self._transfers: TransfersApi | None = None
        self._networks: NetworksApi | None = None
        self._assets: AssetsApi | None = None
        self._trades: TradesApi | None = None
        self._contract_invocations: ContractInvocationsApi | None = None
        self._smart_contracts: SmartContractsApi | None = None
        self._balance_history: BalanceHistoryApi | None = None
        self._transaction_history: TransactionHistoryApi | None = None

    @property
    def wallets(self) -> WalletsApi:
        """Get the WalletsApi client instance.

        Returns:
            WalletsApi: The WalletsApi client instance.

        Note:
            This property lazily initializes the WalletsApi client on first access.

        """
        if self._wallets is None:
            self._wallets = WalletsApi(api_client=self._cdp_client)
        return self._wallets

    @property
    def webhooks(self) -> WebhooksApi:
        """Get the WebhooksApi client instance.

        Returns:
            WebhooksApi: The WebhooksApi client instance.

        Note:
            This property lazily initializes the WebhooksApi client on first access.

        """
        if self._webhooks is None:
            self._webhooks = WebhooksApi(api_client=self._cdp_client)
        return self._webhooks

    @property
    def addresses(self) -> AddressesApi:
        """Get the AddressesApi client instance.

        Returns:
            AddressesApi: The AddressesApi client instance.

        Note:
            This property lazily initializes the AddressesApi client on first access.

        """
        if self._addresses is None:
            self._addresses = AddressesApi(api_client=self._cdp_client)
        return self._addresses

    @property
    def external_addresses(self) -> ExternalAddressesApi:
        """Get the ExternalAddressesApi client instance.

        Returns:
            ExternalAddressesApi: The ExternalAddressesApi client instance.

        Note:
            This property lazily initializes the ExternalAddressesApi client on first access.

        """
        if self._external_addresses is None:
            self._external_addresses = ExternalAddressesApi(api_client=self._cdp_client)
        return self._external_addresses

    @property
    def transfers(self) -> TransfersApi:
        """Get the TransfersApi client instance.

        Returns:
            TransfersApi: The TransfersApi client instance.

        Note:
            This property lazily initializes the TransfersApi client on first access.

        """
        if self._transfers is None:
            self._transfers = TransfersApi(api_client=self._cdp_client)
        return self._transfers

    @property
    def networks(self) -> NetworksApi:
        """Get the NetworksApi client instance.

        Returns:
            NetworksApi: The NetworksApi client instance.

        Note:
            This property lazily initializes the NetworksApi client on first access.

        """
        if self._networks is None:
            self._networks = NetworksApi(api_client=self._cdp_client)
        return self._networks

    @property
    def assets(self) -> AssetsApi:
        """Get the AssetsApi client instance.

        Returns:
            AssetsApi: The AssetsApi client instance.

        Note:
            This property lazily initializes the AssetsApi client on first access.

        """
        if self._assets is None:
            self._assets = AssetsApi(api_client=self._cdp_client)
        return self._assets

    @property
    def trades(self) -> TradesApi:
        """Get the TradesApi client instance.

        Returns:
            TradesApi: The TradesApi client instance.

        Note:
            This property lazily initializes the TradesApi client on first access.

        """
        if self._trades is None:
            self._trades = TradesApi(api_client=self._cdp_client)
        return self._trades

    @property
    def contract_invocations(self) -> ContractInvocationsApi:
        """Get the ContractInvocationsApi client instance.

        Returns:
            ContractInvocationsApi: The ContractInvocationsApi client instance.

        Note:
            This property lazily initializes the ContractInvocationsApi client on first access.

        """
        if self._contract_invocations is None:
            self._contract_invocations = ContractInvocationsApi(api_client=self._cdp_client)
        return self._contract_invocations

    @property
    def balance_history(self) -> BalanceHistoryApi:
        """Get the BalanceHistoryApi client instance.

        Returns:
            BalanceHistoryApi: The BalanceHistoryApi client instance.

        Note:
            This property lazily initializes the BalanceHistoryApi client on first access.

        """
        if self._balance_history is None:
            self._balance_history = BalanceHistoryApi(api_client=self._cdp_client)
        return self._balance_history

    @property
    def smart_contracts(self) -> SmartContractsApi:
        """Get the SmartContractsApi client instance.

        Returns:
            SmartContractsApi: The SmartContractsApi client instance.

        Note:
            This property lazily initializes the SmartContractsApi client on first access.

        """
        if self._smart_contracts is None:
            self._smart_contracts = SmartContractsApi(api_client=self._cdp_client)
        return self._smart_contracts

    @property
    def transaction_history(self) -> TransactionHistoryApi:
        """Get the TransactionHistoryApi client instance.

        Returns:
            TransactionHistoryApi: The TransactionHistoryApi client instance.

        Note:
            This property lazily initializes the TransactionHistoryApi client on first access.

        """
        if self._transaction_history is None:
            self._transaction_history = TransactionHistoryApi(api_client=self._cdp_client)
        return self._transaction_history
