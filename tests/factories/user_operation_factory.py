import pytest

from cdp.client.models.call import Call
from cdp.client.models.user_operation import UserOperation as UserOperationModel


@pytest.fixture
def user_operation_model_factory():
    """Create and return a factory for UserOperationModel fixtures."""

    def _create_user_operation_model(
        id="test-user-operation-id",
        network_id="base-sepolia",
        calls=None,
        user_op_hash="0x" + "1" * 64,
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
            unsigned_payload=user_op_hash,
            user_op_hash=user_op_hash,
            signature=signature,
            transaction_hash=transaction_hash,
            status=status,
        )

    return _create_user_operation_model
