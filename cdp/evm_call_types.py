from typing import Any

from eth_typing import HexAddress
from pydantic import BaseModel
from web3.types import HexStr, Wei


class EVMCallDict(BaseModel):
    """Represents a basic call to a smart contract."""

    to: HexAddress
    value: Wei | None = None
    data: HexStr | None = None


class EVMAbiCallDict(BaseModel):
    """Represents a call to a smart contract using ABI encoding."""

    to: HexAddress
    value: Wei | None = None
    abi: list[dict[str, Any]]
    function_name: str
    args: list[Any]


EVMCall = EVMCallDict | EVMAbiCallDict
