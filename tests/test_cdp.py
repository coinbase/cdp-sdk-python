import pytest

from cdp import Cdp
from cdp.errors import UninitializedSDKError


def test_uninitialized_error():
    """Test that direct access to API clients raises UninitializedSDKError."""
    Cdp.api_clients = Cdp.ApiClientsWrapper()

    with pytest.raises(UninitializedSDKError) as excinfo:
        _ = Cdp.api_clients.wallets

    assert "Coinbase SDK has not been initialized" in str(excinfo.value)
    assert "Cdp.configure(api_key_name=" in str(excinfo.value)
    assert "Cdp.configure_from_json(file_path=" in str(excinfo.value)
