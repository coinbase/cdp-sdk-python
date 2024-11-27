from decimal import Decimal
from unittest.mock import ANY, Mock, call, patch

import pytest
from eth_account.signers.local import LocalAccount

from cdp.asset import Asset
from cdp.errors import TransactionNotSignedError
from cdp.sponsored_send import SponsoredSend
from cdp.transaction import Transaction
from cdp.transfer import Transfer


@pytest.mark.parametrize("gasless", [True, False])
def test_transfer_initialization(transfer_factory, gasless):
    """Test the initialization of a Transfer object."""
    transfer = transfer_factory(gasless=gasless)
    assert isinstance(transfer, Transfer)
    if gasless:
        assert isinstance(transfer.send_tx_delegate, SponsoredSend)
    else:
        assert isinstance(transfer.send_tx_delegate, Transaction)


@pytest.mark.parametrize("gasless", [True, False])
def test_transfer_properties(transfer_factory, gasless):
    """Test the properties of a Transfer object."""
    transfer = transfer_factory(gasless=gasless)
    assert transfer.transfer_id == "test-transfer-id"
    assert transfer.wallet_id == "test-wallet-id"
    assert transfer.from_address_id == "0xaddressid"
    assert transfer.destination_address_id == "0xdestination"
    assert transfer.network_id == "base-sepolia"
    assert transfer.asset_id == "usdc"
    assert transfer.amount == Decimal("1")
    assert transfer.transaction_link == "https://sepolia.basescan.org/tx/0xtransactionlink"
    assert transfer.transaction_hash == "0xtransactionhash"
    assert transfer.status.value == "complete"
    assert isinstance(transfer.asset, Asset)
    assert transfer.terminal_state is True
    if gasless:
        assert isinstance(transfer.sponsored_send, SponsoredSend)
    else:
        assert isinstance(transfer.transaction, Transaction)


@patch("cdp.Cdp.api_clients")
@patch("cdp.transfer.Asset")
@pytest.mark.parametrize("gasless", [True, False])
def test_create_transfer(mock_asset, mock_api_clients, transfer_factory, asset_factory, gasless):
    """Test the creation of a Transfer object."""
    mock_fetch = Mock()
    mock_fetch.return_value = asset_factory()
    mock_asset.fetch = mock_fetch

    mock_primary_denomination = Mock()
    mock_primary_denomination.return_value = "usdc"
    mock_asset.primary_denomination = mock_primary_denomination

    mock_create_transfer = Mock()
    mock_create_transfer.return_value = transfer_factory(gasless=gasless)._model
    mock_api_clients.transfers.create_transfer = mock_create_transfer

    transfer = Transfer.create(
        address_id="0xaddressid",
        amount=Decimal("1"),
        asset_id="usdc",
        destination="0xdestination",
        network_id="base-sepolia",
        wallet_id="test-wallet-id",
        gasless=gasless,
    )

    assert isinstance(transfer, Transfer)
    mock_fetch.assert_called_once_with("base-sepolia", "usdc")
    mock_primary_denomination.assert_called_once_with("usdc")
    mock_create_transfer.assert_called_once_with(
        wallet_id="test-wallet-id", address_id="0xaddressid", create_transfer_request=ANY
    )

    create_transfer_request = mock_create_transfer.call_args[1]["create_transfer_request"]
    assert create_transfer_request.amount == "1000000"  # 1 USDC in atomic units
    assert create_transfer_request.asset_id == "usdc"
    assert create_transfer_request.destination == "0xdestination"
    assert create_transfer_request.network_id == "base-sepolia"
    assert create_transfer_request.gasless == gasless


@patch("cdp.Cdp.api_clients")
def test_list_transfers(mock_api_clients, transfer_factory):
    """Test the listing of transfers."""
    mock_list_transfers = Mock()
    mock_list_transfers.return_value = Mock(data=[transfer_factory()._model], has_more=False)
    mock_api_clients.transfers.list_transfers = mock_list_transfers
    transfers = Transfer.list("test-wallet-id", "0xaddressid")
    assert len(list(transfers)) == 1
    assert all(isinstance(t, Transfer) for t in transfers)
    mock_list_transfers.assert_called_once_with(
        wallet_id="test-wallet-id", address_id="0xaddressid", limit=100, page=None
    )


@patch.object(Transfer, "send_tx_delegate")
@pytest.mark.parametrize("gasless", [True, False])
def test_send_tx_delegate_sign(mock_send_tx_delegate, transfer_factory, gasless):
    """Test the signing of a Transfer object."""
    transfer = transfer_factory(gasless=gasless)
    mock_key = Mock(spec=LocalAccount)
    mock_send_tx_delegate.sign = Mock()

    signed_transfer = transfer.sign(mock_key)

    assert signed_transfer == transfer
    mock_send_tx_delegate.sign.assert_called_once_with(mock_key)


@pytest.mark.parametrize("gasless", [True, False])
def test_sign_transfer_invalid_key(transfer_factory, gasless):
    """Test the signing of a Transfer object with an invalid key."""
    transfer = transfer_factory(gasless=gasless)
    with pytest.raises(ValueError, match="key must be a LocalAccount"):
        transfer.sign("invalid_key")


@patch("cdp.transfer.Cdp.api_clients")
@pytest.mark.parametrize("gasless", [True, False])
def test_broadcast_transfer(mock_api_clients, transfer_factory, gasless):
    """Test the broadcasting of a Transfer object."""
    transfer = transfer_factory(gasless=gasless, status="signed")
    broadcast_transfer = transfer_factory(gasless=gasless, status="broadcast")
    mock_broadcast = Mock(return_value=broadcast_transfer._model)
    mock_api_clients.transfers.broadcast_transfer = mock_broadcast
    response = transfer.broadcast()
    mock_broadcast.assert_called_once_with(
        wallet_id=transfer.wallet_id,
        address_id=transfer.from_address_id,
        transfer_id=transfer.transfer_id,
        broadcast_transfer_request=ANY,
    )
    assert isinstance(response, Transfer)
    assert response.status.value == "submitted" if gasless else "broadcast"
    broadcast_transfer_request = mock_broadcast.call_args[1]["broadcast_transfer_request"]
    assert broadcast_transfer_request.signed_payload == transfer.send_tx_delegate.signature


@pytest.mark.parametrize("gasless", [True, False])
def test_broadcast_unsigned_transfer(transfer_factory, gasless):
    """Test the broadcasting of an unsigned Transfer object."""
    transfer = transfer_factory(gasless=gasless, status="pending")
    with pytest.raises(TransactionNotSignedError, match="Transfer is not signed"):
        transfer.broadcast()


@patch("cdp.Cdp.api_clients")
@pytest.mark.parametrize("gasless", [True, False])
def test_reload_transfer(mock_api_clients, transfer_factory, gasless):
    """Test the reloading of a Transfer object."""
    transfer = transfer_factory(gasless=gasless, status="pending")
    complete_transfer = transfer_factory(gasless=gasless, status="complete")
    mock_get_transfer = Mock()
    mock_api_clients.transfers.get_transfer = mock_get_transfer
    mock_get_transfer.return_value = complete_transfer._model
    transfer.reload()
    mock_get_transfer.assert_called_once_with(
        transfer.wallet_id, transfer.from_address_id, transfer.transfer_id
    )
    assert transfer.status.value == "complete"


@patch("cdp.Cdp.api_clients")
@patch("cdp.transfer.time.sleep")
@patch("cdp.transfer.time.time")
@pytest.mark.parametrize("gasless", [True, False])
def test_wait_for_transfer(mock_time, mock_sleep, mock_api_clients, transfer_factory, gasless):
    """Test the waiting for a Transfer object to complete."""
    pending_transfer = transfer_factory(gasless=gasless, status="pending")
    complete_transfer = transfer_factory(gasless=gasless, status="complete")
    mock_get_transfer = Mock()
    mock_api_clients.transfers.get_transfer = mock_get_transfer
    mock_get_transfer.side_effect = [pending_transfer._model, complete_transfer._model]

    mock_time.side_effect = [0, 0.2, 0.4]

    result = pending_transfer.wait(interval_seconds=0.2, timeout_seconds=1)

    assert result.status.value == "complete"
    mock_get_transfer.assert_called_with(
        pending_transfer.wallet_id, pending_transfer.from_address_id, pending_transfer.transfer_id
    )
    assert mock_get_transfer.call_count == 2
    mock_sleep.assert_has_calls([call(0.2)] * 2)
    assert mock_time.call_count == 3


@patch("cdp.Cdp.api_clients")
@patch("cdp.transfer.time.sleep")
@patch("cdp.transfer.time.time")
@pytest.mark.parametrize("gasless", [True, False])
def test_wait_for_transfer_timeout(
    mock_time, mock_sleep, mock_api_clients, transfer_factory, gasless
):
    """Test the waiting for a Transfer object to complete with a timeout."""
    pending_transfer = transfer_factory(gasless=gasless, status="pending")
    mock_get_transfer = Mock(return_value=pending_transfer._model)
    mock_api_clients.transfers.get_transfer = mock_get_transfer

    mock_time.side_effect = [0, 0.5, 1.0, 1.5, 2.0, 2.5]

    with pytest.raises(TimeoutError, match="Timed out waiting for Transfer to land onchain"):
        pending_transfer.wait(interval_seconds=0.5, timeout_seconds=2)

    assert mock_get_transfer.call_count == 5
    mock_sleep.assert_has_calls([call(0.5)] * 4)
    assert mock_time.call_count == 6


@pytest.mark.parametrize("gasless", [True, False])
def test_transfer_str_representation(transfer_factory, gasless):
    """Test the string representation of a Transfer object."""
    transfer = transfer_factory(gasless=gasless)
    expected_str = (
        f"Transfer: (transfer_id: {transfer.transfer_id}, network_id: {transfer.network_id}, "
        f"from_address_id: {transfer.from_address_id}, destination_address_id: {transfer.destination_address_id}, "
        f"asset_id: {transfer.asset_id}, amount: {transfer.amount}, transaction_link: {transfer.transaction_link}, "
        f"status: {transfer.status})"
    )
    assert str(transfer) == expected_str


@pytest.mark.parametrize("gasless", [True, False])
def test_transfer_repr(transfer_factory, gasless):
    """Test the representation of a Transfer object."""
    transfer = transfer_factory(gasless=gasless)
    assert repr(transfer) == str(transfer)
