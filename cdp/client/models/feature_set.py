"""Coinbase Platform API

This is the OpenAPI 3.0 specification for the Coinbase Platform APIs, used in conjunction with the Coinbase Platform SDKs.

The version of the OpenAPI document: 0.0.1-alpha
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""

from __future__ import annotations

import json
import pprint
import re  # noqa: F401
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, StrictBool
from typing_extensions import Self


class FeatureSet(BaseModel):
    """FeatureSet"""

    faucet: StrictBool = Field(description="Whether the network supports a faucet")
    server_signer: StrictBool = Field(description="Whether the network supports Server-Signers")
    transfer: StrictBool = Field(description="Whether the network supports transfers")
    trade: StrictBool = Field(description="Whether the network supports trading")
    stake: StrictBool = Field(description="Whether the network supports staking")
    gasless_send: StrictBool = Field(description="Whether the network supports gasless sends")
    __properties: ClassVar[list[str]] = [
        "faucet",
        "server_signer",
        "transfer",
        "trade",
        "stake",
        "gasless_send",
    ]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Self | None:
        """Create an instance of FeatureSet from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: set[str] = set([])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        return _dict

    @classmethod
    def from_dict(cls, obj: dict[str, Any] | None) -> Self | None:
        """Create an instance of FeatureSet from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "faucet": obj.get("faucet"),
                "server_signer": obj.get("server_signer"),
                "transfer": obj.get("transfer"),
                "trade": obj.get("trade"),
                "stake": obj.get("stake"),
                "gasless_send": obj.get("gasless_send"),
            }
        )
        return _obj