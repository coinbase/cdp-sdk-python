import json
import time
from decimal import Decimal
from typing import Any

from eth_account.signers.local import LocalAccount

from cdp.cdp import Cdp
from cdp.client.models.create_smart_contract_request import CreateSmartContractRequest
from cdp.client.models.deploy_smart_contract_request import DeploySmartContractRequest
from cdp.client.models.smart_contract import SmartContract as SmartContractModel
from cdp.client.models.smart_contract_type import SmartContractType as SmartContractTypeModel
from cdp.errors import TimeoutError
from cdp.transaction import Transaction


class SmartContract:
    """A representation of a SmartContract on the blockchain."""

    class Type:
        """Enumeration of SmartContract types."""

        ERC20 = "ERC20"
        ERC721 = "ERC721"
        ERC1155 = "ERC1155"

        def __str__(self) -> str:
            """Return a string representation of the Type."""
            return self.value

        def __repr__(self) -> str:
            """Return a string representation of the Type."""
            return str(self)

    class TokenOptions:
        """Options for ERC20 token contracts."""

        def __init__(self, name: str, symbol: str, total_supply: int | Decimal | str):
            self.name = name
            self.symbol = symbol
            self.total_supply = total_supply

    class NFTOptions:
        """Options for ERC721 NFT contracts."""

        def __init__(self, name: str, symbol: str, base_uri: str):
            self.name = name
            self.symbol = symbol
            self.base_uri = base_uri

    class MultiTokenOptions:
        """Options for ERC1155 multi-token contracts."""

        def __init__(self, uri: str):
            self.uri = uri

    def __init__(self, model: SmartContractModel) -> None:
        """Initialize the SmartContract class.

        Args:
            model (SmartContractModel): The model representing the smart contract.

        Raises:
            ValueError: If the smart contract model is empty.

        """
        if not model:
            raise ValueError("SmartContract model cannot be empty")
        self._model = model
        self._transaction = None

    @property
    def smart_contract_id(self) -> str:
        """Get the smart contract ID.

        Returns:
            str: The smart contract ID.

        """
        return self._model.smart_contract_id

    @property
    def network_id(self) -> str:
        """Get the network ID of the smart contract.

        Returns:
            str: The network ID.

        """
        return self._model.network_id

    @property
    def wallet_id(self) -> str:
        """Get the wallet ID that deployed the smart contract.

        Returns:
            str: The wallet ID.

        """
        return self._model.wallet_id

    @property
    def contract_address(self) -> str:
        """Get the contract address of the smart contract.

        Returns:
            str: The contract address.

        """
        return self._model.contract_address

    @property
    def deployer_address(self) -> str:
        """Get the deployer address of the smart contract.

        Returns:
            str: The deployer address.

        """
        return self._model.deployer_address

    @property
    def type(self) -> str:
        """Get the type of the smart contract.

        Returns:
            str: The smart contract type.

        Raises:
            ValueError: If the smart contract type is unknown.

        """
        if self._model.type == SmartContractTypeModel.ERC20:
            return self.Type.ERC20
        elif self._model.type == SmartContractTypeModel.ERC721:
            return self.Type.ERC721
        elif self._model.type == SmartContractTypeModel.ERC1155:
            return self.Type.ERC1155
        else:
            raise ValueError(f"Unknown smart contract type: {self._model.type}")

    @property
    def options(self) -> TokenOptions | NFTOptions | MultiTokenOptions:
        """Get the options of the smart contract.

        Returns:
            Union[TokenOptions, NFTOptions, MultiTokenOptions]: The smart contract options.

        """
        if self.type == self.Type.ERC20:
            return self.TokenOptions(
                name=self._model.options.name,
                symbol=self._model.options.symbol,
                total_supply=self._model.options.total_supply,
            )
        elif self.type == self.Type.ERC721:
            return self.NFTOptions(
                name=self._model.options.name,
                symbol=self._model.options.symbol,
                base_uri=self._model.options.base_uri,
            )
        else:
            return self.MultiTokenOptions(uri=self._model.options.uri)

    @property
    def abi(self) -> dict[str, Any]:
        """Get the ABI of the smart contract.

        Returns:
            Dict[str, Any]: The ABI as a JSON object.

        """
        return json.loads(self._model.abi)

    @property
    def transaction(self) -> Transaction:
        """Get the transaction associated with the smart contract deployment.

        Returns:
            Transaction: The transaction.

        """
        if self._transaction is None and self._model.transaction is not None:
            self._update_transaction(self._model)
        return self._transaction

    def sign(self, key: LocalAccount) -> "SmartContract":
        """Sign the smart contract deployment with the given key.

        Args:
            key (LocalAccount): The key to sign the smart contract deployment with.

        Returns:
            SmartContract: The signed SmartContract object.

        Raises:
            ValueError: If the key is not a LocalAccount.

        """
        if not isinstance(key, LocalAccount):
            raise ValueError("key must be a LocalAccount")

        self.transaction.sign(key)
        return self

    def broadcast(self) -> "SmartContract":
        """Broadcast the smart contract deployment to the network.

        Returns:
            SmartContract: The broadcasted SmartContract object.

        Raises:
            ValueError: If the smart contract deployment is not signed.

        """
        if not self.transaction.signed:
            raise ValueError("Cannot broadcast unsigned SmartContract deployment")

        deploy_smart_contract_request = DeploySmartContractRequest(
            signed_payload=self.transaction.signature
        )

        model = Cdp.api_clients.smart_contracts.deploy_smart_contract(
            wallet_id=self.wallet_id,
            deployer_address=self.deployer_address,
            smart_contract_id=self.smart_contract_id,
            deploy_smart_contract_request=deploy_smart_contract_request,
        )
        self._model = model
        return self

    def reload(self) -> "SmartContract":
        """Reload the SmartContract model with the latest data from the server.

        Returns:
            SmartContract: The updated SmartContract object.

        """
        model = Cdp.api_clients.smart_contracts.get_smart_contract(
            wallet_id=self.wallet_id,
            deployer_address=self.deployer_address,
            smart_contract_id=self.smart_contract_id,
        )
        self._model = model
        self._transaction = None
        return self

    def wait(self, interval_seconds: float = 0.2, timeout_seconds: float = 10) -> "SmartContract":
        """Wait until the smart contract deployment is confirmed on the network or fails on chain.

        Args:
            interval_seconds (float): The interval to check the status of the smart contract deployment.
            timeout_seconds (float): The maximum time to wait for the smart contract deployment to be confirmed.

        Returns:
            SmartContract: The SmartContract object in a terminal state.

        Raises:
            TimeoutError: If the smart contract deployment times out.

        """
        start_time = time.time()
        while not self.transaction.terminal_state:
            self.reload()

            if time.time() - start_time > timeout_seconds:
                raise TimeoutError("SmartContract deployment timed out")

            time.sleep(interval_seconds)

        return self

    @classmethod
    def create(
        cls,
        wallet_id: str,
        address_id: str,
        options: TokenOptions | NFTOptions | MultiTokenOptions,
    ) -> "SmartContract":
        """Create a new SmartContract object.

        Args:
            wallet_id (str): The ID of the wallet that will deploy the smart contract.
            address_id (str): The ID of the address that will deploy the smart contract.
            type (str): The type of the smart contract.
            options (Union[TokenOptions, NFTOptions, MultiTokenOptions]): The options of the smart contract.

        """
        if isinstance(options, cls.TokenOptions):
            type = "erc20"
        elif isinstance(options, cls.NFTOptions):
            type = "erc721"
        elif isinstance(options, cls.MultiTokenOptions):
            type = "erc1155"
        else:
            raise ValueError("Invalid options type provided")
        smart_contract_request = CreateSmartContractRequest(
            type=type,
            options=options,
        )

        model = Cdp.api_clients.smart_contracts.create_smart_contract(
            wallet_id=wallet_id,
            address_id=address_id,
            smart_contract_request=smart_contract_request,
        )

        return cls(model)

    def _update_transaction(self, model: SmartContractModel) -> None:
        """Update the transaction with the new model."""
        if model.transaction is not None:
            self._transaction = Transaction(model.transaction)

    def __str__(self) -> str:
        """Return a string representation of the smart contract."""
        return (
            f"SmartContract: (smart_contract_id: {self.smart_contract_id}, network_id: {self.network_id}, "
            f"contract_address: {self.contract_address}, deployer_address: {self.deployer_address}, "
            f"type: {self.type})"
        )

    def __repr__(self) -> str:
        """Return a string representation of the smart contract."""
        return str(self)
