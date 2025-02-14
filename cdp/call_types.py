from typing import Any, Dict, List, NotRequired, TypedDict, Union
from web3.types import Wei, HexStr, Address

class CallDict(TypedDict):
    """Represents a basic call to a smart contract."""
    to: Address
    value: NotRequired[Wei]
    data: NotRequired[HexStr]

class ABICallDict(TypedDict):
    """Represents a call to a smart contract using ABI encoding."""
    to: Address
    value: NotRequired[Wei]
    abi: List[Dict[str, Any]]
    function_name: str
    args: List[Any]

Call = Union[CallDict, ABICallDict]