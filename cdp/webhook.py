from collections.abc import Iterator

from cdp.cdp import Cdp
from cdp.client.models.create_webhook_request import CreateWebhookRequest
from cdp.client.models.update_webhook_request import UpdateWebhookRequest
from cdp.client.models.webhook import Webhook as WebhookModel
from cdp.client.models.webhook import WebhookEventFilter, WebhookEventType, WebhookEventTypeFilter
from cdp.client.models.webhook_list import WebhookList


class Webhook:
    """A class representing a webhook."""

    def __init__(self, model: WebhookModel) -> None:
        """Initialize the Webhook class.

        Args:
            model (WebhookModel): The WebhookModel object representing the Webhook.

        """
        self._model = model

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
            event_type_filter: WebhookEventTypeFilter | None = None,
            event_filters: list[WebhookEventFilter] | None = None,
            network_id: str = "base-sepolia",
    ) -> "Webhook":
        """Create a new webhook.

        Args:
            notification_uri (str): The URI where notifications should be sent.
            event_type (WebhookEventType): The type of event that the webhook listens to.
            event_type_filter (WebhookEventTypeFilter): Filter specifically for wallet activity event type.
            event_filters (List[WebhookEventTypeFilter]): Filters applied to the events that determine which specific address(es) trigger.
            network_id (str): The network ID of the wallet. Defaults to "base-sepolia".

        Returns:
            Webhook: The created webhook object.

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

        """
        while True:
            page = None

            response: WebhookList = Cdp.api_clients.webhooks.list_webhooks(limit=100, page=page)

            for webhook_model in response.data:
                yield cls(webhook_model)

            if not response.has_more:
                break

            page = response.next_page

    @staticmethod
    def delete(webhook_id: str) -> None:
        """Delete a webhook by its ID.

        Args:
            webhook_id (str): The ID of the webhook to delete.

        """
        Cdp.api_clients.webhooks.delete_webhook(webhook_id)

    def update(
        self,
        notification_uri: str | None = None,
        event_type_filter: WebhookEventTypeFilter | None = None
    ) -> "Webhook":
        """Update the webhook with a new notification URI, and/or a new list of addresses to monitor.

        Args:
            notification_uri (str): The new URI for webhook notifications.
            event_type_filter (WebhookEventTypeFilter): The new eventTypeFilter that contains a new list (replacement) of addresses to monitor for the webhook.

        Returns:
            Webhook: The updated webhook object.

        """
        # Fallback to current properties if no new values are provided
        final_notification_uri = notification_uri or self.notification_uri
        final_event_type_filter = event_type_filter or self.event_type_filter

        update_webhook_request = UpdateWebhookRequest(
            event_type_filter=final_event_type_filter,
            event_filters=self.event_filters,
            notification_uri=final_notification_uri,
        )

        # Update the webhook via the API client
        result = Cdp.api_clients.webhooks.update_webhook(
            self.id,
            update_webhook_request,
        )

        # Update the internal model with the API response
        self._model = result

        return self

    def __str__(self) -> str:
        """Return a string representation of the Webhook object.

        Returns:
            str: A string representation of the Webhook.

        """
        return f"Webhook: (id: {self.id}, network_id: {self.network_id}, notification_uri: {self.notification_uri}, event_type: {self.event_type}, event_type_filter: {self.event_type_filter}, event_filters: {self.event_filters})"

    def __repr__(self) -> str:
        """Return a detailed string representation of the Webhook object.

        Returns:
            str: A string that represents the Webhook object.

        """
        return str(self)
