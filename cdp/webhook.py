from cdp.client.models.webhook import Webhook as WebhookModel
from cdp.client.models.webhook import WebhookEventType
from cdp.client.models.webhook import WebhookEventTypeFilter
from cdp.client.models.webhook import WebhookEventFilter
from collections.abc import Iterator
from cdp.client.models.webhook_list import WebhookList
from cdp.client.models.create_webhook_request import CreateWebhookRequest
from cdp.cdp import Cdp


class Webhook:
    """A class representing a webhook."""

    def __init__(self, model: WebhookModel, seed: str | None = None) -> None:
        """Initialize the Webhook class.

        Args:
            model (WebhookModel): The WebhookModel object representing the Webhook.

        """
        self._model = model

    def __str__(self) -> str:
        """Return a string representation of the Webhook object.

        Returns:
            str: A string representation of the Webhook.

        """
        return f"Webhook: (id: {self.id}, network_id: {self.network_id}, notification_uri: {self.notification_uri}, event_type: {self.event_type}, event_type_filter: {self.event_type_filter}, event_filters: {self.event_filters})"

    @property
    def id(self) -> str:
        """Get the ID of the webhook.

        Returns:
            str: The ID of the webhook.

        """
        return self._model.id

    @property
    def network_id(self) -> str:
        """Get the network ID of the webhook.

        Returns:
            str: The network ID of the webhook.

        """
        return self._model.network_id

    @property
    def notification_uri(self) -> str:
        """Get the notification URI of the webhook.

        Returns:
            str: The notification URI of the webhook.

        """
        return self._model.notification_uri

    @property
    def event_type(self) -> WebhookEventType:
        """Get the event type of the webhook.

        Returns:
            str: The event type of the webhook.

        """
        return self._model.event_type

    @property
    def event_type_filter(self) -> WebhookEventTypeFilter:
        """Get the event type filter of the webhook.

        Returns:
            str: The event type filter of the webhook.

        """
        return self._model.event_type_filter

    @property
    def event_filters(self) -> list[WebhookEventFilter]:
        """Get the event filters of the webhook.

        Returns:
            str: The event filters of the webhook.

        """
        return self._model.event_filters

    @classmethod
    def create(
            cls,
            notification_uri: str,
            event_type: WebhookEventType,
            event_type_filter: WebhookEventTypeFilter = None,
            event_filters: list[WebhookEventFilter] = None,
            network_id: str = "base-sepolia",
    ) -> "Webhook":
        """Create a new webhook.

        Args:
            notification_uri (str): The URI where notifications should be sent.
            event_type (WebhookEventType): The type of event that the webhook listens to.
            event_type_filter (WebhookEventTypeFilter): Filter specifically for wallet activity event type.
            event_filters (List[WebhookEventTypeFilter]): Filters applied to the events that determine which specific address(es) trigger
            network_id (str): The network ID of the wallet. Defaults to "base-sepolia".

        Returns:
            Webhook: The created webhook object.

        Raises:
            Exception: If there's an error creating the webhook.

        """
        create_webhook_request = CreateWebhookRequest(
                network_id=network_id,
                event_type=event_type,
                event_type_filter=event_type_filter,
                event_filters=event_filters,
                notification_uri=notification_uri,
        )

        model = Cdp.api_clients.webhooks.create_webhook(create_webhook_request)
        webhook = cls(model)

        return webhook

    @classmethod
    def list(cls) -> Iterator["Webhook"]:
        """List webhooks.

        Returns:
            Iterator[Webhook]: An iterator of webhook objects.

        Raises:
            Exception: If there's an error listing webhooks.

        """
        while True:
            page = None

            response: WebhookList = Cdp.api_clients.webhooks.list_webhooks(limit=100, page=page)

            for webhook_model in response.data:
                yield cls(webhook_model)

            if not response.has_more:
                break

            page = response.next_page


