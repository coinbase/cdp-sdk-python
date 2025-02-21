from dataclasses import dataclass
from typing import Literal

from cdp.client.models.network_identifier import NetworkIdentifier

# Only SmartWallet related chains are listed here right now
SupportedChainId = Literal[8453, 84532]

CHAIN_ID_TO_NETWORK_ID: dict[SupportedChainId, NetworkIdentifier] = {
    8453: "base-mainnet",
    84532: "base-sepolia",
}


@dataclass(frozen=True)
class Network:
    """Represents a network with its chain ID and network identifier."""

    chain_id: SupportedChainId
    network_id: NetworkIdentifier

    @classmethod
    def from_chain_id(cls, chain_id: SupportedChainId) -> "Network":
        """Create a Network instance from a supported chain ID."""
        return cls(chain_id, CHAIN_ID_TO_NETWORK_ID[chain_id])
