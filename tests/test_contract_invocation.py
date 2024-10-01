from decimal import Decimal
from unittest.mock import ANY, Mock, call, patch

import pytest

from cdp.contract_invocation import ContractInvocation
from cdp.errors import TransactionNotSignedError


def test_contract_invocation_initialization(contract_invocation_factory):
    """Test the initialization of a ContractInvocation object."""
    contract_invocation = contract_invocation_factory()
    assert isinstance(contract_invocation, ContractInvocation)


def test_contract_invocation_properties(contract_invocation_factory):
    """Test the properties of a ContractInvocation object."""
    contract_invocation = contract_invocation_factory()
    assert contract_invocation.contract_invocation_id == "test-invocation-id"
    assert contract_invocation.wallet_id == "test-wallet-id"
    assert contract_invocation.address_id == "0xaddressid"
    assert contract_invocation.contract_address == "0xcontractaddress"
    assert contract_invocation.method == "testMethod"
    assert contract_invocation.args == {"arg1": "value1"}
    assert contract_invocation.abi == {"abi": "data"}
    assert contract_invocation.amount == Decimal("1")  # 1 in atomic units
    assert contract_invocation.status.value == "complete"
    assert (
        contract_invocation.transaction_link == "https://sepolia.basescan.org/tx/0xtransactionlink"
    )
    assert contract_invocation.transaction_hash == "0xtransactionhash"


@patch("cdp.Cdp.api_clients")
@patch("cdp.contract_invocation.Asset")
def test_create_contract_invocation(
    mock_asset, mock_api_clients, contract_invocation_factory, asset_factory
):
    """Test the creation of a ContractInvocation object."""
    mock_fetch = Mock()
    mock_fetch.return_value = asset_factory()
    mock_asset.fetch = mock_fetch
    mock_asset.to_atomic_amount = Mock(return_value=Decimal("1"))

    mock_create_invocation = Mock()
    mock_create_invocation.return_value = contract_invocation_factory()._model
    mock_api_clients.contract_invocations.create_contract_invocation = mock_create_invocation

    contract_invocation = ContractInvocation.create(
        address_id="0xaddressid",
        wallet_id="test-wallet-id",
        network_id="base-sepolia",
        contract_address="0xcontractaddress",
        method="testMethod",
        abi=[{"abi": "data"}],
        args={"arg1": "value1"},
        amount=Decimal("1"),
        asset_id="wei",
    )

    assert isinstance(contract_invocation, ContractInvocation)
    mock_create_invocation.assert_called_once_with(
        wallet_id="test-wallet-id",
        address_id="0xaddressid",
        create_contract_invocation_request=ANY,
    )


@patch("cdp.Cdp.api_clients")
def test_broadcast_contract_invocation(mock_api_clients, contract_invocation_factory):
    """Test the broadcasting of a ContractInvocation object."""
    contract_invocation = contract_invocation_factory(status="signed")
    mock_broadcast = Mock(return_value=contract_invocation_factory(status="broadcast")._model)
    mock_api_clients.contract_invocations.broadcast_contract_invocation = mock_broadcast

    response = contract_invocation.broadcast()

    assert isinstance(response, ContractInvocation)
    mock_broadcast.assert_called_once_with(
        wallet_id=contract_invocation.wallet_id,
        address_id=contract_invocation.address_id,
        contract_invocation_id=contract_invocation.contract_invocation_id,
        broadcast_contract_invocation_request=ANY,
    )


def test_broadcast_unsigned_contract_invocation(contract_invocation_factory):
    """Test the broadcasting of an unsigned ContractInvocation object."""
    contract_invocation = contract_invocation_factory(status="pending")
    with pytest.raises(TransactionNotSignedError, match="Contract invocation is not signed"):
        contract_invocation.broadcast()


@patch("cdp.Cdp.api_clients")
def test_reload_contract_invocation(mock_api_clients, contract_invocation_factory):
    """Test the reloading of a ContractInvocation object."""
    contract_invocation = contract_invocation_factory(status="pending")
    complete_invocation = contract_invocation_factory(status="complete")
    mock_get_invocation = Mock()
    mock_api_clients.contract_invocations.get_contract_invocation = mock_get_invocation
    mock_get_invocation.return_value = complete_invocation._model

    contract_invocation.reload()

    mock_get_invocation.assert_called_once_with(
        wallet_id=contract_invocation.wallet_id,
        address_id=contract_invocation.address_id,
        contract_invocation_id=contract_invocation.contract_invocation_id,
    )
    assert contract_invocation.status.value == "complete"


@patch("cdp.Cdp.api_clients")
@patch("cdp.contract_invocation.time.sleep")
@patch("cdp.contract_invocation.time.time")
def test_wait_for_contract_invocation(
    mock_time, mock_sleep, mock_api_clients, contract_invocation_factory
):
    """Test the waiting for a ContractInvocation object to complete."""
    pending_invocation = contract_invocation_factory(status="pending")
    complete_invocation = contract_invocation_factory(status="complete")
    mock_get_invocation = Mock()
    mock_api_clients.contract_invocations.get_contract_invocation = mock_get_invocation
    mock_get_invocation.side_effect = [pending_invocation._model, complete_invocation._model]

    mock_time.side_effect = [0, 0.2, 0.4]

    result = pending_invocation.wait(interval_seconds=0.2, timeout_seconds=1)

    assert result.status.value == "complete"
    mock_get_invocation.assert_called_with(
        wallet_id=pending_invocation.wallet_id,
        address_id=pending_invocation.address_id,
        contract_invocation_id=pending_invocation.contract_invocation_id,
    )
    assert mock_get_invocation.call_count == 2
    mock_sleep.assert_has_calls([call(0.2)] * 2)
    assert mock_time.call_count == 3


@patch("cdp.Cdp.api_clients")
@patch("cdp.contract_invocation.time.sleep")
@patch("cdp.contract_invocation.time.time")
def test_wait_for_contract_invocation_timeout(
    mock_time, mock_sleep, mock_api_clients, contract_invocation_factory
):
    """Test the waiting for a ContractInvocation object to complete with a timeout."""
    pending_invocation = contract_invocation_factory(status="pending")
    mock_get_invocation = Mock(return_value=pending_invocation._model)
    mock_api_clients.contract_invocations.get_contract_invocation = mock_get_invocation

    mock_time.side_effect = [0, 0.5, 1.0, 1.5, 2.0, 2.5]

    with pytest.raises(TimeoutError, match="Contract Invocation timed out"):
        pending_invocation.wait(interval_seconds=0.5, timeout_seconds=2)

    assert mock_get_invocation.call_count == 5
    mock_sleep.assert_has_calls([call(0.5)] * 4)
    assert mock_time.call_count == 6


def test_sign_contract_invocation_invalid_key(contract_invocation_factory):
    """Test the signing of a ContractInvocation object with an invalid key."""
    contract_invocation = contract_invocation_factory()
    with pytest.raises(ValueError, match="key must be a LocalAccount"):
        contract_invocation.sign("invalid_key")


def test_contract_invocation_str_representation(contract_invocation_factory):
    """Test the string representation of a ContractInvocation object."""
    contract_invocation = contract_invocation_factory()
    expected_str = (
        f"ContractInvocation: (contract_invocation_id: {contract_invocation.contract_invocation_id}, "
        f"wallet_id: {contract_invocation.wallet_id}, address_id: {contract_invocation.address_id}, "
        f"network_id: {contract_invocation.network_id}, method: {contract_invocation.method}, "
        f"transaction_hash: {contract_invocation.transaction_hash}, transaction_link: {contract_invocation.transaction_link}, "
        f"status: {contract_invocation.status})"
    )
    assert str(contract_invocation) == expected_str


def test_contract_invocation_repr(contract_invocation_factory):
    """Test the representation of a ContractInvocation object."""
    contract_invocation = contract_invocation_factory()
    assert repr(contract_invocation) == str(contract_invocation)
