import json
from collections.abc import Iterator
from enum import Enum

from eth_account.signers.local import LocalAccount
from eth_account.typed_transactions import DynamicFeeTransaction
from web3 import Web3

from cdp.cdp import Cdp
from cdp.client.models import Transaction as TransactionModel
from cdp.client.models.address_transaction_list import AddressTransactionList


class Transaction:
    """A representation of an onchain Transaction."""

    class Status(Enum):
        """Enumeration of Transaction statuses."""

        PENDING = "pending"
        SIGNED = "signed"
        BROADCAST = "broadcast"
        COMPLETE = "complete"
        FAILED = "failed"
        UNSPECIFIED = "unspecified"

        @classmethod
        def terminal_states(cls):
            """Get the terminal states.

            Returns:
                List[str]: The terminal states.

            """
            return [cls.COMPLETE, cls.FAILED]

        def __str__(self) -> str:
            """Return a string representation of the Status."""
            return self.value

        def __repr__(self) -> str:
            """Return a string representation of the Status."""
            return str(self)

    def __init__(self, model: TransactionModel):
        """Initialize the Transaction class.

        Args:
            model (TransactionModel): The model representing the transaction.

        """
        if not isinstance(model, TransactionModel):
            raise TypeError("model must be of type TransactionModel")
        self._model = model
        self._raw: DynamicFeeTransaction | None = None
        self._signature: str | None = model.signed_payload

    @classmethod
    def list(cls, network_id: str, address_id: str) -> Iterator["Transaction"]:
        """List transactions of the address.

        Args:
            network_id (str): The ID of the network to list transaction for.
            address_id (str): The ID of the address to list transaction for.

        Returns:
            Iterator[Transaction]: An iterator of Transaction objects.

        Raises:
            Exception: If there's an error listing the transactions.

        """
        page = None
        while True:
            response: AddressTransactionList = (
                Cdp.api_clients.transaction_history.list_address_transactions(
                    network_id=network_id,
                    address_id=address_id,
                    limit=1,
                    page=page,
                )
            )

            for model in response.data:
                yield cls(model)

            if not response.has_more:
                break

            page = response.next_page

    @property
    def unsigned_payload(self) -> str:
        """Get the unsigned payload."""
        return self._model.unsigned_payload

    @property
    def signed_payload(self) -> str:
        """Get the signed payload."""
        return self._model.signed_payload

    @property
    def transaction_hash(self) -> str:
        """Get the transaction hash."""
        return self._model.transaction_hash

    @property
    def status(self) -> Status:
        """Get the status."""
        return self.Status(self._model.status)

    @property
    def from_address_id(self) -> str:
        """Get the from address ID."""
        return self._model.from_address_id

    @property
    def to_address_id(self) -> str:
        """Get the to address ID."""
        return self._model.to_address_id

    @property
    def terminal_state(self) -> bool:
        """Check if the Transaction is in a terminal state."""
        return self.status in self.Status.terminal_states()

    @property
    def block_hash(self) -> str:
        """Get the block hash of which the Transaction is recorded."""
        return self._model.block_hash

    @property
    def block_height(self) -> str:
        """Get the block height of which the Transaction is recorded."""
        return self._model.block_height

    @property
    def transaction_link(self) -> str:
        """Get the transaction link."""
        return self._model.transaction_link

    @property
    def content(self) -> str:
        """Get the content of the transaction."""
        return self._model.content

    @property
    def raw(self) -> DynamicFeeTransaction:
        """Get the underlying raw transaction."""
        if self._raw is not None:
            return self._raw

        if self.signed_payload:
            self._raw = DynamicFeeTransaction.from_bytes(bytes.fromhex(self.signed_payload))
        else:
            raw_payload = bytes.fromhex(self.unsigned_payload).decode("utf-8")
            parsed_payload = json.loads(raw_payload)

            transaction_dict = {
                "chainId": int(parsed_payload["chainId"], 16),
                "nonce": int(parsed_payload["nonce"], 16),
                "maxPriorityFeePerGas": int(parsed_payload["maxPriorityFeePerGas"], 16),
                "maxFeePerGas": int(parsed_payload["maxFeePerGas"], 16),
                "gas": int(parsed_payload["gas"], 16),
                "value": int(parsed_payload["value"], 16),
                "data": parsed_payload.get("input", ""),
                "type": "0x2",  # EIP-1559 transaction type
            }

            # Handle 'to' field separately since smart contract deployments have an empty 'to' field
            if parsed_payload["to"]:
                transaction_dict["to"] = Web3.to_bytes(hexstr=parsed_payload["to"])
            else:
                transaction_dict["to"] = b""  # Empty bytes for contract deployment
            self._raw = DynamicFeeTransaction(transaction_dict)

        return self._raw

    @property
    def signature(self) -> str:
        """Get the signature of the Transaction."""
        if not self.signed:
            raise ValueError("Transaction is not signed")

        return self._signature

    def sign(self, key: LocalAccount) -> str:
        """Sign the Transaction with the provided key.

        Args:
            key (LocalAccount): The Ethereum account to sign with.

        Returns:
            str: The hex-encoded signed payload.

        Raises:
            ValueError: If the transaction is already signed.

        """
        if self.signed:
            raise ValueError("Transaction is already signed")

        signed_transaction = key.sign_transaction(self.raw.as_dict())
        self._signature = signed_transaction.raw_transaction.hex()
        self._raw = DynamicFeeTransaction.from_bytes(signed_transaction.raw_transaction)

        return self.signature

    @property
    def signed(self) -> bool:
        """Check if the Transaction has been signed."""
        return self._signature is not None

    def __str__(self) -> str:
        """Get a string representation of the Transaction."""
        return (
            f"Transaction: (transaction_hash: {self.transaction_hash}, status: {self.status.value})"
        )

    def __repr__(self) -> str:
        """Get a string representation of the Transaction."""
        return str(self)
