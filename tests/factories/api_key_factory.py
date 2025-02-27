import base64

import pytest


@pytest.fixture
def dummy_key_factory():
    """Create and return a factory function for generating dummy keys for testing.

    The factory accepts a `key_type` parameter with the following options:
      - "ecdsa": Returns a PEM-encoded ECDSA private key.
      - "ed25519-32": Returns a base64-encoded 32-byte Ed25519 private key.
      - "ed25519-64": Returns a base64-encoded 64-byte dummy Ed25519 key (the first 32 bytes will be used).
    """

    def _create_dummy(key_type: str = "ecdsa") -> str:
        if key_type == "ecdsa":
            return (
                "-----BEGIN EC PRIVATE KEY-----\n"
                "MHcCAQEEIMM75bm9WZCYPkfjXSUWNU5eHx47fWM2IpG8ki90BhRDoAoGCCqGSM49\n"
                "AwEHoUQDQgAEicwlaAqy7Z4SS7lvrEYoy6qR9Kf0n0jFzg+XExcXKU1JMr18z47W\n"
                "5mrftEqWIqPCLQ16ByoKW2Bsup5V3q9P4g==\n"
                "-----END EC PRIVATE KEY-----\n"
            )
        elif key_type == "ed25519-32":
            return "BXyKC+eFINc/6ztE/3neSaPGgeiU9aDRpaDnAbaA/vyTrUNgtuh/1oX6Vp+OEObV3SLWF+OkF2EQNPtpl0pbfA=="
        elif key_type == "ed25519-64":
            # Create a 64-byte dummy by concatenating a 32-byte sequence with itself.
            dummy_32 = b"\x01" * 32
            dummy_64 = dummy_32 + dummy_32
            return base64.b64encode(dummy_64).decode("utf-8")
        else:
            raise ValueError("Unsupported key type for dummy key creation")

    return _create_dummy
