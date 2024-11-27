from unittest.mock import Mock, call, patch

import pytest

from cdp.faucet_transaction import FaucetTransaction


def test_faucet_tx_initialization(faucet_transaction_factory):
    """Test the initialization of a FaucetTransaction."""
    faucet_transaction = faucet_transaction_factory()

    assert isinstance(faucet_transaction, FaucetTransaction)
    assert faucet_transaction.transaction_hash == "0xtransactionhash"
    assert (
        faucet_transaction.transaction_link == "https://sepolia.basescan.org/tx/0xtransactionlink"
    )
    assert faucet_transaction.network_id == "base-sepolia"
    assert faucet_transaction.address_id == "0xdestination"
    assert faucet_transaction.status.value == "complete"


@patch("cdp.Cdp.api_clients")
def test_reload_faucet_tx(mock_api_clients, faucet_transaction_factory):
    """Test the reloading of a FaucetTransaction object."""
    faucet_tx = faucet_transaction_factory(status="broadcast")
    complete_faucet_tx = faucet_transaction_factory(status="complete")

    # Mock the GetFaucetTransaction API returning a complete faucet transaction.
    mock_get_faucet_tx = Mock()
    mock_get_faucet_tx.return_value = complete_faucet_tx._model
    mock_api_clients.external_addresses.get_faucet_transaction = mock_get_faucet_tx

    reloaded_faucet_tx = faucet_tx.reload()

    mock_get_faucet_tx.assert_called_once_with("base-sepolia", "0xdestination", "0xtransactionhash")
    assert faucet_tx.status.value == "complete"
    assert reloaded_faucet_tx.status.value == "complete"


@patch("cdp.Cdp.api_clients")
@patch("cdp.faucet_transaction.time.sleep")
@patch("cdp.faucet_transaction.time.time")
def test_wait_for_faucet_transaction(
    mock_time, mock_sleep, mock_api_clients, faucet_transaction_factory
):
    """Test the waiting for a FaucetTransaction object to complete."""
    faucet_tx = faucet_transaction_factory(status="broadcast")
    complete_faucet_tx = faucet_transaction_factory(status="complete")

    # Mock GetFaucetTransaction returning a `broadcast` and then a `complete`
    # faucet transaction.
    mock_get_faucet_tx = Mock()
    mock_api_clients.external_addresses.get_faucet_transaction = mock_get_faucet_tx
    mock_get_faucet_tx.side_effect = [faucet_tx._model, complete_faucet_tx._model]

    mock_time.side_effect = [0, 0.2, 0.4]

    result = faucet_tx.wait(interval_seconds=0.2, timeout_seconds=1)

    assert result.status.value == "complete"

    mock_get_faucet_tx.assert_called_with("base-sepolia", "0xdestination", "0xtransactionhash")
    assert mock_get_faucet_tx.call_count == 2
    mock_sleep.assert_has_calls([call(0.2)] * 2)
    assert mock_time.call_count == 3


@patch("cdp.Cdp.api_clients")
@patch("cdp.faucet_transaction.time.sleep")
@patch("cdp.faucet_transaction.time.time")
def test_wait_for_faucet_transaction_timeout(
    mock_time, mock_sleep, mock_api_clients, faucet_transaction_factory
):
    """Test the waiting for a FaucetTransaction object to complete with a timeout."""
    faucet_tx = faucet_transaction_factory(status="broadcast")

    mock_get_faucet_tx = Mock()
    mock_get_faucet_tx.return_value = faucet_tx._model
    mock_api_clients.external_addresses.get_faucet_transaction = mock_get_faucet_tx

    mock_time.side_effect = [0, 0.5, 1.0, 1.5, 2.0, 2.5]

    with pytest.raises(
        TimeoutError, match="Timed out waiting for FaucetTransaction to land onchain"
    ):
        faucet_tx.wait(interval_seconds=0.5, timeout_seconds=2)

    mock_get_faucet_tx.assert_called_with("base-sepolia", "0xdestination", "0xtransactionhash")

    assert mock_get_faucet_tx.call_count == 5
    mock_sleep.assert_has_calls([call(0.5)] * 4)
    assert mock_time.call_count == 6
