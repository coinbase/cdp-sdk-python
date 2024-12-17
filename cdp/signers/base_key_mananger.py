from abc import ABC, abstractmethod
from base_signer import BaseSigner, LocalSigner


class BaseKeyManager(ABC):
    """Abstract base class for managing cryptographic keys."""

    @property
    @abstractmethod
    def seed(self) -> str | None:
        """Gets the seed.

        Returns:
            str | None: The current master node seed, or None if not set.

        """
        pass

    @seed.setter
    @abstractmethod
    def seed(self, seed: str | None = None) -> None:
        """Set the master node seed.

        Args:
            seed (str | None): The seed to initialize the master node. If None, resets the master node.

        """
        pass

    @abstractmethod
    def derive_key(self, index: int) -> BaseSigner:
        """Derive a key pair (private and public key) at the specified index.

        Args:
            index (int): The index at which to derive the key.

        Returns:
            BaseSigner: A signer backed by the newly derived key.

        """
        pass


from bip_utils import Bip32Slip10Secp256k1
import os


class LocalBip32KeyManager(BaseKeyManager):

    def __init__(self) -> None:
        self._master_node = None
        self._seed = None
        self._derivation_path = "m/44'/60'/0'/0"

    @property
    def seed(self) -> str | None:
        """Gets the seed.

        Returns:
            str | None: The current master node seed, or None if not set.

        """
        return self._seed

    @seed.setter
    def seed(self, seed: str | None = None) -> None:
        """Set the master node seed.

        Args:
            seed (str | None): The seed to initialize the master node. If None, resets the master node.

        """
        if self._seed is None:
            seed = os.urandom(64)
            self._seed = seed.hex()

        if self._seed == "":
            return None

        seed = bytes.fromhex(self._seed)

        self._validate_seed(seed)

        self._master_node = Bip32Slip10Secp256k1.FromSeed(seed)

    def derive_key(self, index: int) -> LocalSigner:
        """Derive a key pair (private and public key) at the specified index.

        Args:
            index (int): The index at which to derive the key.

        Returns:
            LocalSigner: A local signer backed by the newly derived key.

        """
        derived_key: Bip32Slip10Secp256k1 = self._master.DerivePath(self._derivation_path + f"/{index}")

        private_key = derived_key.PrivateKey().Raw().ToBytes()

        return LocalSigner(private_key)
