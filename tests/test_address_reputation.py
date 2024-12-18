import pytest
from unittest.mock import Mock, patch
from cdp.address_reputation import AddressReputation


def test_address_reputation_initialization(address_reputation_factory):
    address_reputation = address_reputation_factory()
    assert isinstance(address_reputation, AddressReputation)


def test_address_reputation_score(address_reputation_factory):
    address_reputation = address_reputation_factory()

    assert address_reputation.score == 10


def test_address_reputation_metadata(address_reputation_factory):
    address_reputation = address_reputation_factory()

    assert address_reputation.metadata.total_transactions == 2
    assert address_reputation.metadata.unique_days_active == 3


def test_address_reputation_risky(address_reputation_factory):
    address_reputation = address_reputation_factory(score=-5)
    assert address_reputation.risky is True

    address_reputation = address_reputation_factory(score=0)
    assert address_reputation.risky is False

    address_reputation = address_reputation_factory(score=5)
    assert address_reputation.risky is False


def test_address_reputation_str(address_reputation_factory):
    address_reputation = address_reputation_factory(score=10)
    expected_str = "Address Reputation: (score=10, metadata=(total_transactions=2, unique_days_active=3, longest_active_streak=4, current_active_streak=5, activity_period_days=6, token_swaps_performed=7, bridge_transactions_performed=8, lend_borrow_stake_transactions=9, ens_contract_interactions=10, smart_contract_deployments=10))"
    assert str(address_reputation) == expected_str


def test_address_reputation_repr(address_reputation_factory):
    address_reputation = address_reputation_factory(score=10)
    expected_repr = "Address Reputation: (score=10, metadata=(total_transactions=2, unique_days_active=3, longest_active_streak=4, current_active_streak=5, activity_period_days=6, token_swaps_performed=7, bridge_transactions_performed=8, lend_borrow_stake_transactions=9, ens_contract_interactions=10, smart_contract_deployments=10))"
    assert repr(address_reputation) == expected_repr
