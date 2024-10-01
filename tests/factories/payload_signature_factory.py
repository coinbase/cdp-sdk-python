import pytest

from cdp.client.models.payload_signature import PayloadSignature as PayloadSignatureModel
from cdp.payload_signature import PayloadSignature


@pytest.fixture
def payload_signature_model_factory():
    """Create and return a factory for creating PayloadSignatureModel fixtures."""

    def _create_payload_signature_model(status="signed"):
        payload_signature_model = PayloadSignatureModel(
            payload_signature_id="test-payload-signature-id",
            address_id="0xaddressid",
            wallet_id="test-wallet-id",
            unsigned_payload="0xunsignedpayload",
            signature="0xsignature" if status == "signed" else None,
            status=status,
        )

        return payload_signature_model

    return _create_payload_signature_model


@pytest.fixture
def payload_signature_factory(payload_signature_model_factory):
    """Create and return a factory for creating PayloadSignature fixtures."""

    def _create_payload_signature(status="signed"):
        payload_signature_model = payload_signature_model_factory(status)
        return PayloadSignature(payload_signature_model)

    return _create_payload_signature
