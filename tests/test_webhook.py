from unittest.mock import patch

from cdp.client.models.create_webhook_request import CreateWebhookRequest
from cdp.client.models.update_webhook_request import UpdateWebhookRequest
from cdp.client.models.webhook import WebhookEventFilter, WebhookEventType, WebhookEventTypeFilter
from cdp.webhook import Webhook, WebhookModel


@patch("cdp.Cdp.api_clients")
def test_webhook_creation(mock_api_clients, webhook_factory):
    """Test Webhook creation method."""
    mock_api_clients.webhooks.create_webhook.return_value = webhook_factory()

    # Define input parameters for the webhook creation
    notification_uri = "https://example.com/webhook"
    event_type = WebhookEventType.WALLET_ACTIVITY
    event_type_filter = WebhookEventTypeFilter()
    event_filters = [WebhookEventFilter()]

    expected_request = CreateWebhookRequest(
        network_id="base-sepolia",
        event_type=event_type,
        event_type_filter=event_type_filter,
        event_filters=event_filters,
        notification_uri=notification_uri
    )

    webhook = Webhook.create(
        notification_uri=notification_uri,
        event_type=event_type,
        event_type_filter=event_type_filter,
        event_filters=event_filters,
        network_id="base-sepolia"
    )

    mock_api_clients.webhooks.create_webhook.assert_called_once_with(expected_request)

    # Check that the returned object is a Webhook instance
    assert isinstance(webhook, Webhook)
    assert webhook.notification_uri == notification_uri
    assert webhook.event_type == event_type


@patch("cdp.Cdp.api_clients")
def test_webhook_delete(mock_api_clients):
    """Test Webhook delete method."""
    webhook_id = "webhook-123"

    Webhook.delete(webhook_id)

    mock_api_clients.webhooks.delete_webhook.assert_called_once_with(webhook_id)


@patch("cdp.Cdp.api_clients")
def test_webhook_update(mock_api_clients, webhook_factory):
    """Test Webhook update method."""
    webhook_model = webhook_factory()

    # Create a Webhook instance
    webhook = Webhook(model=webhook_model)

    assert webhook.notification_uri == "https://example.com/webhook"

    # Define new values for the update
    new_notification_uri = "https://new.example.com/webhook"

    # Mock the API response for update
    mock_api_clients.webhooks.update_webhook.return_value = WebhookModel(
            id=webhook.id,
            network_id=webhook.network_id,
            notification_uri=new_notification_uri,
            event_type=webhook.event_type,
            event_type_filter=webhook.event_type_filter,
            event_filters=webhook.event_filters
        )

    expected_request = UpdateWebhookRequest(
        event_type_filter=webhook.event_type_filter,
        event_filters=webhook.event_filters,
        notification_uri=new_notification_uri
    )

    updated_webhook_model = webhook.update(
        notification_uri=new_notification_uri,
    )

    updated_webhook = Webhook(model=updated_webhook_model)

    # Verify that the API client was called with the correct arguments
    mock_api_clients.webhooks.update_webhook.assert_called_once_with(
        webhook.id, expected_request
    )

    # Assert that the returned object is the updated webhook
    assert isinstance(updated_webhook, Webhook)
    assert updated_webhook.notification_uri == new_notification_uri
    assert updated_webhook.id == webhook.id
