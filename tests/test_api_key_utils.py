import pytest
from cryptography.hazmat.primitives.asymmetric import ec, ed25519

from cdp.api_key_utils import _parse_private_key


def test_parse_private_key_pem_ec(dummy_key_factory):
    """Test that a PEM-encoded ECDSA key is parsed correctly using a dummy key from the factory."""
    dummy_key = dummy_key_factory("ecdsa")
    parsed_key = _parse_private_key(dummy_key)
    assert isinstance(parsed_key, ec.EllipticCurvePrivateKey)


def test_parse_private_key_ed25519_32(dummy_key_factory):
    """Test that a base64-encoded 32-byte Ed25519 key is parsed correctly using a dummy key from the factory."""
    dummy_key = dummy_key_factory("ed25519-32")
    parsed_key = _parse_private_key(dummy_key)
    assert isinstance(parsed_key, ed25519.Ed25519PrivateKey)


def test_parse_private_key_ed25519_64(dummy_key_factory):
    """Test that a base64-encoded 64-byte input is parsed correctly by taking the first 32 bytes using a dummy key from the factory."""
    dummy_key = dummy_key_factory("ed25519-64")
    parsed_key = _parse_private_key(dummy_key)
    assert isinstance(parsed_key, ed25519.Ed25519PrivateKey)


def test_parse_private_key_invalid():
    """Test that an invalid key string raises a ValueError."""
    with pytest.raises(ValueError, match="Could not parse the private key"):
        _parse_private_key("invalid_key")
