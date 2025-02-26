import os
from unittest.mock import MagicMock

from cdp import Cdp
import pytest

from cdp.api_clients import ApiClients

@pytest.fixture(autouse=True)
def initialize_cdp():
    """Initialize the CDP SDK with mock API clients before each test."""
    mock_api_clients = MagicMock(spec=ApiClients)
    Cdp.api_clients = mock_api_clients
    

    
    
factory_modules = [
    f[:-3] for f in os.listdir("./tests/factories") if f.endswith(".py") and f != "__init__.py"
]

pytest_plugins = [f"tests.factories.{module_name}" for module_name in factory_modules]
