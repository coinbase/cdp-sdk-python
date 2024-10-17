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


@pytest.fixture
def all_read_types_abi():
    return [
        {
            "type": "function",
            "name": "exampleFunction",
            "inputs": [
                {
                    "name": "z",
                    "type": "uint256",
                    "internalType": "uint256",
                },
            ],
            "outputs": [
                {
                    "name": "",
                    "type": "bool",
                    "internalType": "bool",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureAddress",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "address",
                    "internalType": "address",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureArray",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "uint256[]",
                    "internalType": "uint256[]",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBool",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bool",
                    "internalType": "bool",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureFunctionSelector",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes4",
                    "internalType": "bytes4",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureInt128",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "int128",
                    "internalType": "int128",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureInt16",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "int16",
                    "internalType": "int16",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureInt256",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "int256",
                    "internalType": "int256",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureInt32",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "int32",
                    "internalType": "int32",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureInt64",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "int64",
                    "internalType": "int64",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureInt8",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "int8",
                    "internalType": "int8",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureNestedStruct",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "tuple",
                    "internalType": "struct TestAllReadTypes.ExampleStruct",
                    "components": [
                        {
                            "name": "a",
                            "type": "uint256",
                            "internalType": "uint256",
                        },
                        {
                            "name": "nestedFields",
                            "type": "tuple",
                            "internalType": "struct TestAllReadTypes.NestedData",
                            "components": [
                                {
                                    "name": "nestedArray",
                                    "type": "tuple",
                                    "internalType": "struct TestAllReadTypes.ArrayData",
                                    "components": [
                                        {
                                            "name": "a",
                                            "type": "uint256[]",
                                            "internalType": "uint256[]",
                                        },
                                    ],
                                },
                                {
                                    "name": "a",
                                    "type": "uint256",
                                    "internalType": "uint256",
                                },
                            ],
                        },
                    ],
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureString",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "string",
                    "internalType": "string",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureTuple",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "uint256",
                    "internalType": "uint256",
                },
                {
                    "name": "",
                    "type": "uint256",
                    "internalType": "uint256",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureTupleMixedTypes",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "uint256",
                    "internalType": "uint256",
                },
                {
                    "name": "",
                    "type": "address",
                    "internalType": "address",
                },
                {
                    "name": "",
                    "type": "bool",
                    "internalType": "bool",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureUint128",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "uint128",
                    "internalType": "uint128",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureUint16",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "uint16",
                    "internalType": "uint16",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureUint256",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "uint256",
                    "internalType": "uint256",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureUint32",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "uint32",
                    "internalType": "uint32",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureUint64",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "uint64",
                    "internalType": "uint64",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureUint8",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "uint8",
                    "internalType": "uint8",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "returnFunction",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "function",
                    "internalType": "function (uint256) external returns (bool)",
                },
            ],
            "stateMutability": "view",
        },
        {
            "type": "function",
            "name": "viewUint",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "uint256",
                    "internalType": "uint256",
                },
            ],
            "stateMutability": "view",
        },
        {
            "type": "function",
            "name": "x",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "uint256",
                    "internalType": "uint256",
                },
            ],
            "stateMutability": "view",
        },
        {
            "type": "function",
            "name": "pureBytes",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes",
                    "internalType": "bytes",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes1",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes1",
                    "internalType": "bytes1",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes2",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes2",
                    "internalType": "bytes2",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes3",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes3",
                    "internalType": "bytes3",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes4",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes4",
                    "internalType": "bytes4",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes5",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes5",
                    "internalType": "bytes5",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes6",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes6",
                    "internalType": "bytes6",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes7",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes7",
                    "internalType": "bytes7",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes8",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes8",
                    "internalType": "bytes8",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes9",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes9",
                    "internalType": "bytes9",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes10",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes10",
                    "internalType": "bytes10",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes11",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes11",
                    "internalType": "bytes11",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes12",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes12",
                    "internalType": "bytes12",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes13",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes13",
                    "internalType": "bytes13",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes14",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes14",
                    "internalType": "bytes14",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes15",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes15",
                    "internalType": "bytes15",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes16",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes16",
                    "internalType": "bytes16",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes17",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes17",
                    "internalType": "bytes17",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes18",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes18",
                    "internalType": "bytes18",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes19",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes19",
                    "internalType": "bytes19",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes20",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes20",
                    "internalType": "bytes20",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes21",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes21",
                    "internalType": "bytes21",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes22",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes22",
                    "internalType": "bytes22",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes23",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes23",
                    "internalType": "bytes23",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes24",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes24",
                    "internalType": "bytes24",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes25",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes25",
                    "internalType": "bytes25",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes26",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes26",
                    "internalType": "bytes26",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes27",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes27",
                    "internalType": "bytes27",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes28",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes28",
                    "internalType": "bytes28",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes29",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes29",
                    "internalType": "bytes29",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes30",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes30",
                    "internalType": "bytes30",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes31",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes31",
                    "internalType": "bytes31",
                },
            ],
            "stateMutability": "pure",
        },
        {
            "type": "function",
            "name": "pureBytes32",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes32",
                    "internalType": "bytes32",
                },
            ],
            "stateMutability": "pure",
        },
    ]
