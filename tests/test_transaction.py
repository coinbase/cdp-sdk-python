from unittest.mock import Mock, patch

import pytest

from cdp.client.exceptions import ApiException
from cdp.client.models.transaction import Transaction as TransactionModel
from cdp.errors import ApiError
from cdp.transaction import Transaction


def test_transaction_initialization(transaction_factory):
    """Test transaction initialization."""
    transaction = transaction_factory()

    assert isinstance(transaction, Transaction)
    assert isinstance(transaction._model, TransactionModel)
    assert transaction._raw is None
    assert transaction._signature == "0xsignedpayload"


def test_transaction_initialization_invalid_model():
    """Test transaction initialization with an invalid model."""
    with pytest.raises(TypeError, match="model must be of type TransactionModel"):
        Transaction("invalid_model")


def test_unsigned_payload(transaction_factory):
    """Test unsigned payload."""
    transaction = transaction_factory()

    assert transaction.unsigned_payload == "0xunsignedpayload"


def test_signed_payload(transaction_factory):
    """Test signed payload."""
    transaction = transaction_factory()

    assert transaction.signed_payload == "0xsignedpayload"


def test_transaction_hash(transaction_factory):
    """Test transaction hash."""
    transaction = transaction_factory()

    assert transaction.transaction_hash == "0xtransactionhash"


@pytest.mark.parametrize(
    "status, expected_status",
    [
        ("pending", Transaction.Status.PENDING),
        ("signed", Transaction.Status.SIGNED),
        ("broadcast", Transaction.Status.BROADCAST),
        ("complete", Transaction.Status.COMPLETE),
        ("failed", Transaction.Status.FAILED),
        ("unspecified", Transaction.Status.UNSPECIFIED),
    ],
)
def test_status(transaction_factory, status, expected_status):
    """Test transaction status."""
    transaction = transaction_factory()

    transaction._model.status = status
    assert transaction.status == expected_status


def test_from_address_id(transaction_factory):
    """Test from address ID."""
    transaction = transaction_factory()

    assert transaction.from_address_id == "0xaddressid"


def test_to_address_id(transaction_factory):
    """Test to address ID."""
    transaction = transaction_factory()

    assert transaction.to_address_id == "0xdestination"


def test_terminal_state(transaction_factory):
    """Test terminal state."""
    unsigned_transaction = transaction_factory("pending")
    transaction = transaction_factory()

    assert not unsigned_transaction.terminal_state
    assert transaction.terminal_state


def test_block_hash(transaction_factory):
    """Test block hash."""
    transaction = transaction_factory()

    assert transaction.block_hash == "0xblockhash"


def test_block_height(transaction_factory):
    """Test block height."""
    transaction = transaction_factory()

    assert transaction.block_height == "123456"


def test_transaction_link(transaction_factory):
    """Test transaction link."""
    transaction = transaction_factory()

    assert transaction.transaction_link == "https://sepolia.basescan.org/tx/0xtransactionlink"


def test_signed(transaction_factory):
    """Test signed."""
    unsigned_transaction = transaction_factory("pending")
    transaction = transaction_factory()

    assert not unsigned_transaction.signed
    assert transaction.signed


def test_signature(transaction_factory):
    """Test signature."""
    transaction = transaction_factory()

    assert transaction.signature == "0xsignedpayload"


def test_signature_not_signed(transaction_factory):
    """Test signature not signed."""
    unsigned_transaction = transaction_factory("pending")

    with pytest.raises(ValueError, match="Transaction is not signed"):
        unsigned_transaction.signature  # noqa: B018


def test_str_representation(transaction_factory):
    """Test string representation."""
    transaction = transaction_factory()

    expected_str = "Transaction: (transaction_hash: 0xtransactionhash, status: complete)"
    assert str(transaction) == expected_str


def test_repr(transaction_factory):
    """Test repr."""
    transaction = transaction_factory()

    expected_repr = "Transaction: (transaction_hash: 0xtransactionhash, status: complete)"
    assert repr(transaction) == expected_repr


@patch("cdp.Cdp.api_clients")
def test_list_transactions(mock_api_clients, transaction_model_factory):
    """Test the listing of transactions."""
    mock_list_transactions = Mock()
    mock_list_transactions.return_value = Mock(data=[transaction_model_factory()], has_more=False)
    mock_api_clients.transaction_history.list_address_transactions = mock_list_transactions

    transactions = Transaction.list(network_id="test-network-id", address_id="0xaddressid")

    assert len(list(transactions)) == 1
    assert all(isinstance(t, Transaction) for t in transactions)
    mock_list_transactions.assert_called_once_with(
        network_id="test-network-id", address_id="0xaddressid", limit=1, page=None
    )


@patch("cdp.Cdp.api_clients")
def test_list_transactions_error(mock_api_clients):
    """Test the listing of transactions getting api error."""
    mock_list_transactions = Mock()
    err = ApiException(500, "boom")
    mock_list_transactions.side_effect = ApiError(err, code="boom", message="boom")
    mock_api_clients.transaction_history.list_address_transactions = mock_list_transactions

    with pytest.raises(ApiError):
        transactions = Transaction.list(network_id="test-network-id", address_id="0xaddressid")
        next(transactions)
