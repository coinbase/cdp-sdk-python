import json
import time
from typing import Any
from enum import Enum

from eth_account.signers.local import LocalAccount

from cdp.cdp import Cdp
from cdp.client.models.create_smart_contract_request import CreateSmartContractRequest
from cdp.client.models.deploy_smart_contract_request import DeploySmartContractRequest
from cdp.client.models.smart_contract import SmartContract as SmartContractModel
from cdp.transaction import Transaction


class SmartContract:
    """A representation of a SmartContract on the blockchain."""

    class Type(Enum):
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
    def type(self) -> Type:
        """Get the type of the smart contract.

        Returns:
            Type: The smart contract type.

        Raises:
            ValueError: If the smart contract type is unknown.

        """
        try:
            return self.Type(self._model.type)
        except ValueError:
            raise ValueError(f"Unknown smart contract type: {self._model.type}")

    @property
    def options(self) -> dict[str, Any]:
        """Get the options of the smart contract.

        Returns:
            dict[str, Any]: The smart contract options.

        """
        return self._model.options.__dict__

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
        self._update_transaction(model)
        return self

    def wait(self, interval_seconds: float = 0.2, timeout_seconds: float = 10) -> "SmartContract":
        """Wait until the smart contract deployment is confirmed on the network or fails onchain.

        Args:
            interval_seconds (float): The interval to check the status of the smart contract deployment.
            timeout_seconds (float): The maximum time to wait for the smart contract deployment to be confirmed.

        Returns:
            SmartContract: The SmartContract object in a terminal state.

        Raises:
            TimeoutError: If the smart contract deployment times out.

        """
        start_time = time.time()
        while self.transaction is not None and not self.transaction.terminal_state:
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
        type: Type,
        options: dict[str, Any],
    ) -> "SmartContract":
        """Create a new SmartContract object.

        Args:
            wallet_id (str): The ID of the wallet that will deploy the smart contract.
            address_id (str): The ID of the address that will deploy the smart contract.
            type (Type): The type of the smart contract (ERC20, ERC721, or ERC1155).
            options (dict[str, Any]): The options of the smart contract.

        """
        smart_contract_request = CreateSmartContractRequest(
            type=type.value,
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
