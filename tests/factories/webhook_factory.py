import pytest

from cdp.client import WebhookWalletActivityFilter, WebhookEventTypeFilter
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
        # Ensure the event_type_filter is properly initialized
        if event_type_filter is None and event_type == WebhookEventType.WALLET_ACTIVITY:
            event_type_filter = WebhookEventTypeFilter(
                actual_instance=WebhookWalletActivityFilter(
                    wallet_id="w1",
                    addresses=["0xa55C5950F7A3C42Fa5799B2Cac0e455774a07382"],
                )
            )

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
