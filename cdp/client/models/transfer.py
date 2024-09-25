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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr, field_validator
from typing_extensions import Self

from cdp.client.models.asset import Asset
from cdp.client.models.sponsored_send import SponsoredSend
from cdp.client.models.transaction import Transaction


class Transfer(BaseModel):
    """A transfer of an asset from one address to another"""

    network_id: StrictStr = Field(description="The ID of the blockchain network")
    wallet_id: StrictStr = Field(description="The ID of the wallet that owns the from address")
    address_id: StrictStr = Field(description="The onchain address of the sender")
    destination: StrictStr = Field(description="The onchain address of the recipient")
    amount: StrictStr = Field(description="The amount in the atomic units of the asset")
    asset_id: StrictStr = Field(description="The ID of the asset being transferred")
    asset: Asset
    transfer_id: StrictStr = Field(description="The ID of the transfer")
    transaction: Transaction | None = None
    sponsored_send: SponsoredSend | None = None
    unsigned_payload: StrictStr | None = Field(
        default=None,
        description="The unsigned payload of the transfer. This is the payload that needs to be signed by the sender.",
    )
    signed_payload: StrictStr | None = Field(
        default=None,
        description="The signed payload of the transfer. This is the payload that has been signed by the sender.",
    )
    transaction_hash: StrictStr | None = Field(
        default=None, description="The hash of the transfer transaction"
    )
    status: StrictStr | None = Field(default=None, description="The status of the transfer")
    gasless: StrictBool = Field(description="Whether the transfer uses sponsored gas")
    __properties: ClassVar[list[str]] = [
        "network_id",
        "wallet_id",
        "address_id",
        "destination",
        "amount",
        "asset_id",
        "asset",
        "transfer_id",
        "transaction",
        "sponsored_send",
        "unsigned_payload",
        "signed_payload",
        "transaction_hash",
        "status",
        "gasless",
    ]

    @field_validator("status")
    def status_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(["pending", "broadcast", "complete", "failed"]):
            raise ValueError(
                "must be one of enum values ('pending', 'broadcast', 'complete', 'failed')"
            )
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
    def from_json(cls, json_str: str) -> Self | None:
        """Create an instance of Transfer from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of asset
        if self.asset:
            _dict["asset"] = self.asset.to_dict()
        # override the default output from pydantic by calling `to_dict()` of transaction
        if self.transaction:
            _dict["transaction"] = self.transaction.to_dict()
        # override the default output from pydantic by calling `to_dict()` of sponsored_send
        if self.sponsored_send:
            _dict["sponsored_send"] = self.sponsored_send.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: dict[str, Any] | None) -> Self | None:
        """Create an instance of Transfer from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "network_id": obj.get("network_id"),
                "wallet_id": obj.get("wallet_id"),
                "address_id": obj.get("address_id"),
                "destination": obj.get("destination"),
                "amount": obj.get("amount"),
                "asset_id": obj.get("asset_id"),
                "asset": Asset.from_dict(obj["asset"]) if obj.get("asset") is not None else None,
                "transfer_id": obj.get("transfer_id"),
                "transaction": Transaction.from_dict(obj["transaction"])
                if obj.get("transaction") is not None
                else None,
                "sponsored_send": SponsoredSend.from_dict(obj["sponsored_send"])
                if obj.get("sponsored_send") is not None
                else None,
                "unsigned_payload": obj.get("unsigned_payload"),
                "signed_payload": obj.get("signed_payload"),
                "transaction_hash": obj.get("transaction_hash"),
                "status": obj.get("status"),
                "gasless": obj.get("gasless"),
            }
        )
        return _obj