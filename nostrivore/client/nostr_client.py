import time
import ssl
from nostr.relay import Relay
from nostr.message_pool import MessagePool
from nostr.event import Event
# from nostr.message_type import EventMessage # Not strictly needed for this change
from nostrivore.models.events import ArticleSaveEvent, ArticleContentEvent

class NostrClient:
    def __init__(self, relay_urls: list[str]):
        self.relay_urls = relay_urls
        self.message_pool = MessagePool()
        self.relays = {}

    def connect(self):
        for url in self.relay_urls:
            relay = Relay(url, self.message_pool, ssl_options={"cert_reqs": ssl.CERT_NONE})
            try:
                relay.connect()
                self.relays[url] = relay
                time.sleep(1)  # Allow time for connection to establish
            except Exception as e:
                print(f"Failed to connect to {url}: {e}")


    def disconnect(self):
        for relay in self.relays.values():
            relay.close()

    def publish_event(self, event: Event):
        self.message_pool.publish(event)
        time.sleep(1)  # Allow time for the event to be sent

    def publish_article_with_content(
        self,
        private_key_hex: str,
        article_save_model: ArticleSaveEvent,
        article_content_model: ArticleContentEvent
    ) -> tuple[Event | None, Event | None]:
        """
        Publishes a Kind 30000 (article metadata) event and then
        a Kind 30001 (article content) event referencing the first one.
        """
        # Generate and publish Kind 30000 event (article metadata)
        save_event_nostr = article_save_model.to_nostr_event(private_key_hex)

        # Assuming publish_event raises an exception or logs on failure,
        # otherwise, we proceed optimistically.
        self.publish_event(save_event_nostr)

        if not save_event_nostr.id:
            # This case should ideally not happen if to_nostr_event and publish_event are correct
            # and Event class populates id upon creation/signing.
            print("Error: ArticleSaveEvent Nostr ID not set after creation.")
            return None, None

        # Set parent_event_id and privacy for the content event
        article_content_model.parent_event_id = save_event_nostr.id
        article_content_model.is_private = (article_save_model.privacy_kind == "private")

        # Generate and publish Kind 30001 event (article content)
        content_event_nostr = article_content_model.to_nostr_event(private_key_hex)
        self.publish_event(content_event_nostr)

        if not content_event_nostr.id:
            # Similar check for the content event
            print("Error: ArticleContentEvent Nostr ID not set after creation.")
            # We might have a partially successful operation here (save_event published)
            # For now, return what we have. Robust error handling would be more complex.
            return save_event_nostr, None

        return save_event_nostr, content_event_nostr
