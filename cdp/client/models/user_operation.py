# coding: utf-8

"""
    Coinbase Platform API

    This is the OpenAPI 3.0 specification for the Coinbase Platform APIs, used in conjunction with the Coinbase Platform SDKs.

    The version of the OpenAPI document: 0.0.1-alpha
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from cdp.client.models.call import Call
from typing import Optional, Set
from typing_extensions import Self

class UserOperation(BaseModel):
    """
    UserOperation
    """ # noqa: E501
    id: StrictStr = Field(description="The ID of the user operation.")
    network_id: StrictStr = Field(description="The ID of the network the user operation is being created on.")
    calls: List[Call] = Field(description="The list of calls to make from the smart wallet.")
    user_op_hash: StrictStr = Field(description="The unique identifier for the user operation onchain. This is the payload that must be signed by one of the owners of the smart wallet to send the user operation.")
    unsigned_payload: StrictStr = Field(description="The hex-encoded hash that must be signed by the user.")
    signature: Optional[StrictStr] = Field(default=None, description="The hex-encoded signature of the user operation.")
    transaction_hash: Optional[StrictStr] = Field(default=None, description="The hash of the transaction that was broadcast.")
    status: StrictStr = Field(description="The status of the user operation.")
    __properties: ClassVar[List[str]] = ["id", "network_id", "calls", "user_op_hash", "unsigned_payload", "signature", "transaction_hash", "status"]

    @field_validator('status')
    def status_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['pending', 'signed', 'broadcast', 'complete', 'failed']):
            raise ValueError("must be one of enum values ('pending', 'signed', 'broadcast', 'complete', 'failed')")
        return value

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
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of UserOperation from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of each item in calls (list)
        _items = []
        if self.calls:
            for _item_calls in self.calls:
                if _item_calls:
                    _items.append(_item_calls.to_dict())
            _dict['calls'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of UserOperation from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "network_id": obj.get("network_id"),
            "calls": [Call.from_dict(_item) for _item in obj["calls"]] if obj.get("calls") is not None else None,
            "user_op_hash": obj.get("user_op_hash"),
            "unsigned_payload": obj.get("unsigned_payload"),
            "signature": obj.get("signature"),
            "transaction_hash": obj.get("transaction_hash"),
            "status": obj.get("status")
        })
        return _obj


