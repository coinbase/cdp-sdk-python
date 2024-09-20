import pytest

from cdp.client.models.transaction import Transaction as TransactionModel
from cdp.transaction import Transaction


@pytest.fixture
def transaction_model():
    """Create and return a fixture for a TransactionModel."""
    return TransactionModel(
        network_id="base-sepolia",
        transaction_hash="0xtransactionhash",
        from_address_id="0xfromaddressid",
        to_address_id="0xtoaddressid",
        unsigned_payload="0xunsignedpayload",
        signed_payload="0xsignedpayload",
        status="complete",
        block_hash="0xblockhash",
        block_height="123456",
        transaction_link="https://basescan.org/tx/0xtransactionlink",
    )


@pytest.fixture
def unsigned_transaction_model():
    """Create and return a fixture for an unsigned TransactionModel."""
    return TransactionModel(
        network_id="base-sepolia",
        from_address_id="0xfromaddressid",
        to_address_id="0xtoaddressid",
        unsigned_payload="0xunsignedpayload",
        status="pending",
    )


@pytest.fixture
def transaction(transaction_model):
    """Create and return a fixture for a Transaction."""
    return Transaction(transaction_model)


@pytest.fixture
def unsigned_transaction(unsigned_transaction_model):
    """Create and return a fixture for an unsigned Transaction."""
    return Transaction(unsigned_transaction_model)


def test_transaction_initialization(transaction):
    """Test transaction initialization."""
    assert isinstance(transaction._model, TransactionModel)
    assert transaction._raw is None
    assert transaction._signature == "0xsignedpayload"


def test_transaction_initialization_invalid_model():
    """Test transaction initialization with an invalid model."""
    with pytest.raises(TypeError, match="model must be of type TransactionModel"):
        Transaction("invalid_model")


def test_unsigned_payload(transaction):
    """Test unsigned payload."""
    assert transaction.unsigned_payload == "0xunsignedpayload"


def test_signed_payload(transaction):
    """Test signed payload."""
    assert transaction.signed_payload == "0xsignedpayload"


def test_transaction_hash(transaction):
    """Test transaction hash."""
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
def test_status(transaction, status, expected_status):
    """Test transaction status."""
    transaction._model.status = status
    assert transaction.status == expected_status


def test_from_address_id(transaction):
    """Test from address ID."""
    assert transaction.from_address_id == "0xfromaddressid"


def test_to_address_id(transaction):
    """Test to address ID."""
    assert transaction.to_address_id == "0xtoaddressid"


def test_terminal_state(unsigned_transaction, transaction):
    """Test terminal state."""
    assert not unsigned_transaction.terminal_state
    assert transaction.terminal_state


def test_block_hash(transaction):
    """Test block hash."""
    assert transaction.block_hash == "0xblockhash"


def test_block_height(transaction):
    """Test block height."""
    assert transaction.block_height == "123456"


def test_transaction_link(transaction):
    """Test transaction link."""
    assert transaction.transaction_link == "https://basescan.org/tx/0xtransactionlink"


def test_signed(unsigned_transaction, transaction):
    """Test signed."""
    assert not unsigned_transaction.signed
    assert transaction.signed


def test_signature(transaction):
    """Test signature."""
    assert transaction.signature == "0xsignedpayload"


def test_signature_not_signed(unsigned_transaction):
    """Test signature not signed."""
    with pytest.raises(ValueError, match="Transaction is not signed"):
        unsigned_transaction.signature  # noqa: B018


def test_str_representation(transaction):
    """Test string representation."""
    expected_str = "Transaction: (transaction_hash: 0xtransactionhash, status: complete)"
    assert str(transaction) == expected_str


def test_repr(transaction):
    """Test repr."""
    expected_repr = "Transaction: (transaction_hash: 0xtransactionhash, status: complete)"
    assert repr(transaction) == expected_repr
