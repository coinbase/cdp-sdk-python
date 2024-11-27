import json
import time
from collections.abc import Iterator
from decimal import Decimal
from typing import Any

from eth_account.signers.local import LocalAccount

from cdp.asset import Asset
from cdp.cdp import Cdp
from cdp.client.models.broadcast_contract_invocation_request import (
    BroadcastContractInvocationRequest,
)
from cdp.client.models.contract_invocation import ContractInvocation as ContractInvocationModel
from cdp.client.models.create_contract_invocation_request import CreateContractInvocationRequest
from cdp.errors import TransactionNotSignedError
from cdp.transaction import Transaction


class ContractInvocation:
    """A class representing a contract invocation."""

    def __init__(self, model: ContractInvocationModel) -> None:
        """Initialize the ContractInvocation class.

        Args:
            model (ContractInvocationModel): The model representing the contract invocation.

        """
        self._model = model
        self._transaction = None

    @property
    def contract_invocation_id(self) -> str:
        """Get the contract invocation ID.

        Returns:
            str: The contract invocation ID.

        """
        return self._model.contract_invocation_id

    @property
    def wallet_id(self) -> str:
        """Get the wallet ID of the contract invocation.

        Returns:
            str: The wallet ID.

        """
        return self._model.wallet_id

    @property
    def address_id(self) -> str:
        """Get the address ID of the contract invocation.

        Returns:
            str: The address ID.

        """
        return self._model.address_id

    @property
    def network_id(self) -> str:
        """Get the network ID of the contract invocation.

        Returns:
            str: The network ID.

        """
        return self._model.network_id

    @property
    def contract_address(self) -> str:
        """Get the contract address.

        Returns:
            str: The contract address.

        """
        return self._model.contract_address

    @property
    def abi(self) -> dict[str, Any]:
        """Get the ABI of the contract invocation.

        Returns:
            Dict: The ABI JSON.

        """
        return dict(json.loads(self._model.abi).items())

    @property
    def method(self) -> str:
        """Get the method being invoked in the contract.

        Returns:
            str: The method being invoked.

        """
        return self._model.method

    @property
    def args(self) -> dict[str, Any]:
        """Get the arguments passed to the contract method.

        Returns:
            Dict: The arguments passed to the contract method.

        """
        return dict(json.loads(self._model.args).items())

    @property
    def amount(self) -> Decimal:
        """Get the amount sent to the contract in atomic units.

        Returns:
            Decimal: The amount in atomic units.

        """
        return Decimal(self._model.amount)

    @property
    def transaction(self) -> Transaction | None:
        """Get the transaction associated with the contract invocation.

        Returns:
            Transaction: The transaction.

        """
        if self._transaction is None and self._model.transaction is not None:
            self._update_transaction(self._model)
        return self._transaction

    @property
    def transaction_link(self) -> str:
        """Get the link to the transaction on the blockchain explorer.

        Returns:
            str: The transaction link.

        """
        return self.transaction.transaction_link

    @property
    def transaction_hash(self) -> str:
        """Get the transaction hash of the contract invocation.

        Returns:
            str: The transaction hash.

        """
        return self.transaction.transaction_hash

    @property
    def status(self) -> str:
        """Get the status of the contract invocation.

        Returns:
            str: The status.

        """
        return self.transaction.status if self.transaction else None

    def sign(self, key: LocalAccount) -> "ContractInvocation":
        """Sign the contract invocation transaction with the given key.

        Args:
            key (LocalAccount): The key to sign the contract invocation with.

        Returns:
            ContractInvocation: The signed ContractInvocation object.

        Raises:
            ValueError: If the key is not a LocalAccount.

        """
        if not isinstance(key, LocalAccount):
            raise ValueError("key must be a LocalAccount")

        self.transaction.sign(key)
        return self

    def broadcast(self) -> "ContractInvocation":
        """Broadcast the contract invocation to the network.

        Returns:
            ContractInvocation: The broadcasted ContractInvocation object.

        Raises:
            TransactionNotSignedError: If the transaction is not signed.

        """
        if not self.transaction.signed:
            raise TransactionNotSignedError("Contract invocation is not signed")

        broadcast_contract_invocation_request = BroadcastContractInvocationRequest(
            signed_payload=self.transaction.signature
        )

        model = Cdp.api_clients.contract_invocations.broadcast_contract_invocation(
            wallet_id=self.wallet_id,
            address_id=self.address_id,
            contract_invocation_id=self.contract_invocation_id,
            broadcast_contract_invocation_request=broadcast_contract_invocation_request,
        )
        self._model = model
        return self

    def reload(self) -> "ContractInvocation":
        """Reload the Contract Invocation model with the latest version from the server.

        Returns:
            ContractInvocation: The updated ContractInvocation object.

        """
        model = Cdp.api_clients.contract_invocations.get_contract_invocation(
            wallet_id=self.wallet_id,
            address_id=self.address_id,
            contract_invocation_id=self.contract_invocation_id,
        )

        self._model = model
        self._update_transaction(model)

        return self

    def wait(
        self, interval_seconds: float = 0.2, timeout_seconds: float = 20
    ) -> "ContractInvocation":
        """Wait until the contract invocation is signed or fails by polling the server.

        Args:
            interval_seconds: The interval at which to poll the server.
            timeout_seconds: The maximum time to wait before timing out.

        Returns:
            ContractInvocation: The completed contract invocation.

        Raises:
            TimeoutError: If the invocation takes longer than the given timeout.

        """
        start_time = time.time()
        while not self.transaction.terminal_state:
            self.reload()

            if time.time() - start_time > timeout_seconds:
                raise TimeoutError("Contract Invocation timed out")

            time.sleep(interval_seconds)

        return self

    @classmethod
    def create(
        cls,
        address_id: str,
        wallet_id: str,
        network_id: str,
        contract_address: str,
        method: str,
        abi: list[dict] | None = None,
        args: dict | None = None,
        amount: Decimal | None = None,
        asset_id: str | None = None,
    ) -> "ContractInvocation":
        """Create a new ContractInvocation object.

        Args:
            address_id (str): The address ID of the signing address.
            wallet_id (str): The wallet ID associated with the signing address.
            network_id (str): The Network ID.
            contract_address (str): The contract address.
            method (str): The contract method.
            abi (Optional[list[dict]]): The contract ABI, if provided.
            args (Optional[dict]): The arguments to pass to the contract method.
            amount (Optional[Decimal]): The amount of native asset to send to a payable contract method.
            asset_id (Optional[str]): The asset ID to send to the contract.

        Returns:
            ContractInvocation: The new ContractInvocation object.

        """
        atomic_amount = None
        abi_json = None

        if asset_id and amount:
            asset = Asset.fetch(network_id, asset_id)
            atomic_amount = str(int(asset.to_atomic_amount(Decimal(amount))))

        if abi:
            abi_json = json.dumps(abi, separators=(",", ":"))

        create_contract_invocation_request = CreateContractInvocationRequest(
            contract_address=contract_address,
            abi=abi_json,
            method=method,
            args=json.dumps(args or {}, separators=(",", ":")),
            amount=atomic_amount,
        )

        model = Cdp.api_clients.contract_invocations.create_contract_invocation(
            wallet_id=wallet_id,
            address_id=address_id,
            create_contract_invocation_request=create_contract_invocation_request,
        )

        return cls(model)

    @classmethod
    def list(cls, wallet_id: str, address_id: str) -> Iterator["ContractInvocation"]:
        """List Contract Invocations.

        Args:
            wallet_id (str): The wallet ID.
            address_id (str): The address ID.

        Returns:
            Iterator[ContractInvocation]: An iterator of ContractInvocation objects.

        """
        page = None
        while True:
            response = Cdp.api_clients.contract_invocations.list_contract_invocations(
                wallet_id=wallet_id, address_id=address_id, limit=100, page=page
            )
            for contract_invocation in response.data:
                yield cls(contract_invocation)

            if not response.has_more:
                break

            page = response.next_page

    def _update_transaction(self, model: ContractInvocationModel) -> None:
        """Update the transaction with the new model."""
        if model.transaction is not None:
            self._transaction = Transaction(model.transaction)

    def __str__(self) -> str:
        """Return a string representation of the contract invocation."""
        return (
            f"ContractInvocation: (contract_invocation_id: {self.contract_invocation_id}, wallet_id: {self.wallet_id}, address_id: {self.address_id}, "
            f"network_id: {self.network_id}, method: {self.method}, transaction_hash: {self.transaction_hash}, transaction_link: {self.transaction_link}, status: {self.status})"
        )

    def __repr__(self) -> str:
        """Return a string representation of the contract invocation."""
        return str(self)
