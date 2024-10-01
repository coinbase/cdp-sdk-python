import pytest

from cdp.client.models.contract_invocation import ContractInvocation as ContractInvocationModel
from cdp.contract_invocation import ContractInvocation


@pytest.fixture
def contract_invocation_model_factory(transaction_model_factory):
    """Create and return a factory for creating ContractInvocationModel fixtures."""

    def _create_contract_invocation_model(status="complete"):
        return ContractInvocationModel(
            network_id="base-sepolia",
            wallet_id="test-wallet-id",
            address_id="0xaddressid",
            contract_invocation_id="test-invocation-id",
            contract_address="0xcontractaddress",
            method="testMethod",
            args='{"arg1": "value1"}',
            abi='{"abi": "data"}',
            amount="1",
            transaction=transaction_model_factory(status),
        )

    return _create_contract_invocation_model


@pytest.fixture
def contract_invocation_factory(contract_invocation_model_factory):
    """Create and return a factory for creating ContractInvocation fixtures."""

    def _create_contract_invocation(status="complete"):
        contract_invocation_model = contract_invocation_model_factory(status)
        return ContractInvocation(contract_invocation_model)

    return _create_contract_invocation
