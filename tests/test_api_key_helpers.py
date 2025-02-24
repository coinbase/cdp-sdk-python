import base64
from cryptography.hazmat.primitives.asymmetric import ec, ed25519
from cryptography.hazmat.primitives import serialization

from cdp.api_key_helpers import _parse_private_key


DUMMY_ECDSA_PEM = "-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIMM75bm9WZCYPkfjXSUWNU5eHx47fWM2IpG8ki90BhRDoAoGCCqGSM49\nAwEHoUQDQgAEicwlaAqy7Z4SS7lvrEYoy6qR9Kf0n0jFzg+XExcXKU1JMr18z47W\n5mrftEqWIqPCLQ16ByoKW2Bsup5V3q9P4g==\n-----END EC PRIVATE KEY-----\n"
DUMMY_ED25519_BASE64 = "BXyKC+eFINc/6ztE/3neSaPGgeiU9aDRpaDnAbaA/vyTrUNgtuh/1oX6Vp+OEObV3SLWF+OkF2EQNPtpl0pbfA=="

def test_parse_private_key_pem_ec():
    """Test that a PEM-encoded ECDSA key is parsed correctly using a hardcoded dummy key."""
    parsed_key = _parse_private_key(DUMMY_ECDSA_PEM)
    assert isinstance(parsed_key, ec.EllipticCurvePrivateKey)


def test_parse_private_key_ed25519_32():
    """Test that a base64-encoded 32-byte Ed25519 key is parsed correctly using a hardcoded dummy key."""
    parsed_key = _parse_private_key(DUMMY_ED25519_BASE64)
    assert isinstance(parsed_key, ed25519.Ed25519PrivateKey)


def test_parse_private_key_ed25519_64():
    """Test that a base64-encoded 64-byte input is parsed correctly by taking the first 32 bytes."""
    # Create a 64-byte dummy by concatenating the 32-byte dummy with itself.
    dummy_64 = b'\x01' * 32 + b'\x01' * 32
    dummy_64_base64 = base64.b64encode(dummy_64).decode("utf-8")
    parsed_key = _parse_private_key(dummy_64_base64)
    assert isinstance(parsed_key, ed25519.Ed25519PrivateKey)


def test_parse_private_key_invalid():
    """Test that an invalid key string raises a ValueError."""
    try:
        _parse_private_key("invalid_key")
    except ValueError as e:
        assert "Could not parse the private key" in str(e)
    else:
        assert False, "Expected ValueError was not raised"
