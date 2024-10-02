import builtins
import hashlib
import json
import os
import time
from collections.abc import Iterator
from decimal import Decimal
from numbers import Number
from typing import Any, Union

import coincurve
from bip_utils import Bip32Slip10Secp256k1
from Crypto.Cipher import AES
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from eth_account import Account

from cdp.address import Address
from cdp.balance_map import BalanceMap
from cdp.cdp import Cdp
from cdp.client.models.address import Address as AddressModel
from cdp.client.models.create_address_request import CreateAddressRequest
from cdp.client.models.create_wallet_request import (
    CreateWalletRequest,
    CreateWalletRequestWallet,
)
from cdp.client.models.wallet import Wallet as WalletModel
from cdp.client.models.wallet_list import WalletList
from cdp.contract_invocation import ContractInvocation
from cdp.faucet_transaction import FaucetTransaction
from cdp.payload_signature import PayloadSignature
from cdp.smart_contract import SmartContract
from cdp.trade import Trade
from cdp.wallet_address import WalletAddress
from cdp.wallet_data import WalletData


class Wallet:
    """A class representing a wallet."""

    MAX_ADDRESSES: int = 20
    """The maximum number of addresses that can be associated with a wallet."""

    def __init__(self, model: WalletModel, seed: str | None = None) -> None:
        """Initialize the Wallet class.

        Args:
            model (WalletModel): The WalletModel object representing the wallet.
            seed (Optional[str]): The seed for the wallet. Defaults to None.

        """
        self._model = model
        self._addresses: list[WalletAddress] | None = None
        self._seed = seed
        self._master = None if Cdp.use_server_signer else self._set_master_node()

    @property
    def id(self) -> str:
        """Get the ID of the wallet.

        Returns:
            str: The ID of the wallet.

        """
        return self._model.id

    @property
    def network_id(self) -> str:
        """Get the network ID of the wallet.

        Returns:
            str: The network ID of the wallet.

        """
        return self._model.network_id

    @property
    def server_signer_status(self) -> str:
        """Get the server signer status of the wallet.

        Returns:
            str: The server signer status of the wallet.

        """
        return self._model.server_signer_status

    @property
    def addresses(self) -> list[WalletAddress]:
        """Get the addresses of the wallet.

        Returns:
            List[WalletAddress]: The addresses of the wallet.

        """
        if self._addresses is None:
            self._set_addresses()

        return self._addresses

    @property
    def can_sign(self) -> bool:
        """Check if the wallet can sign transactions.

        Returns:
            bool: True if the wallet can sign, False otherwise.

        """
        return self._master is not None

    @classmethod
    def create(
        cls,
        network_id: str = "base-sepolia",
        interval_seconds: float = 0.2,
        timeout_seconds: float = 20,
    ) -> "Wallet":
        """Create a new wallet.

        Args:
            network_id (str): The network ID of the wallet. Defaults to "base-sepolia".
            interval_seconds (float): The interval between checks in seconds. Defaults to 0.2.
            timeout_seconds (float): The maximum time to wait for the server signer to be active. Defaults to 20.

        Returns:
            Wallet: The created wallet object.

        Raises:
            Exception: If there's an error creating the wallet.

        """
        create_wallet_request = CreateWalletRequest(
            wallet=CreateWalletRequestWallet(
                network_id=network_id, use_server_signer=Cdp.use_server_signer
            )
        )

        model = Cdp.api_clients.wallets.create_wallet(create_wallet_request)
        wallet = cls(model)

        if Cdp.use_server_signer:
            wallet._wait_for_signer(interval_seconds, timeout_seconds)

        wallet.create_address()

        return wallet

    def _wait_for_signer(self, interval_seconds: float, timeout_seconds: float) -> "Wallet":
        """Wait for the server signer to be active.

        Args:
            interval_seconds (float): The interval between checks in seconds.
            timeout_seconds (float): The maximum time to wait for the server signer to be active.

        Returns:
            Wallet: The current wallet instance.

        Raises:
            TimeoutError: If the wallet creation times out.

        """
        start_time = time.time()

        while self.server_signer_status != "active_seed":
            self.reload()

            if time.time() - start_time > timeout_seconds:
                raise TimeoutError("Wallet creation timed out. Check status of your Server-Signer")

            time.sleep(interval_seconds)

        return self

    def reload(self) -> None:
        """Reload the wallet model from the API.

        Returns:
            None

        """
        model = Cdp.api_clients.wallets.get_wallet(self.id)
        self._model = model
        return

    @classmethod
    def fetch(cls, wallet_id: str) -> "Wallet":
        """Fetch a wallet by its ID.

        Args:
            wallet_id (str): The ID of the wallet to retrieve.

        Returns:
            Wallet: The retrieved wallet object.

        Raises:
            Exception: If there's an error retrieving the wallet.

        """
        model = Cdp.api_clients.wallets.get_wallet(wallet_id)

        return cls(model, "")

    @classmethod
    def list(cls) -> Iterator["Wallet"]:
        """List wallets.

        Returns:
            Iterator[Wallet]: An iterator of wallet objects.

        Raises:
            Exception: If there's an error listing the wallets.

        """
        while True:
            page = None

            response: WalletList = Cdp.api_clients.wallets.list_wallets(limit=100, page=page)

            for wallet_model in response.data:
                yield cls(wallet_model, "")

            if not response.has_more:
                break

            page = response.next_page

    @classmethod
    def import_data(cls, data: WalletData) -> "Wallet":
        """Import a wallet from previously exported wallet data.

        Args:
            data (WalletData): The wallet data to import.

        Returns:
            Wallet: The imported wallet.

        Raises:
            Exception: If there's an error getting the wallet.

        """
        if not isinstance(data, WalletData):
            raise ValueError("Data must be a WalletData instance")

        model = Cdp.api_clients.wallets.get_wallet(data.wallet_id)

        wallet = cls(model, data.seed)

        wallet._set_addresses()

        return wallet

    def create_address(self) -> "WalletAddress":
        """Create a new address for the wallet.

        Returns:
            WalletAddress: The created address object.

        Raises:
            Exception: If there's an error creating the address.

        """
        if self._addresses is None:
            self._set_addresses()

        index = None

        create_address_request = CreateAddressRequest()
        if self.can_sign:
            index = len(self._addresses)
            derived_key = self._derive_key(index)
            public_key_hex = derived_key.PublicKey().RawCompressed().ToHex()
            attestation = self._create_attestation(derived_key, public_key_hex)

            create_address_request = CreateAddressRequest(
                public_key=public_key_hex, attestation=attestation, address_index=index
            )

        model = Cdp.api_clients.addresses.create_address(
            wallet_id=self.id, create_address_request=create_address_request
        )

        if self.default_address is None:
            self.reload()

        wallet_address = self._build_wallet_address(model, index)
        self._addresses.append(wallet_address)

        return wallet_address

    def faucet(self, asset_id: str | None = None) -> FaucetTransaction:
        """Request faucet funds.

        Args:
            asset_id (Optional[str]): The asset ID. Defaults to None.

        Returns:
            FaucetTransaction: The faucet transaction object.

        Raises:
            ValueError: If the default address does not exist.

        """
        if self.default_address is None:
            raise ValueError("Default address does not exist")

        return self.default_address.faucet(asset_id)

    def balance(self, asset_id: str) -> Decimal:
        """Get the balance of a specific asset for the default address.

        Args:
            asset_id (str): The ID of the asset to check the balance for.

        Returns:
            Any: The balance of the specified asset.

        Raises:
            ValueError: If the default address does not exist.

        """
        if self.default_address is None:
            raise ValueError("Default address does not exist")

        return self.default_address.balance(asset_id)

    def balances(self) -> BalanceMap:
        """List balances of the address.

        Returns:
           BalanceMap: The balances of the address, keyed by asset ID. Ether balances are denominated in ETH.

        Raises:
            ValueError: If the default address does not exist.

        """
        if self.default_address is None:
            raise ValueError("Default address does not exist")

        return self.default_address.balances()

    def transfer(
        self,
        amount: Number | Decimal | str,
        asset_id: str,
        destination: Union[Address, "Wallet", str],
        gasless: bool = False,
    ) -> Any:
        """Transfer funds from the wallet.

        Args:
            amount (Union[Number, Decimal, str]): The amount of funds to transfer.
            asset_id (str): The ID of the asset to transfer.
            destination (Union[Address, 'Wallet', str]): The destination for the transfer.
            gasless (bool): Whether the transfer should be gasless. Defaults to False.

        Returns:
            Any: The result of the transfer operation.

        Raises:
            ValueError: If the default address does not exist.

        """
        if self.default_address is None:
            raise ValueError("Default address does not exist")

        # Convert amount to Decimal
        if isinstance(amount, float | int | str):
            amount = Decimal(amount)

        return self.default_address.transfer(amount, asset_id, destination, gasless)

    def trade(self, amount: Number | Decimal | str, from_asset_id: str, to_asset_id: str) -> Trade:
        """Trade funds from the wallet address.

        Args:
            amount (Union[Number, Decimal, str]): The amount to trade.
            from_asset_id (str): The asset ID to trade from.
            to_asset_id (str): The asset ID to trade to.

        Returns:
            Trade: The trade object.

        Raises:
            ValueError: If the default address does not exist.

        """
        if self.default_address is None:
            raise ValueError("Default address does not exist")

        return self.default_address.trade(amount, from_asset_id, to_asset_id)

    def invoke_contract(
        self,
        contract_address: str,
        method: str,
        abi: builtins.list[dict] | None = None,
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

        Raises:
            ValueError: If the default address does not exist.

        """
        if self.default_address is None:
            raise ValueError("Default address does not exist")

        invocation = self.default_address.invoke_contract(
            contract_address, method, abi, args, amount, asset_id
        )

        return invocation

    def sign_payload(self, unsigned_payload: str) -> PayloadSignature:
        """Sign the given unsigned payload.

        Args:
            unsigned_payload (str): The unsigned payload.

        Returns:
            PayloadSignature: The payload signature object.


        """
        if self.default_address is None:
            raise ValueError("Default address does not exist")

        return self.default_address.sign_payload(unsigned_payload)

    @property
    def default_address(self) -> WalletAddress | None:
        """Get the default address of the wallet.

        Returns:
            Optional[WalletAddress]: The default address object, or None if not set.

        """
        return (
            self._address(self._model.default_address.address_id)
            if self._model.default_address is not None
            else None
        )

    def export_data(self) -> WalletData:
        """Export the wallet's data.

        Returns:
            WalletData: The wallet's data.

        Raises:
            ValueError: If the wallet does not have a seed loaded.

        """
        if self._master is None or self._seed is None:
            raise ValueError("Wallet does not have seed loaded")

        return WalletData(self.id, self._seed)

    def save_seed(self, file_path: str, encrypt: bool | None = False) -> None:
        """Save the wallet seed to a file.

        Args:
            file_path (str): The path to the file where the seed will be saved.
            encrypt (Optional[bool]): Whether to encrypt the seed before saving. Defaults to False.

        Raises:
            ValueError: If the wallet does not have a seed loaded.

        """
        if self._master is None or self._seed is None:
            raise ValueError("Wallet does not have seed loaded")

        key = self._encryption_key()

        existing_seeds = self._existing_seeds(file_path)

        seed_to_store = self._seed
        auth_tag = ""
        iv = ""

        if encrypt:
            cipher = AES.new(key, AES.MODE_GCM)
            iv = cipher.nonce.hex()

            encrypted_data, auth_tag_bytes = cipher.encrypt_and_digest(bytes.fromhex(self._seed))

            seed_to_store = encrypted_data.hex()
            auth_tag = auth_tag_bytes.hex()

        existing_seeds[self.id] = {
            "seed": seed_to_store,
            "encrypted": encrypt,
            "auth_tag": auth_tag,
            "iv": iv,
        }

        with open(file_path, "w") as f:
            json.dump(existing_seeds, f, indent=4)

    def load_seed(self, file_path: str) -> None:
        """Load the wallet seed from a file.

        Args:
            file_path (str): The path to the file containing the seed data.

        Raises:
            ValueError: If the file does not contain seed data for this wallet or if decryption fails.

        """
        existing_seeds = self._existing_seeds(file_path)

        if self.id not in existing_seeds:
            raise ValueError(f"File {file_path} does not cantain seed data for wallet {self.id}")

        seed_data = existing_seeds[self.id]

        seed = seed_data["seed"]

        if seed_data["encrypted"]:
            key = self._encryption_key()
            encrypted_seed = bytes.fromhex(seed)
            cipher = AES.new(key, AES.MODE_GCM, nonce=bytes.fromhex(seed_data["iv"]))
            auth_tag = bytes.fromhex(seed_data["auth_tag"])
            try:
                decrypted_seed = cipher.decrypt_and_verify(encrypted_seed, auth_tag)
                seed = decrypted_seed.hex()
            except (ValueError, KeyError) as e:
                raise ValueError(f"Unable to decrypt seed for wallet {self.id}") from e

        self._seed = seed
        self._master = self._set_master_node()

    def _encryption_key(self) -> bytes:
        """Generate an encryption key based on the private key.

        Returns:
            bytes: The generated encryption key.

        """
        private_key = serialization.load_pem_private_key(Cdp.private_key.encode(), password=None)

        public_key = private_key.public_key()

        shared_secret = private_key.exchange(ec.ECDH(), public_key)

        return hashlib.sha256(shared_secret).digest()

    def _existing_seeds(self, file_path: str) -> dict[str, Any]:
        """Load existing seeds from a file.

        Args:
            file_path (str): The path to the file containing seed data.

        Returns:
            Dict[str, Any]: A dictionary of existing seeds.

        """
        seeds_in_file = {}

        if os.path.exists(file_path):
            with open(file_path) as f:
                seeds_in_file = json.load(f)

        return seeds_in_file

    def _set_addresses(self) -> None:
        """Set the addresses of the wallet by fetching them from the API.

        Returns:
            None

        """
        addresses = Cdp.api_clients.addresses.list_addresses(self.id, limit=self.MAX_ADDRESSES)

        self._addresses = [
            self._build_wallet_address(model, index) for index, model in enumerate(addresses.data)
        ]

    def _build_wallet_address(self, model: AddressModel, index: int | None = None) -> WalletAddress:
        """Build a wallet address object.

        Args:
            model (AddressModel): The address model.
            index (Optional[int]): The index of the address. Defaults to None.

        Returns:
            WalletAddress: The created address object.

        Raises:
            ValueError: If the derived key does not match the wallet.

        """
        if not self.can_sign:
            return WalletAddress(model)

        key = self._derive_key(index)
        account = Account.from_key(key.PrivateKey().Raw().ToHex())

        if account.address != model.address_id:
            raise ValueError("Derived key does not match wallet")

        return WalletAddress(model, account)

    def _address(self, address_id: str) -> WalletAddress | None:
        """Get an address by its ID.

        Args:
            address_id (str): The ID of the address to retrieve.

        Returns:
            Optional[WalletAddress]: The retrieved address object, or None if not found.

        """
        return next(
            (address for address in self.addresses if address.address_id == address_id),
            None,
        )

    def _set_master_node(self) -> Bip32Slip10Secp256k1 | None:
        """Set the master node for the wallet.

        Returns:
            Optional[Bip32Slip10Secp256k1]: The master node, or None if no seed is available.

        """
        if self._seed is None:
            seed = os.urandom(64)
            self._seed = seed.hex()

        if self._seed == "":
            return None

        seed = bytes.fromhex(self._seed)

        self._validate_seed(seed)

        return Bip32Slip10Secp256k1.FromSeed(seed)

    def _validate_seed(self, seed: bytes) -> None:
        """Validate the seed.

        Args:
            seed (bytes): The seed to validate.

        Raises:
            ValueError: If the seed length is invalid.

        """
        if len(seed) != 64:
            raise ValueError("Invalid seed length")

    def _derive_key(self, index: int) -> Bip32Slip10Secp256k1:
        """Derive a key from the master node.

        Args:
            index (int): The index to use for key derivation.

        Returns:
            Bip32Slip10Secp256k1: The derived key.

        """
        return self._master.DerivePath("m/44'/60'/0'/0" + f"/{index}")

    def _create_attestation(self, key: Bip32Slip10Secp256k1, public_key_hex: str) -> str:
        """Create an attestation for the given private key in the format expected.

        Args:
            key (Bip32Slip10Secp256k1): The private key.
            public_key_hex (str): The public key in hexadecimal format.

        Returns:
            str: The hexadecimal representation of the attestation.

        """
        payload = json.dumps(
            {"wallet_id": self.id, "public_key": public_key_hex}, separators=(",", ":")
        )

        signature = coincurve.PrivateKey(key.PrivateKey().Raw().ToBytes()).sign_recoverable(
            payload.encode()
        )

        r = signature[:32]
        s = signature[32:64]
        v = signature[64] + 27 + 4

        attestation = bytes([v]) + r + s

        return attestation.hex()

    def __str__(self) -> str:
        """Return a string representation of the Wallet object.

        Returns:
            str: A string representation of the Wallet.

        """
        return f"Wallet: (id: {self.id}, network_id: {self.network_id}, server_signer_status: {self.server_signer_status})"

    def __repr__(self) -> str:
        """Return a string representation of the Wallet object.

        Returns:
            str: A string representation of the Wallet.

        """
        return str(self)

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

        Raises:
            ValueError: If the default address does not exist.

        """
        if self.default_address is None:
            raise ValueError("Default address does not exist")

        return self.default_address.deploy_token(name, symbol, str(total_supply))

    def deploy_nft(self, name: str, symbol: str, base_uri: str) -> SmartContract:
        """Deploy an NFT smart contract.

        Args:
            name (str): The name of the NFT.
            symbol (str): The symbol of the NFT.
            base_uri (str): The base URI for the NFT.

        Returns:
            SmartContract: The deployed smart contract.

        Raises:
            ValueError: If the default address does not exist.

        """
        if self.default_address is None:
            raise ValueError("Default address does not exist")

        return self.default_address.deploy_nft(name, symbol, base_uri)

    def deploy_multi_token(self, uri: str) -> SmartContract:
        """Deploy a multi-token smart contract.

        Args:
            uri (str): The URI for the multi-token contract.

        Returns:
            SmartContract: The deployed smart contract.

        Raises:
            ValueError: If the default address does not exist.

        """
        if self.default_address is None:
            raise ValueError("Default address does not exist")

        return self.default_address.deploy_multi_token(uri)
