from unittest.mock import Mock, patch

from cdp.reputation import AddressReputation


def test_address_reputation_initialization(address_reputation_factory):
    address_reputation = address_reputation_factory(reputation_score=10)
    assert isinstance(address_reputation, AddressReputation)

@patch("cdp.Cdp.api_clients")
def test_address_reputation_score(mock_api_clients, address_reputation_factory):
    address_reputation = address_reputation_factory(reputation_score=10)

    mock_request_address_reputation = Mock()
    mock_request_address_reputation.return_value = address_reputation
    mock_api_clients.reputation.get_address_reputation = mock_request_address_reputation
    assert address_reputation.score == 10

def test_address_reputation_metadata(address_reputation_factory):
    address_reputation = address_reputation_factory(
        reputation_score=10,
        total_transactions=2,
        unique_days_active=3,
        longest_active_streak=4,
        current_active_streak=5,
        activity_period_days=6,
        token_swaps_performed=7,
        bridge_transactions_performed=8,
        lend_borrow_stake_transactions=9,
        ens_contract_interactions=10,
        smart_contract_deployments=11
    )
    assert address_reputation.metadata.total_transactions == 2
    assert address_reputation.metadata.unique_days_active == 3

def test_address_reputation_risky(address_reputation_factory):
    address_reputation = address_reputation_factory(reputation_score=-5)
    assert address_reputation.is_risky() is True

    address_reputation = address_reputation_factory(reputation_score=5)
    assert address_reputation.is_risky() is False

def test_address_reputation_str(address_reputation_factory):
    address_reputation = address_reputation_factory(reputation_score=10)
    expected_str = "<AddressReputation(score=10, metadata={'total_transactions': 2, 'unique_days_active': 3, 'longest_active_streak': 4, 'current_active_streak': 5, 'activity_period_days': 6, 'token_swaps_performed': 7, 'bridge_transactions_performed': 8, 'lend_borrow_stake_transactions': 9, 'ens_contract_interactions': 10, 'smart_contract_deployments': 11})>"
    assert str(address_reputation) == expected_str
