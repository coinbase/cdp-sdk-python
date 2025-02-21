from unittest.mock import Mock, call, patch

import pytest

from cdp.client.models.broadcast_user_operation_request import BroadcastUserOperationRequest
from cdp.client.models.call import Call
from cdp.client.models.create_user_operation_request import CreateUserOperationRequest
from cdp.user_operation import UserOperation


def test_user_operation_properties(user_operation_model_factory):
    """Test the properties of a UserOperation object."""
    call = Call(to="0x1234567890123456789012345678901234567890", data="0xdata", value="0")

    model = user_operation_model_factory(
        "test-user-operation-id",
        "base-sepolia",
        [call],
        "0x" + "1" * 64,
        None,
        "0x4567890123456789012345678901234567890123",
        "pending",
    )
    user_operation = UserOperation(model, "0x1234567890123456789012345678901234567890")
    assert user_operation.smart_wallet_address == "0x1234567890123456789012345678901234567890"
    assert user_operation.user_op_hash == model.user_op_hash
    assert user_operation.status == UserOperation.Status.PENDING
    assert user_operation.signature is None
    assert user_operation.transaction_hash == model.transaction_hash


@patch("cdp.Cdp.api_clients")
def test_create_user_operation(mock_api_clients, user_operation_model_factory):
    """Test the creation of a UserOperation object."""
    model = user_operation_model_factory()
    mock_create_operation = Mock()
    mock_create_operation.return_value = model
    mock_api_clients.smart_wallets.create_user_operation = mock_create_operation

    call = Call(to="0x1234567890123456789012345678901234567890", data="0xdata", value="0")
    calls = [call]

    user_operation = UserOperation.create(
        smart_wallet_address="0xsmartwallet",
        network_id="base-sepolia",
        calls=calls,
        paymaster_url="https://paymaster.example.com",
    )

    assert isinstance(user_operation, UserOperation)

    # Verify the create operation was called with correct arguments
    mock_create_operation.assert_called_once()
    args = mock_create_operation.call_args.args

    assert args[0] == "0xsmartwallet"  # smart_wallet_address
    assert args[1] == "base-sepolia"  # network_id

    # Verify the CreateUserOperationRequest object
    request = args[2]
    assert isinstance(request, CreateUserOperationRequest)
    assert request.calls == calls
    assert request.paymaster_url == "https://paymaster.example.com"


def test_sign_user_operation(user_operation_model_factory, account_factory):
    """Test signing a UserOperation object."""
    model = user_operation_model_factory(signature=None)
    user_operation = UserOperation(model, "0xsmartwallet")
    account = account_factory()

    result = user_operation.sign(account)

    assert isinstance(result, UserOperation)
    assert result.signature is not None
    assert result.signature.startswith("0x")
    # Verify the signature length (0x + 130 hex characters for r, s, v)
    assert len(result.signature) == 132


@patch("cdp.Cdp.api_clients")
def test_broadcast_user_operation(mock_api_clients, user_operation_model_factory):
    """Test broadcasting a UserOperation object."""
    initial_model = user_operation_model_factory(status="signed")
    initial_operation = UserOperation(initial_model, "0xsmartwallet")
    initial_operation._signature = "0xsignature"

    broadcast_model = user_operation_model_factory(status="broadcast")
    mock_broadcast = Mock(return_value=broadcast_model)
    mock_api_clients.smart_wallets.broadcast_user_operation = mock_broadcast

    result = initial_operation.broadcast()

    assert isinstance(result, UserOperation)
    assert result.status == UserOperation.Status.BROADCAST
    mock_broadcast.assert_called_once_with(
        smart_wallet_address=initial_operation.smart_wallet_address,
        user_op_hash=initial_operation.user_op_hash,
        broadcast_user_operation_request=BroadcastUserOperationRequest(signature="0xsignature"),
    )


@patch("cdp.Cdp.api_clients")
def test_reload_user_operation(mock_api_clients, user_operation_model_factory):
    """Test reloading a UserOperation object."""
    pending_model = user_operation_model_factory(status="pending")
    complete_model = user_operation_model_factory(status="complete")
    pending_operation = UserOperation(pending_model, "0xsmartwallet")

    mock_get_operation = Mock(return_value=complete_model)
    mock_api_clients.smart_wallets.get_user_operation = mock_get_operation

    pending_operation.reload()

    mock_get_operation.assert_called_once_with(
        smart_wallet_address=pending_operation.smart_wallet_address,
        user_op_hash=pending_operation.user_op_hash,
    )
    assert pending_operation.status == UserOperation.Status.COMPLETE


@patch("cdp.Cdp.api_clients")
@patch("cdp.user_operation.time.sleep")
@patch("cdp.user_operation.time.time")
def test_wait_for_user_operation(
    mock_time, mock_sleep, mock_api_clients, user_operation_model_factory
):
    """Test waiting for a UserOperation object to complete."""
    pending_model = user_operation_model_factory(status="pending")
    complete_model = user_operation_model_factory(status="complete")
    pending_operation = UserOperation(pending_model, "0xsmartwallet")

    mock_get_operation = Mock()
    mock_api_clients.smart_wallets.get_user_operation = mock_get_operation
    mock_get_operation.side_effect = [pending_model, complete_model]

    mock_time.side_effect = [0, 0.2, 0.4]

    result = pending_operation.wait(interval_seconds=0.2, timeout_seconds=1)

    assert result.status == UserOperation.Status.COMPLETE
    mock_get_operation.assert_called_with(
        smart_wallet_address=pending_operation.smart_wallet_address,
        user_op_hash=pending_operation.user_op_hash,
    )
    assert mock_get_operation.call_count == 2
    mock_sleep.assert_has_calls([call(0.2)] * 2)
    assert mock_time.call_count == 3


@patch("cdp.Cdp.api_clients")
@patch("cdp.user_operation.time.sleep")
@patch("cdp.user_operation.time.time")
def test_wait_for_user_operation_timeout(
    mock_time, mock_sleep, mock_api_clients, user_operation_model_factory
):
    """Test waiting for a UserOperation object to complete with a timeout."""
    pending_model = user_operation_model_factory(status="pending")
    pending_operation = UserOperation(pending_model, "0xsmartwallet")

    mock_get_operation = Mock(return_value=pending_model)
    mock_api_clients.smart_wallets.get_user_operation = mock_get_operation

    mock_time.side_effect = [0, 0.5, 1.0, 1.5, 2.0, 2.5]

    with pytest.raises(TimeoutError, match="User Operation timed out"):
        pending_operation.wait(interval_seconds=0.5, timeout_seconds=2)

    assert mock_get_operation.call_count == 5
    mock_sleep.assert_has_calls([call(0.5)] * 4)
    assert mock_time.call_count == 6


def test_terminal_states():
    """Test the terminal states of UserOperation Status."""
    assert UserOperation.Status.terminal_states() == [
        UserOperation.Status.COMPLETE,
        UserOperation.Status.FAILED,
    ]


def test_status_string_representation():
    """Test the string representation of UserOperation Status."""
    assert str(UserOperation.Status.PENDING) == "pending"
    assert repr(UserOperation.Status.PENDING) == "pending"


def test_user_operation_str_representation(user_operation_model_factory):
    """Test the string representation of a UserOperation object."""
    model = user_operation_model_factory()
    user_operation = UserOperation(model, "0xsmartwallet")
    expected_str = (
        f"UserOperation: (user_op_hash: {user_operation.user_op_hash}, "
        f"status: {user_operation.status})"
    )
    assert str(user_operation) == expected_str


def test_user_operation_repr(user_operation_model_factory):
    """Test the representation of a UserOperation object."""
    model = user_operation_model_factory()
    user_operation = UserOperation(model, "0xsmartwallet")
    assert repr(user_operation) == str(user_operation)
