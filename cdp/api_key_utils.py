import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


def _parse_private_key(key_str: str):
    """Parse a private key from a given string representation.

    Args:
        key_str (str): A string representing the private key. It should be either a PEM-encoded
            key (for ECDSA keys) or a base64-encoded string (for Ed25519 keys).

    Returns:
        An instance of a private key. Specifically:

    Raises:
        ValueError: If the key cannot be parsed as a valid PEM-encoded key or a base64-encoded
            Ed25519 private key.

    """
    key_data = key_str.encode()
    try:
        return serialization.load_pem_private_key(key_data, password=None)
    except Exception:
        try:
            decoded_key = base64.b64decode(key_str)
            if len(decoded_key) == 32:
                return ed25519.Ed25519PrivateKey.from_private_bytes(decoded_key)
            elif len(decoded_key) == 64:
                return ed25519.Ed25519PrivateKey.from_private_bytes(decoded_key[:32])
            else:
                raise ValueError("Ed25519 private key must be 32 or 64 bytes after base64 decoding")
        except Exception as e:
            raise ValueError("Could not parse the private key") from e
