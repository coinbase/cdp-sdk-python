import pytest

from cdp.client.models.call import Call
from cdp.client.models.user_operation import UserOperation as UserOperationModel
from cdp.user_operation import UserOperation


@pytest.fixture
def user_operation_model_factory():
    """Create and return a factory for UserOperationModel fixtures."""

    def _create_user_operation_model(
        id="test-user-operation-id",
        network_id="base-sepolia",
        calls=None,
        unsigned_payload="0x" + "1" * 64,
        signature="0x3456789012345678901234567890123456789012",
        transaction_hash="0x4567890123456789012345678901234567890123",
        status="pending",
    ):
        if calls is None:
            calls = [
                Call(
                    to="0x1234567890123456789012345678901234567890",
                    value="1000000000000000000",
                    data="0x",
                )
            ]
        return UserOperationModel(
            id=id,
            network_id=network_id,
            calls=calls,
            unsigned_payload=unsigned_payload,
            signature=signature,
            transaction_hash=transaction_hash,
            status=status,
        )

    return _create_user_operation_model


@pytest.fixture
def user_operation_factory(user_operation_model_factory):
    """Create and return a factory for UserOperation fixtures."""

    def _create_user_operation(
        user_operation_id, network_id, calls, unsigned_payload, signature, transaction_hash, status
    ):
        user_operation_model = user_operation_model_factory(
            id=user_operation_id,
            network_id=network_id,
            calls=calls,
            unsigned_payload=unsigned_payload,
            signature=signature,
            transaction_hash=transaction_hash,
            status=status,
        )
        return UserOperation(
            user_operation_model.id,
            user_operation_model.network_id,
            user_operation_model.calls,
            user_operation_model.unsigned_payload,
            user_operation_model.signature,
            user_operation_model.transaction_hash,
            user_operation_model.status,
        )

    return _create_user_operation
