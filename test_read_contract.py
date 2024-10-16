import asyncio
from decimal import Decimal
from cdp.smart_contract import SmartContract
from cdp.cdp import Cdp

# Configure Cdp (assuming it has a similar configuration method)
Cdp.configure_from_json(
    file_path="~/.apikeys/dev.json",
    base_path="http://localhost:8002",  # Adjust as needed
    debugging=False,
)

# ABI definition (simplified for brevity, add more as needed)
ABI = [
    {
        "type": "function",
        "name": "pureInt16",
        "inputs": [],
        "outputs": [{"name": "", "type": "int16"}],
        "stateMutability": "pure",
    },
    {
        "type": "function",
        "name": "pureUint16",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint16"}],
        "stateMutability": "pure",
    },
    {
        "type": "function",
        "name": "pureUint256",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "pure",
    },
    {
        "type": "function",
        "name": "pureBool",
        "inputs": [],
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "pure",
    },
    {
        "type": "function",
        "name": "pureAddress",
        "inputs": [],
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "pure",
    },
    {
        "type": "function",
        "name": "exampleFunction",
        "inputs": [{"name": "z", "type": "uint256"}],
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "pure",
    },
    {
        "type": "function",
        "name": "pureArray",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint256[]"}],
        "stateMutability": "pure",
    },
    {
        "type": "function",
        "name": "pureBytes12",
        "inputs": [],
        "outputs": [{"name": "", "type": "bytes12", "internalType": "bytes12"}],
        "stateMutability": "pure",
    },
    {
        "inputs": [],
        "stateMutability": "pure",
        "type": "function",
        "name": "pureBytes",
        "outputs": [{"internalType": "bytes", "name": "", "type": "bytes"}],
    },
    {
        "type": "function",
        "name": "pureNestedStruct",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "tuple",
                "components": [
                    {"name": "a", "type": "uint256"},
                    {
                        "name": "nestedFields",
                        "type": "tuple",
                        "components": [
                            {
                                "name": "nestedArray",
                                "type": "tuple",
                                "components": [{"name": "a", "type": "uint256[]"}],
                            },
                            {"name": "a", "type": "uint256"},
                        ],
                    },
                ],
            }
        ],
        "stateMutability": "pure",
    },
]

CONTRACT_ADDRESS = "0x0B54409D1B1dd1438eDF7729CDAea3E331Ae12ED"
NETWORK_ID = "base-sepolia"


async def main():
    # Test pureInt16
    int16 = SmartContract.read(
        NETWORK_ID,
        CONTRACT_ADDRESS,
        "pureInt16",
        ABI,
    )
    print("pureInt16:", int16)

    # Test pureUint16
    uint16 = SmartContract.read(
        NETWORK_ID,
        CONTRACT_ADDRESS,
        "pureUint16",
        ABI,
    )
    print("pureUint16:", uint16)

    # Test pureUint256
    uint256 = SmartContract.read(
        NETWORK_ID,
        CONTRACT_ADDRESS,
        "pureUint256",
        ABI,
    )
    print("pureUint256:", uint256)

    # Test pureBool
    bool_value = SmartContract.read(
        NETWORK_ID,
        CONTRACT_ADDRESS,
        "pureBool",
        ABI,
    )
    print("pureBool:", bool_value)

    # Test pureAddress
    address = SmartContract.read(
        NETWORK_ID,
        CONTRACT_ADDRESS,
        "pureAddress",
        ABI,
    )
    print("pureAddress:", address)

    # Test exampleFunction
    example_bool = SmartContract.read(
        NETWORK_ID, CONTRACT_ADDRESS, "exampleFunction", ABI, args={"z": str(1)}
    )
    print("exampleFunction:", example_bool)

    # Test pureArray
    array = SmartContract.read(
        NETWORK_ID,
        CONTRACT_ADDRESS,
        "pureArray",
        ABI,
    )
    print("pureArray:", array)

    # Test pureBytes12
    pure_bytes12 = SmartContract.read(
        NETWORK_ID,
        CONTRACT_ADDRESS,
        "pureBytes12",
        ABI,
    )
    print("pureBytes12:", pure_bytes12)

    # Test pureBytes
    pure_bytes = SmartContract.read(
        NETWORK_ID,
        CONTRACT_ADDRESS,
        "pureBytes",
        ABI,
    )
    print("pureBytes:", pure_bytes)

    # Test pureNestedStruct
    nested_struct = SmartContract.read(
        NETWORK_ID,
        CONTRACT_ADDRESS,
        "pureNestedStruct",
        ABI,
    )
    print("pureNestedStruct:", nested_struct)


if __name__ == "__main__":
    asyncio.run(main())
