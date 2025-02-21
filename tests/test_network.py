from dataclasses import FrozenInstanceError

import pytest

from cdp.network import Network


def test_network_creation():
    """Test basic network instance creation."""
    network = Network(8453, "base-mainnet")
    assert network.chain_id == 8453
    assert network.network_id == "base-mainnet"


def test_network_immutability():
    """Test that the network instance is immutable."""
    network = Network(8453, "base-mainnet")
    with pytest.raises(FrozenInstanceError):
        network.chain_id = 84532


def test_from_chain_id_factory():
    """Test the from_chain_id factory method."""
    network = Network.from_chain_id(8453)
    assert network.chain_id == 8453
    assert network.network_id == "base-mainnet"
