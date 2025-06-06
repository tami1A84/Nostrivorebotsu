import time
import ssl
from nostr.relay import Relay
from nostr.message_pool import MessagePool
from nostr.event import Event
from nostr.message_type import EventMessage

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
