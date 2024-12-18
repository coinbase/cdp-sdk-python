from cdp.cdp import Cdp
from cdp.client import AddressReputationMetadata
from cdp.client.models.address_reputation import AddressReputation as AddressReputationModel


class AddressReputation:
    """A representation of the reputation of a blockchain address."""

    def __init__(self, model: AddressReputationModel) -> None:
        """Initialize the AddressReputation class."""
        if not model:
            raise ValueError("model is required")

        self._score = model.score
        self._metadata = model.metadata

    @property
    def metadata(self) -> AddressReputationMetadata:
        return self._metadata

    @property
    def score(self) -> int:
        return self._score

    @property
    def risky(self) -> bool:
        return self.score < 0

    def __str__(self) -> str:
        metadata = ", ".join(f"{key}={getattr(self.metadata, key)}" for key in vars(self.metadata))
        return f"Address Reputation: (score={self.score}, metadata=({metadata}))"

    def __repr__(self) -> str:
        return str(self)
