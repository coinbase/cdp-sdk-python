import pytest

from cdp.client.models.compiled_smart_contract import (
    CompiledSmartContract as CompiledSmartContractModel,
)


@pytest.fixture
def compiled_smart_contract_model_factory():
    """Create and return a factory for creating CompiledSmartContractModel fixtures."""

    def _create_compiled_smart_contract_model():
        return CompiledSmartContractModel(
            compiled_smart_contract_id="test-compiled-smart-contract-id",
            contract_name="TestContract",
            abi='{"abi":"data"}',
            solidity_version="0.8.28+commit.7893614a",
            solidity_input_json='{"abi":"data"}',
        )

    return _create_compiled_smart_contract_model
