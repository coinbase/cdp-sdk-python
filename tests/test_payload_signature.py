from unittest.mock import ANY, Mock, call, patch

import pytest

from cdp.payload_signature import PayloadSignature


def test_payload_signature_initialization(payload_signature_factory):
    """Test the initialization of a PayloadSignature object."""
    payload_signature = payload_signature_factory()
    assert isinstance(payload_signature, PayloadSignature)


def test_payload_signuatre_properties(payload_signature_factory):
    """Test the properties of a PayloadSignature object."""
    payload_signature = payload_signature_factory()
    assert payload_signature.payload_signature_id == "test-payload-signature-id"
    assert payload_signature.address_id == "0xaddressid"
    assert payload_signature.wallet_id == "test-wallet-id"
    assert payload_signature.unsigned_payload == "0xunsignedpayload"
    assert payload_signature.signature == "0xsignature"
    assert payload_signature.status.value == "signed"


@patch("cdp.Cdp.api_clients")
def test_create_unsigned_payload_signature(mock_api_clients, payload_signature_model_factory):
    """Test the creation of a PayloadSignature object."""
    mock_create_payload_signature = Mock(return_value=payload_signature_model_factory("pending"))
    mock_api_clients.addresses.create_payload_signature = mock_create_payload_signature

    payload_signature = PayloadSignature.create(
        wallet_id="test-wallet-id",
        address_id="0xaddressid",
        unsigned_payload="0xunsignedpayload",
        signature="0xsignature",
    )

    assert isinstance(payload_signature, PayloadSignature)
    mock_create_payload_signature.assert_called_once_with(
        wallet_id="test-wallet-id", address_id="0xaddressid", create_payload_signature_request=ANY
    )

    create_payload_signature_request = mock_create_payload_signature.call_args[1][
        "create_payload_signature_request"
    ]
    assert create_payload_signature_request.unsigned_payload == "0xunsignedpayload"


@patch("cdp.Cdp.api_clients")
def test_create_payload_signature(mock_api_clients, payload_signature_model_factory):
    """Test the creation of a PayloadSignature object."""
    mock_create_payload_signature = Mock(return_value=payload_signature_model_factory())
    mock_api_clients.addresses.create_payload_signature = mock_create_payload_signature

    payload_signature = PayloadSignature.create(
        wallet_id="test-wallet-id",
        address_id="0xaddressid",
        unsigned_payload="0xunsignedpayload",
        signature="0xsignature",
    )

    assert isinstance(payload_signature, PayloadSignature)
    mock_create_payload_signature.assert_called_once_with(
        wallet_id="test-wallet-id", address_id="0xaddressid", create_payload_signature_request=ANY
    )

    create_payload_signature_request = mock_create_payload_signature.call_args[1][
        "create_payload_signature_request"
    ]
    assert create_payload_signature_request.unsigned_payload == "0xunsignedpayload"
    assert create_payload_signature_request.signature == "0xsignature"


@patch("cdp.Cdp.api_clients")
def test_list_payload_signatures(mock_api_clients, payload_signature_model_factory):
    """Test the listing of payload signatures."""
    mock_list_payload_signatures = Mock()
    mock_list_payload_signatures.return_value = Mock(
        data=[payload_signature_model_factory()], has_more=False
    )
    mock_api_clients.addresses.list_payload_signatures = mock_list_payload_signatures

    payload_signatures = PayloadSignature.list("test-wallet-id", "0xaddressid")
    assert len(list(payload_signatures)) == 1
    assert all(isinstance(p, PayloadSignature) for p in payload_signatures)
    mock_list_payload_signatures.assert_called_once_with(
        wallet_id="test-wallet-id", address_id="0xaddressid", limit=100, page=None
    )


@patch("cdp.Cdp.api_clients")
def test_reload_payload_signature(mock_api_clients, payload_signature_factory):
    """Test the reloading of a payload signature."""
    payload_signature = payload_signature_factory("pending")
    signed_payload_signature = payload_signature_factory()
    mock_get_payload_signature = Mock(return_value=signed_payload_signature._model)
    mock_api_clients.addresses.get_payload_signature = mock_get_payload_signature

    payload_signature.reload()
    mock_get_payload_signature.assert_called_once_with(
        payload_signature.wallet_id,
        payload_signature.address_id,
        payload_signature.payload_signature_id,
    )
    assert payload_signature.status.value == "signed"


@patch("cdp.Cdp.api_clients")
@patch("cdp.payload_signature.time.sleep")
@patch("cdp.payload_signature.time.time")
def test_wait_for_payload_signature(
    mock_time, mock_sleep, mock_api_clients, payload_signature_factory
):
    """Test the waiting for a PayloadSignature object to be signed."""
    pending_payload_signature = payload_signature_factory("pending")
    signed_payload_signature = payload_signature_factory()
    mock_get_payload_signature = Mock()
    mock_api_clients.addresses.get_payload_signature = mock_get_payload_signature
    mock_get_payload_signature.side_effect = [
        pending_payload_signature._model,
        signed_payload_signature._model,
    ]

    mock_time.side_effect = [0, 0.2, 0.4]

    result = pending_payload_signature.wait(interval_seconds=0.2, timeout_seconds=1)

    assert result.status.value == "signed"
    mock_get_payload_signature.assert_called_with(
        pending_payload_signature.wallet_id,
        pending_payload_signature.address_id,
        pending_payload_signature.payload_signature_id,
    )
    assert mock_get_payload_signature.call_count == 2
    mock_sleep.assert_has_calls([call(0.2)] * 2)
    assert mock_time.call_count == 3


@patch("cdp.Cdp.api_clients")
@patch("cdp.payload_signature.time.sleep")
@patch("cdp.payload_signature.time.time")
def test_wait_for_payload_signature_timeout(
    mock_time, mock_sleep, mock_api_clients, payload_signature_factory
):
    """Test the waiting for a PayloadSignature object to be signed with a timeout."""
    pending_payload_signature = payload_signature_factory("pending")
    mock_get_payload_signature = Mock(return_value=pending_payload_signature._model)
    mock_api_clients.addresses.get_payload_signature = mock_get_payload_signature

    mock_time.side_effect = [0, 0.5, 1.0, 1.5, 2.0, 2.5]

    with pytest.raises(TimeoutError, match="Timed out waiting for PayloadSignature to be signed"):
        pending_payload_signature.wait(interval_seconds=0.5, timeout_seconds=2)

    assert mock_get_payload_signature.call_count == 5
    mock_sleep.assert_has_calls([call(0.5)] * 4)
    assert mock_time.call_count == 6


def test_payload_signature_str_representation(payload_signature_factory):
    """Test the string representation of a PayloadSignature object."""
    payload_signature = payload_signature_factory()
    expected_str = (
        f"PayloadSignature: (payload_signature_id: {payload_signature.payload_signature_id}, wallet_id: {payload_signature.wallet_id}, "
        f"address_id: {payload_signature.address_id}, unsigned_payload: {payload_signature.unsigned_payload}, signature: {payload_signature.signature}, "
        f"status: {payload_signature.status})"
    )
    assert str(payload_signature) == expected_str


def test_payload_signature_repr(payload_signature_factory):
    """Test the representation of a PayloadSignature object."""
    payload_signature = payload_signature_factory()
    assert repr(payload_signature) == str(payload_signature)
