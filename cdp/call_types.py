from typing import Any, NotRequired, TypedDict, Union

from web3.types import Address, HexStr, Wei


class CallDict(TypedDict):
    """Represents a basic call to a smart contract."""

    to: Address
    value: NotRequired[Wei]
    data: NotRequired[HexStr]


class ABICallDict(TypedDict):
    """Represents a call to a smart contract using ABI encoding."""

    to: Address
    value: NotRequired[Wei]
    abi: list[dict[str, Any]]
    function_name: str
    args: list[Any]


Call = CallDict | ABICallDict
