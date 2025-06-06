import time
from typing import List, Optional

from nostr.event import Event
from nostr.key import PrivateKey
# nip04_encrypt is part of PrivateKey.encrypt_message for this library version
# from nostr.nip04 import nip04_encrypt # Not needed directly if using PrivateKey methods
from pydantic import BaseModel


class ArticleSaveEvent(BaseModel):
    """
    Represents a Nostr Kind 30000 event for saving an article.
    """
    title: str  # maps to Nostr content
    url: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = []  # for Omnivore tags like ["t", "tag1"]
    privacy_kind: str  # "public" or "private", maps to ["kind", "public/private"]
    omnivore_id: str

    def to_nostr_event(self, private_key_hex: str) -> Event:
        """
        Constructs a Nostr event from this ArticleSaveEvent.
        """
        event_tags = [["url", self.url]]
        if self.description:
            event_tags.append(["description", self.description])
        if self.image:
            event_tags.append(["image", self.image])
        if self.author:
            event_tags.append(["author", self.author])
        for tag_item in self.tags:
            event_tags.append(["t", tag_item])
        event_tags.append(["kind", self.privacy_kind])
        event_tags.append(["omnivore_id", self.omnivore_id])

        sender_private_key = PrivateKey(bytes.fromhex(private_key_hex))
        sender_public_key_hex = sender_private_key.public_key.hex() # Ensure this is the raw hex, not with "02" prefix for PublicKey
        event_content = self.title
        created_at_ts = int(time.time())

        if self.privacy_kind == "private":
            encrypted_title = sender_private_key.encrypt_message(
                message=self.title,
                public_key_hex=sender_public_key_hex
            )
            event_content = encrypted_title
            event_tags.append(["p", sender_public_key_hex])

        # Compute ID using the static method
        event_id = Event.compute_id(
            public_key=sender_public_key_hex,
            created_at=created_at_ts,
            kind=30000,
            tags=event_tags,
            content=event_content
        )

        # Sign the ID (must be bytes) using the correct method from nostr.key.PrivateKey
        event_signature_hex = sender_private_key.sign_message_hash(bytes.fromhex(event_id))

        event = Event(
            public_key=sender_public_key_hex,
            content=event_content,
            created_at=created_at_ts,
            kind=30000,
            tags=event_tags,
            id=event_id,
            signature=event_signature_hex
        )
        return event


class ArticleContentEvent(BaseModel):
    """
    Represents a Nostr Kind 30001 event for saving article content.
    NIP-04 encrypted if private.
    """
    article_content: str
    parent_event_id: str  # ID of the Kind 30000 ArticleSaveEvent this content belongs to
    is_private: bool

    def to_nostr_event(self, private_key_hex: str) -> Event:
        """
        Constructs a Nostr event from this ArticleContentEvent.
        """
        sender_private_key = PrivateKey(bytes.fromhex(private_key_hex))
        sender_public_key_hex = sender_private_key.public_key.hex()

        event_content = self.article_content
        event_tags = [["e", self.parent_event_id]]
        created_at_ts = int(time.time())
        kind = 30001 # Nostr Kind for Article Content

        if self.is_private:
            encrypted_content = sender_private_key.encrypt_message(
                message=self.article_content,
                public_key_hex=sender_public_key_hex  # Encrypting to self for now
            )
            event_content = encrypted_content
            event_tags.append(["p", sender_public_key_hex])

        # Compute ID using the static method from nostr.event.Event
        event_id = Event.compute_id(
            public_key=sender_public_key_hex,
            created_at=created_at_ts,
            kind=kind,
            tags=event_tags,
            content=event_content
        )

        # Sign the ID using the method from nostr.key.PrivateKey
        event_signature_hex = sender_private_key.sign_message_hash(bytes.fromhex(event_id))

        # Create the Event object
        nostr_event = Event(
            public_key=sender_public_key_hex,
            content=event_content,
            created_at=created_at_ts,
            kind=kind,
            tags=event_tags,
            id=event_id,
            signature=event_signature_hex
        )
        return nostr_event
