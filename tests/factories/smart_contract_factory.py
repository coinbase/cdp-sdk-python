import pytest

from cdp.client.models.smart_contract import SmartContract as SmartContractModel
from cdp.client.models.smart_contract_options import SmartContractOptions
from cdp.client.models.token_contract_options import TokenContractOptions
from cdp.smart_contract import SmartContract


@pytest.fixture
def smart_contract_model_factory(transaction_model_factory):
    """Create and return a factory for creating SmartContractModel fixtures."""

    def _create_smart_contract_model(status="complete"):
        token_options = TokenContractOptions(name="TestToken", symbol="TT", total_supply="1000000")
        smart_contract_options = SmartContractOptions(actual_instance=token_options)

        return SmartContractModel(
            smart_contract_id="test-contract-id",
            network_id="base-sepolia",
            wallet_id="test-wallet-id",
            contract_address="0xcontractaddress",
            deployer_address="0xdeployeraddress",
            type="erc20",
            options=smart_contract_options,
            abi='{"abi": "data"}',
            transaction=transaction_model_factory(status),
        )

    return _create_smart_contract_model


@pytest.fixture
def smart_contract_factory(smart_contract_model_factory):
    """Create and return a factory for creating SmartContract fixtures."""

    def _create_smart_contract(status="complete"):
        smart_contract_model = smart_contract_model_factory(status)
        return SmartContract(smart_contract_model)

    return _create_smart_contract
