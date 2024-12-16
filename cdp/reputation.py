from cdp.cdp import Cdp
from cdp.client.models.address_reputation import AddressReputation as AddressReputationModel


class AddressReputation:
    """A representation of the reputation of a blockchain address.
    """

    def __init__(self, model: AddressReputationModel) -> None:
        self._model = model

    @classmethod
    def fetch(cls, address_id:str, network_id:str) -> "AddressReputation":

        # Use the ReputationApi to fetch address reputation
        model = Cdp.api_clients.reputation.get_address_reputation(
            address_id=address_id,
            network_id=network_id,
        )

        return cls(model)

    @property
    def score(self):
        return self._model.score

    @property
    def metadata(self):
        return self._model.metadata

    def is_risky(self):
        return self.score < 0

    def __str__(self) -> str:
        return self.pretty_print_object(
            self.__class__.__name__,
            score=self.score,
            metadata=self.metadata.to_dict()
        )

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def pretty_print_object(class_name, **kwargs):
        """Pretty prints an object as a string.
        """
        attributes = ', '.join(f"{key}={value}" for key, value in kwargs.items())
        return f"<{class_name}({attributes})>"

