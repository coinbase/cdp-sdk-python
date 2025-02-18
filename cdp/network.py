from dataclasses import dataclass
from typing import Literal

from cdp.client.models.network_identifier import NetworkIdentifier

# Only SmartWallet related chains are listed here right now
SupportedChainId = Literal[8453, 84532]

_CHAIN_ID_TO_NETWORK_ID: dict[SupportedChainId, NetworkIdentifier] = {
    8453: "base-mainnet",
    84532: "base-sepolia",
}


@dataclass(frozen=True)
class Network:
    """Represents a network with its chain ID and network identifier."""

    _chain_id: SupportedChainId
    _network_id: NetworkIdentifier

    @property
    def chain_id(self) -> SupportedChainId:
        """Returns the chain ID."""
        return self._chain_id

    @property
    def network_id(self) -> NetworkIdentifier:
        """Returns the network ID as a string."""
        return self._network_id

    @classmethod
    def from_chain_id(cls, chain_id: SupportedChainId) -> "Network":
        """Create a Network instance from a supported chain ID."""
        return cls(chain_id, _CHAIN_ID_TO_NETWORK_ID[chain_id])
