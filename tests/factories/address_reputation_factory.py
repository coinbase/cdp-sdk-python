import pytest

from cdp.client.models.address_reputation import AddressReputation as AddressReputationModel
from cdp.client.models.address_reputation_metadata import AddressReputationMetadata
from cdp.reputation import AddressReputation


@pytest.fixture
def address_reputation_model_factory():
    """Create and return a factory for creating AddressReputation fixtures."""

    def _create_address_reputation_model(
            reputation_score=1,
            total_transactions=2,
            unique_days_active=3,
            longest_active_streak=4,
            current_active_streak=5,
            activity_period_days=6,
            token_swaps_performed=7,
            bridge_transactions_performed=8,
            lend_borrow_stake_transactions=9,
            ens_contract_interactions=10,
            smart_contract_deployments=10
    ):
        metadata = AddressReputationMetadata(
            total_transactions=total_transactions,
            unique_days_active=unique_days_active,
            longest_active_streak=longest_active_streak,
            current_active_streak=current_active_streak,
            activity_period_days=activity_period_days,
            token_swaps_performed=token_swaps_performed,
            bridge_transactions_performed=bridge_transactions_performed,
            lend_borrow_stake_transactions=lend_borrow_stake_transactions,
            ens_contract_interactions=ens_contract_interactions,
            smart_contract_deployments=smart_contract_deployments
        )
        return AddressReputationModel(reputation_score=reputation_score, metadata=metadata)

    return _create_address_reputation_model

@pytest.fixture
def address_reputation_factory(address_reputation_model_factory):
    """Create and return a factory for creating AddressReputation fixtures."""

    def _create_address_reputation(reputation_score: int| None):
        reputation_model = address_reputation_model_factory(reputation_score)
        return AddressReputation(reputation_model)

    return _create_address_reputation
