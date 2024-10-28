import pytest

from cdp.webhook import Webhook, WebhookEventType, WebhookModel


@pytest.fixture
def webhook_factory():
    """Create and return a factory for Webhook fixtures."""

    def _create_webhook(
        webhook_id="webhook-123",
        network_id="base-sepolia",
        notification_uri="https://example.com/webhook",
        event_type=WebhookEventType.WALLET_ACTIVITY,
        event_type_filter=None,
        event_filters=None,
    ):
        model = WebhookModel(
            id=webhook_id,
            network_id=network_id,
            notification_uri=notification_uri,
            event_type=event_type,
            event_type_filter=event_type_filter,
            event_filters=event_filters or [],
        )
        return Webhook(model)

    return _create_webhook
