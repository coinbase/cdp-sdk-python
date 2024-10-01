from collections.abc import Iterator
from decimal import Decimal
from numbers import Number
from typing import TYPE_CHECKING, Union

from eth_account.signers.local import LocalAccount
from eth_utils import to_bytes, to_hex

from cdp.address import Address
from cdp.cdp import Cdp
from cdp.client.models.address import Address as AddressModel
from cdp.contract_invocation import ContractInvocation
from cdp.errors import InsufficientFundsError
from cdp.payload_signature import PayloadSignature
from cdp.smart_contract import SmartContract
from cdp.trade import Trade
from cdp.transfer import Transfer

if TYPE_CHECKING:
    from cdp.wallet import Wallet


class WalletAddress(Address):
    """A class representing a wallet address."""

    def __init__(self, model: AddressModel, key: LocalAccount | None = None) -> None:
        """Initialize the WalletAddress.

        Args:
            model (AddressModel): The address model.
            key (Optional[LocalAccount]): The local account key.

        """
        self._model = model
        self._key = key

        super().__init__(model.network_id, model.address_id)

    @property
    def wallet_id(self) -> str:
        """Get the wallet ID."""
        return self._model.wallet_id

    @property
    def key(self) -> LocalAccount | None:
        """Get the local account key."""
        return self._key

    @key.setter
    def key(self, key: LocalAccount) -> None:
        """Set the private key for signing transactions.

        Args:
            key (LocalAccount): The private key.

        Raises:
            ValueError: If the private key is already set.

        """
        if self.key is not None:
            raise ValueError("Private key is already set")

        self._key = key

    @property
    def can_sign(self) -> bool:
        """Get whether the address can sign.

        Returns:
            bool: Whether the address can sign.

        """
        return self.key is not None

    def transfer(
        self,
        amount: Number | Decimal | str,
        asset_id: str,
        destination: Union[Address, "Wallet", str],
        gasless: bool = False,
    ) -> Transfer:
        """Transfer funds from the wallet address.

        Args:
            amount (Union[Number, Decimal, str]): The amount to transfer.
            asset_id (str): The asset ID.
            destination (Union[Address, 'Wallet', str]): The transfer destination.
            gasless (bool): Whether to use gasless transfer.

        Returns:
            Transfer: The created transfer object.

        """
        normalized_amount = Decimal(amount)

        self._ensure_sufficient_balance(normalized_amount, asset_id)

        transfer = Transfer.create(
            address_id=self.address_id,
            amount=normalized_amount,
            asset_id=asset_id,
            destination=destination,
            network_id=self.network_id,
            wallet_id=self.wallet_id,
            gasless=gasless,
        )

        if Cdp.use_server_signer:
            return transfer

        transfer.sign(self.key)
        transfer.broadcast()

        return transfer

    def trade(self, amount: Number | Decimal | str, from_asset_id: str, to_asset_id: str) -> Trade:
        """Trade funds from the wallet address.

        Args:
            amount (Union[Number, Decimal, str]): The amount to trade.
            from_asset_id (str): The source asset ID.
            to_asset_id (str): The destination asset ID.

        Returns:
            Trade: The created trade object.

        """
        normalized_amount = Decimal(amount)

        self._ensure_sufficient_balance(normalized_amount, from_asset_id)

        trade = Trade.create(
            address_id=self.address_id,
            from_asset_id=from_asset_id,
            to_asset_id=to_asset_id,
            amount=normalized_amount,
            network_id=self.network_id,
            wallet_id=self.wallet_id,
        )

        if Cdp.use_server_signer:
            return trade

        trade.transaction.sign(self.key)

        if trade.approve_transaction is not None:
            trade.approve_transaction.sign(self.key)

        trade.broadcast()

        return trade

    def invoke_contract(
        self,
        contract_address: str,
        method: str,
        abi: list[dict] | None = None,
        args: dict | None = None,
        amount: Number | Decimal | str | None = None,
        asset_id: str | None = None,
    ) -> ContractInvocation:
        """Invoke a method on the specified contract address, with the given ABI and arguments.

        Args:
            contract_address (str): The address of the contract to invoke.
            method (str): The name of the method to call on the contract.
            abi (Optional[list[dict]]): The ABI of the contract, if provided.
            args (Optional[dict]): The arguments to pass to the method.
            amount (Optional[Union[Number, Decimal, str]]): The amount to send with the invocation, if applicable.
            asset_id (Optional[str]): The asset ID associated with the amount, if applicable.

        Returns:
            ContractInvocation: The contract invocation object.

        """
        normalized_amount = Decimal(amount) if amount else Decimal("0")

        if amount and asset_id:
            self._ensure_sufficient_balance(amount, asset_id)

        invocation = ContractInvocation.create(
            address_id=self.address_id,
            wallet_id=self.wallet_id,
            network_id=self.network_id,
            contract_address=contract_address,
            method=method,
            abi=abi,
            args=args,
            amount=normalized_amount,
            asset_id=asset_id,
        )

        if Cdp.use_server_signer:
            return invocation

        invocation.sign(self.key)

        invocation.broadcast()

        return invocation

    def sign_payload(self, unsigned_payload: str) -> PayloadSignature:
        """Sign the given unsigned payload.

        Args:
            unsigned_payload (str): The unsigned payload.

        Returns:
            PayloadSignature: The payload signature object.

        """
        signature = None

        if not Cdp.use_server_signer:
            signed_message = self.key.unsafe_sign_hash(to_bytes(hexstr=unsigned_payload))
            signature = to_hex(signed_message.signature)

        return PayloadSignature.create(
            wallet_id=self.wallet_id,
            address_id=self.address_id,
            unsigned_payload=unsigned_payload,
            signature=signature,
        )

    def deploy_token(
        self, name: str, symbol: str, total_supply: Number | Decimal | str
    ) -> SmartContract:
        """Deploy a token smart contract.

        Args:
            name (str): The name of the token.
            symbol (str): The symbol of the token.
            total_supply (Union[Number, Decimal, str]): The total supply of the token.

        Returns:
            SmartContract: The deployed smart contract.

        """
        smart_contract = SmartContract.create(
            wallet_id=self.wallet_id,
            address_id=self.address_id,
            type=SmartContract.Type.ERC20,
            options=SmartContract.TokenContractOptions(
                name=name, symbol=symbol, total_supply=str(total_supply)
            ),
        )

        if Cdp.use_server_signer:
            return smart_contract

        smart_contract.sign(self.key)
        smart_contract.broadcast()

        return smart_contract

    def deploy_nft(self, name: str, symbol: str, base_uri: str) -> SmartContract:
        """Deploy an NFT smart contract.

        Args:
            name (str): The name of the NFT.
            symbol (str): The symbol of the NFT.
            base_uri (str): The base URI for the NFT.

        Returns:
            SmartContract: The deployed smart contract.

        """
        smart_contract = SmartContract.create(
            wallet_id=self.wallet_id,
            address_id=self.address_id,
            type=SmartContract.Type.ERC721,
            options=SmartContract.NFTContractOptions(name=name, symbol=symbol, base_uri=base_uri),
        )

        if Cdp.use_server_signer:
            return smart_contract

        smart_contract.sign(self.key)
        smart_contract.broadcast()

        return smart_contract

    def deploy_multi_token(self, uri: str) -> SmartContract:
        """Deploy a multi-token smart contract.

        Args:
            uri (str): The URI for the multi-token contract.

        Returns:
            SmartContract: The deployed smart contract.

        """
        smart_contract = SmartContract.create(
            wallet_id=self.wallet_id,
            address_id=self.address_id,
            type=SmartContract.Type.ERC1155,
            options=SmartContract.MultiTokenContractOptions(uri=uri),
        )

        if Cdp.use_server_signer:
            return smart_contract

        smart_contract.sign(self.key)
        smart_contract.broadcast()

        return smart_contract

    def transfers(self) -> Iterator[Transfer]:
        """List transfers for this wallet address.

        Returns:
            Iterator[Transfer]: Iterator of transfer objects.

        """
        return Transfer.list(wallet_id=self.wallet_id, address_id=self.address_id)

    def trades(self) -> Iterator[Trade]:
        """List trades for this wallet address.

        Returns:
            Iterator[Trade]: Iterator of trade objects.

        """
        return Trade.list(wallet_id=self.wallet_id, address_id=self.address_id)

    def _ensure_sufficient_balance(self, amount: Decimal, asset_id: str) -> None:
        """Ensure the wallet address has sufficient balance.

        Args:
            amount (Decimal): The amount to check.
            asset_id (str): The asset ID.

        Raises:
            InsufficientFundsError: If there are insufficient funds.

        """
        current_balance = self.balance(asset_id)

        if amount < current_balance:
            return

        raise InsufficientFundsError(expected=amount, exact=current_balance)

    def __str__(self) -> str:
        """Return a string representation of the WalletAddress."""
        return f"WalletAddress: (address_id: {self.address_id}, wallet_id: {self.wallet_id}, network_id: {self.network_id})"

    def __repr__(self) -> str:
        """Return a string representation of the WalletAddress."""
        return str(self)
