from abc import ABC, abstractmethod


class BaseSigner(ABC):
    """Abstract base class for cryptographic signing."""

    @property
    @abstractmethod
    def private_key(self) -> bytes:
        """Retrieves the private key data associated with the signer.

        Returns:
            bytes: The private key in bytes format.

        """
        pass

    @property
    @abstractmethod
    def public_address(self) -> str:
        """Retrieves the public address derived from the public key.

        Returns:
            str: The public address in string format.

        """
        pass

    @abstractmethod
    def sign(self, unsigned_payload: bytes) -> bytes:
        """Signs the provided payload using the associated private key.

        Args:
            unsigned_payload (bytes): The data payload to be signed.

        Returns:
            bytes: The signature in bytes format.

        """
        pass

from eth_account.signers.local import LocalAccount
from eth_account.types import PrivateKeyType


class LocalSigner(BaseSigner):

    def __init__(self, private_key: PrivateKeyType) -> None:
        self._local_account: LocalAccount = LocalAccount.from_key(private_key)

    @property
    def private_key(self) -> bytes:
        """Retrieves the public key associated with the signer.

        Returns:
            bytes: The public key in bytes format.

        """
        return bytes(self._local_account)

    @property
    def public_address(self) -> str:
        """Retrieves the public address derived from the public key.

        Returns:
            str: The public address in string format.

        """
        return self._local_account.address

    def sign(self, unsigned_payload: bytes) -> bytes:
        """Signs the provided payload using the associated private key.

        Args:
            unsigned_payload (bytes): The data payload to be signed.

        Returns:
            bytes: The signature in bytes format.

        """
        signed_message = self._local_account.unsafe_sign_hash(unsigned_payload)
        return signed_message.signature

