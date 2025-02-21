import pytest
from web3.types import Wei

from cdp.evm_call_types import ContractCall, EncodedCall, FunctionCall


def test_evm_call_dict_valid():
    """Test that the EVMCallDict is valid."""
    call = EncodedCall(to="0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
    assert isinstance(call.to, str)
    assert call.value is None
    assert call.data is None

    call = EncodedCall(
        to="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        value=Wei(1000000000000000000),
        data="0x095ea7b30000000000000000000000742d35cc6634c0532925a3b844bc454e4438f44e",
    )
    assert isinstance(call.to, str)
    assert call.value == 1000000000000000000
    assert isinstance(call.data, str)


def test_evm_abi_call_dict_valid():
    """Test that the EVMAbiCallDict is valid."""
    call = FunctionCall(
        to="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        abi=[
            {
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"type": "uint256"}],
                "stateMutability": "view",
                "type": "function",
            }
        ],
        function_name="totalSupply",
        args=[],
    )
    assert isinstance(call.to, str)
    assert call.value is None
    assert isinstance(call.abi, list)
    assert call.function_name == "totalSupply"
    assert call.args == []

    call = FunctionCall(
        to="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        value=Wei(1000000000000000000),
        abi=[
            {
                "inputs": [
                    {"name": "spender", "type": "address"},
                    {"name": "amount", "type": "uint256"},
                ],
                "name": "approve",
                "outputs": [{"type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function",
            }
        ],
        function_name="approve",
        args=["0x742d35Cc6634C0532925a3b844Bc454e4438f44e", 1000000],
    )
    assert isinstance(call.to, str)
    assert call.value == 1000000000000000000
    assert isinstance(call.abi, list)
    assert call.function_name == "approve"
    assert len(call.args) == 2


def test_evm_abi_call_dict_invalid():
    """Test that the EVMAbiCallDict is invalid."""
    with pytest.raises(ValueError):
        FunctionCall(to="0x742d35Cc6634C0532925a3b844Bc454e4438f44e", function_name="test", args=[])


def test_evm_call_union():
    """Test that the EVMCall union is valid."""
    call_dict = EncodedCall(to="0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
    abi_call_dict = FunctionCall(
        to="0x742d35Cc6634C0532925a3b844Bc454e4438f44e", abi=[], function_name="test", args=[]
    )

    call: ContractCall = call_dict
    assert isinstance(call, EncodedCall)

    call = abi_call_dict
    assert isinstance(call, FunctionCall)
