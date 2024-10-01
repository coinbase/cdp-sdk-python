import pytest

from cdp.client.models.sponsored_send import SponsoredSend as SponsoredSendModel


@pytest.fixture
def sponsored_send_model_factory():
    """Create and return a factory for creating SponsoredSendModel fixtures."""

    def _create_sponsored_send_model(status="complete"):
        status = "submitted" if status == "broadcast" else status

        return SponsoredSendModel(
            to_address_id="0xdestination",
            raw_typed_data="0xtypeddata",
            typed_data_hash="0xtypeddatahash",
            signature="0xsignature" if status in ["signed", "submitted", "complete"] else None,
            transaction_hash="0xtransactionhash" if status == "complete" else None,
            transaction_link="https://sepolia.basescan.org/tx/0xtransactionlink"
            if status == "complete"
            else None,
            status=status,
        )

    return _create_sponsored_send_model
