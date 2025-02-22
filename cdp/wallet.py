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
from bip_utils import Bip32Slip10Secp256k1, Bip39MnemonicValidator, Bip39SeedGenerator
from Crypto.Cipher import AES
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec  # unchanged: ed25519 import added below
from cryptography.hazmat.primitives.asymmetric import ed25519
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
from cdp.client.models.create_wallet_webhook_request import CreateWalletWebhookRequest
from cdp.client.models.wallet import Wallet as WalletModel
from cdp.client.models.wallet_list import WalletList
from cdp.contract_invocation import ContractInvocation
from cdp.faucet_transaction import FaucetTransaction
from cdp.fund_operation import FundOperation
from cdp.fund_quote import FundQuote
from cdp.mnemonic_seed_phrase import MnemonicSeedPhrase
from cdp.payload_signature import PayloadSignature
from cdp.smart_contract import SmartContract
from cdp.trade import Trade
from cdp.transfer import Transfer
from cdp.wallet_address import WalletAddress
from cdp.wallet_data import WalletData
from cdp.webhook import Webhook


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
        """Create a new wallet with a random seed.

        Args:
            network_id (str): The network ID of the wallet. Defaults to "base-sepolia".
            interval_seconds (float): The interval between checks in seconds. Defaults to 0.2.
            timeout_seconds (float): The maximum time to wait for the server signer to be active. Defaults to 20.

        Returns:
            Wallet: The created wallet object.
        """
        return cls.create_with_seed(
            seed=None,
            network_id=network_id,
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds,
        )

    @classmethod
    def create_with_seed(
        cls,
        seed: str | None = None,
        network_id: str = "base-sepolia",
        interval_seconds: float = 0.2,
        timeout_seconds: float = 20,
    ) -> "Wallet":
        """Create a new wallet with the given seed.

        Args:
            seed (str): The seed to use for the wallet. If None, a random seed will be generated.
            network_id (str): The network ID of the wallet. Defaults to "base-sepolia".
            interval_seconds (float): The interval between checks in seconds. Defaults to 0.2.
            timeout_seconds (float): The maximum time to wait for the server signer to be active. Defaults to 20.

        Returns:
            Wallet: The created wallet object.
        """
        create_wallet_request = CreateWalletRequest(
            wallet=CreateWalletRequestWallet(
                network_id=network_id, use_server_signer=Cdp.use_server_signer
            )
        )

        model = Cdp.api_clients.wallets.create_wallet(create_wallet_request)
        wallet = cls(model, seed)

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
        """
        start_time = time.time()

        while self.server_signer_status != "active_seed":
            self.reload()

            if time.time() - start_time > timeout_seconds:
                raise TimeoutError("Wallet creation timed out. Check status of your Server-Signer")

            time.sleep(interval_seconds)

        return self

    def reload(self) -> None:
        """Reload the wallet model from the API."""
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
        """
        model = Cdp.api_clients.wallets.get_wallet(wallet_id)

        return cls(model, "")

    @classmethod
    def list(cls) -> Iterator["Wallet"]:
        """List wallets.

        Returns:
            Iterator[Wallet]: An iterator of wallet objects.
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
    def import_wallet(
        cls, data: WalletData | MnemonicSeedPhrase, network_id: str = "base-sepolia"
    ) -> "Wallet":
        """Import a wallet from previously exported wallet data or a mnemonic seed phrase."""
        if isinstance(data, MnemonicSeedPhrase):
            # Validate mnemonic phrase
            if not data.mnemonic_phrase:
                raise ValueError("BIP-39 mnemonic seed phrase must be provided")

            # Validate the mnemonic using bip_utils
            if not Bip39MnemonicValidator().IsValid(data.mnemonic_phrase):
                raise ValueError("Invalid BIP-39 mnemonic seed phrase")

            # Convert mnemonic to seed
            seed_bytes = Bip39SeedGenerator(data.mnemonic_phrase).Generate()
            seed = seed_bytes.hex()

            # Create wallet using the provided seed
            wallet = cls.create_with_seed(seed=seed, network_id=network_id)
            wallet._set_addresses()
            return wallet

        elif isinstance(data, WalletData):
            model = Cdp.api_clients.wallets.get_wallet(data.wallet_id)
            wallet = cls(model, data.seed)
            wallet._set_addresses()
            return wallet

        raise ValueError("Data must be a WalletData or MnemonicSeedPhrase instance")

    @classmethod
    def import_data(cls, data: WalletData) -> "Wallet":
        """Import a wallet from previously exported wallet data."""
        return cls.import_wallet(data)

    def create_address(self) -> "WalletAddress":
        """Create a new address for the wallet."""
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

    def create_webhook(self, notification_uri: str) -> "Webhook":
        """Create a new webhook for the wallet."""
        create_wallet_webhook_request = CreateWalletWebhookRequest(
            notification_uri=notification_uri
        )
        model = Cdp.api_clients.webhooks.create_wallet_webhook(
            wallet_id=self.id, create_wallet_webhook_request=create_wallet_webhook_request
        )

        return Webhook(model)

    def faucet(self, asset_id: str | None = None) -> FaucetTransaction:
        """Request faucet funds."""
        if self.default_address is None:
            raise ValueError("Default address does not exist")

        return self.default_address.faucet(asset_id)

    def balance(self, asset_id: str) -> Decimal:
        """Get the balance of a specific asset for the default address."""
        if self.default_address is None:
            raise ValueError("Default address does not exist")

        return self.default_address.balance(asset_id)

    def balances(self) -> BalanceMap:
        """List balances of the address."""
        if self.default_address is None:
            raise ValueError("Default address does not exist")

        return self.default_address.balances()

    def transfer(
        self,
        amount: Number | Decimal | str,
        asset_id: str,
        destination: Union[Address, "Wallet", str],
        gasless: bool = False,
        skip_batching: bool = False,
    ) -> Transfer:
        """Transfer funds from the wallet."""
        if self.default_address is None:
            raise ValueError("Default address does not exist")

        # Convert amount to Decimal
        if isinstance(amount, float | int | str):
            amount = Decimal(amount)

        return self.default_address.transfer(amount, asset_id, destination, gasless, skip_batching)

    def trade(self, amount: Number | Decimal | str, from_asset_id: str, to_asset_id: str) -> Trade:
        """Trade funds from the wallet address."""
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
        """Invoke a method on the specified contract address."""
        if self.default_address is None:
            raise ValueError("Default address does not exist")

        invocation = self.default_address.invoke_contract(
            contract_address, method, abi, args, amount, asset_id
        )

        return invocation

    def sign_payload(self, unsigned_payload: str) -> PayloadSignature:
        """Sign the given unsigned payload."""
        if self.default_address is None:
            raise ValueError("Default address does not exist")

        return self.default_address.sign_payload(unsigned_payload)

    @property
    def default_address(self) -> WalletAddress | None:
        """Get the default address of the wallet."""
        return (
            self._address(self._model.default_address.address_id)
            if self._model.default_address is not None
            else None
        )

    def export_data(self) -> WalletData:
        """Export the wallet's data."""
        if self._master is None or self._seed is None:
            raise ValueError("Wallet does not have seed loaded")

        return WalletData(self.id, self._seed, self.network_id)

    def save_seed(self, file_path: str, encrypt: bool | None = False) -> None:
        """(Deprecated) Save the wallet seed to a file."""
        import warnings

        warnings.warn(
            "save_seed() is deprecated and will be removed in a future version. Use save_seed_to_file() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.save_seed_to_file(file_path, encrypt)

    def save_seed_to_file(self, file_path: str, encrypt: bool | None = False) -> None:
        """Save the wallet seed to a file."""
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
            "network_id": self.network_id,
        }

        with open(file_path, "w") as f:
            json.dump(existing_seeds, f, indent=4)

    def load_seed(self, file_path: str) -> None:
        """(Deprecated) Load the wallet seed from a file."""
        import warnings

        warnings.warn(
            "load_seed() is deprecated and will be removed in a future version. Use load_seed_from_file() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.load_seed_from_file(file_path)

    def load_seed_from_file(self, file_path: str) -> None:
        """Load the wallet seed from a file."""
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

    # --- Business Change: Updated _encryption_key to support Ed25519 keys ---
    def _encryption_key(self) -> bytes:
        """Generate an encryption key based on the private key.
        
        For ECDSA keys (PEM encoded), an ECDH exchange is performed.
        For Ed25519 keys (base64 encoded), the raw private key bytes are hashed.
        
        Returns:
            bytes: The generated encryption key.
        """
        import base64, hashlib
        from cryptography.hazmat.primitives.asymmetric import ec, ed25519

        # Attempt to load as a PEM-encoded key (for ECDSA)
        try:
            key_obj = serialization.load_pem_private_key(Cdp.private_key.encode(), password=None)
        except Exception:
            # If PEM loading fails, assume the key is provided as a base64-encoded Ed25519 key.
            try:
                decoded = base64.b64decode(Cdp.private_key)
                if len(decoded) == 32:
                    key_obj = ed25519.Ed25519PrivateKey.from_private_bytes(decoded)
                elif len(decoded) == 64:
                    key_obj = ed25519.Ed25519PrivateKey.from_private_bytes(decoded[:32])
                else:
                    raise ValueError("Invalid Ed25519 key length")
            except Exception as e2:
                raise ValueError("Could not parse the private key") from e2

        # For ECDSA keys, perform an ECDH exchange with its own public key.
        if isinstance(key_obj, ec.EllipticCurvePrivateKey):
            public_key = key_obj.public_key()
            shared_secret = key_obj.exchange(ec.ECDH(), public_key)
            return hashlib.sha256(shared_secret).digest()
        # For Ed25519 keys, derive the encryption key by hashing the raw private key bytes.
        elif isinstance(key_obj, ed25519.Ed25519PrivateKey):
            raw_bytes = key_obj.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption(),
            )
            return hashlib.sha256(raw_bytes).digest()
        else:
            raise ValueError("Unsupported key type for encryption key derivation")
    # --- End of Business Change ---

    def _existing_seeds(self, file_path: str) -> dict[str, Any]:
        """Load existing seeds from a file."""
        seeds_in_file = {}

        if os.path.exists(file_path):
            with open(file_path) as f:
                seeds_in_file = json.load(f)

        return seeds_in_file

    def _set_addresses(self) -> None:
        """Set the addresses of the wallet by fetching them from the API."""
        addresses = Cdp.api_clients.addresses.list_addresses(self.id, limit=self.MAX_ADDRESSES)

        self._addresses = [
            self._build_wallet_address(model, model.index) for _, model in enumerate(addresses.data)
        ]

    def _build_wallet_address(self, model: AddressModel, index: int | None = None) -> WalletAddress:
        """Build a wallet address object."""
        if not self.can_sign:
            return WalletAddress(model)

        key = self._derive_key(index)
        account = Account.from_key(key.PrivateKey().Raw().ToHex())

        if account.address != model.address_id:
            raise ValueError("Derived key does not match wallet")

        return WalletAddress(model, account)

    def _address(self, address_id: str) -> WalletAddress | None:
        """Get an address by its ID."""
        return next(
            (address for address in self.addresses if address.address_id == address_id),
            None,
        )

    def _set_master_node(self) -> Bip32Slip10Secp256k1 | None:
        """Set the master node for the wallet."""
        if self._seed is None:
            seed = os.urandom(64)
            self._seed = seed.hex()

        if self._seed == "":
            return None

        seed = bytes.fromhex(self._seed)

        self._validate_seed(seed)

        return Bip32Slip10Secp256k1.FromSeed(seed)

    def _validate_seed(self, seed: bytes) -> None:
        """Validate the seed."""
        if len(seed) != 32 and len(seed) != 64:
            raise ValueError("Seed must be 32 or 64 bytes")

    def _derive_key(self, index: int) -> Bip32Slip10Secp256k1:
        """Derive a key from the master node."""
        return self._master.DerivePath("m/44'/60'/0'/0" + f"/{index}")

    def _create_attestation(self, key: Bip32Slip10Secp256k1, public_key_hex: str) -> str:
        """Create an attestation for the given private key."""
        payload = json.dumps({"wallet_id": self.id, "public_key": public_key_hex}, separators=(",", ":"))
        signature = coincurve.PrivateKey(key.PrivateKey().Raw().ToBytes()).sign_recoverable(payload.encode())
        r = signature[:32]
        s = signature[32:64]
        v = signature[64] + 27 + 4
        attestation = bytes([v]) + r + s
        return attestation.hex()

    def __str__(self) -> str:
        """Return a string representation of the Wallet object."""
        return f"Wallet: (id: {self.id}, network_id: {self.network_id}, server_signer_status: {self.server_signer_status})"

    def __repr__(self) -> str:
        """Return a string representation of the Wallet object."""
        return str(self)

    def deploy_token(
        self, name: str, symbol: str, total_supply: Number | Decimal | str
    ) -> SmartContract:
        if self.default_address is None:
            raise ValueError("Default address does not exist")
        return self.default_address.deploy_token(name, symbol, str(total_supply))

    def deploy_nft(self, name: str, symbol: str, base_uri: str) -> SmartContract:
        if self.default_address is None:
            raise ValueError("Default address does not exist")
        return self.default_address.deploy_nft(name, symbol, base_uri)

    def deploy_multi_token(self, uri: str) -> SmartContract:
        if self.default_address is None:
            raise ValueError("Default address does not exist")
        return self.default_address.deploy_multi_token(uri)

    def deploy_contract(
        self,
        solidity_version: str,
        solidity_input_json: str,
        contract_name: str,
        constructor_args: dict,
    ) -> SmartContract:
        if self.default_address is None:
            raise ValueError("Default address does not exist")
        return self.default_address.deploy_contract(solidity_version, solidity_input_json, contract_name, constructor_args)

    def fund(self, amount: Number | Decimal | str, asset_id: str) -> FundOperation:
        if self.default_address is None:
            raise ValueError("Default address does not exist")
        return self.default_address.fund(amount, asset_id)

    def quote_fund(self, amount: Number | Decimal | str, asset_id: str) -> FundQuote:
        if self.default_address is None:
            raise ValueError("Default address does not exist")
        return self.default_address.quote_fund(amount, asset_id)
