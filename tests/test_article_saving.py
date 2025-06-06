import pytest
from nostrivore.models.events import ArticleSaveEvent
from nostr.key import PrivateKey
# nip04_decrypt is a method of PrivateKey

def test_create_public_article_save_event():
    test_private_key = PrivateKey()
    test_private_key_hex = test_private_key.hex()
    test_public_key_hex = test_private_key.public_key.hex()

    article_event = ArticleSaveEvent(
        title="Test Public Article",
        url="http://example.com/public",
        omnivore_id="omni-public-123",
        privacy_kind="public",
        description="A public test article.",
        image="http://example.com/public.jpg",
        author="Public Author",
        tags=["news", "tech"]
    )

    nostr_event = article_event.to_nostr_event(test_private_key_hex)

    assert nostr_event.kind == 30000
    assert nostr_event.content == article_event.title
    assert nostr_event.public_key == test_public_key_hex

    expected_tags = [
        ["url", article_event.url],
        ["description", article_event.description],
        ["image", article_event.image],
        ["author", article_event.author],
        ["t", "news"],
        ["t", "tech"],
        ["kind", "public"],
        ["omnivore_id", article_event.omnivore_id]
    ]
    for tag in expected_tags:
        assert tag in nostr_event.tags

    # Check that no "p" tag for the user's public key is present
    p_tags = [t for t in nostr_event.tags if t[0] == "p"]
    assert not any(pt[1] == test_public_key_hex for pt in p_tags)

    assert nostr_event.id is not None
    assert nostr_event.signature is not None

def test_create_private_article_save_event():
    test_private_key = PrivateKey()
    test_private_key_hex = test_private_key.hex()
    test_public_key_hex = test_private_key.public_key.hex()

    article_event = ArticleSaveEvent(
        title="Test Private Article",
        url="http://example.com/private",
        omnivore_id="omni-private-456",
        privacy_kind="private",
        description="A private test article.",
        # Not including image and author to test optionality with private
        tags=["secret", "personal"]
    )

    nostr_event = article_event.to_nostr_event(test_private_key_hex)

    assert nostr_event.kind == 30000
    assert nostr_event.content != article_event.title  # Should be encrypted
    assert nostr_event.public_key == test_public_key_hex

    # Use the decrypt_message method from the PrivateKey object
    decrypted_title = test_private_key.decrypt_message(
        encoded_message=nostr_event.content,
        public_key_hex=test_public_key_hex # This is the pubkey of the other party, which is oneself here
    )
    assert decrypted_title == article_event.title

    expected_tags_present = [
        ["url", article_event.url],
        ["description", article_event.description],
        ["t", "secret"],
        ["t", "personal"],
        ["kind", "private"],
        ["omnivore_id", article_event.omnivore_id],
        ["p", test_public_key_hex]
    ]
    for tag in expected_tags_present:
        assert tag in nostr_event.tags

    # Check that optional fields not provided are not in tags
    assert not any(t[0] == "image" for t in nostr_event.tags)
    assert not any(t[0] == "author" for t in nostr_event.tags)

    assert nostr_event.id is not None
    assert nostr_event.signature is not None

def test_public_event_optional_fields_not_present():
    test_private_key = PrivateKey()
    test_private_key_hex = test_private_key.hex()

    article_event = ArticleSaveEvent(
        title="Test Public Article Minimal",
        url="http://example.com/public-minimal",
        omnivore_id="omni-public-min-789",
        privacy_kind="public"
        # No description, image, author, tags
    )
    nostr_event = article_event.to_nostr_event(test_private_key_hex)
    assert not any(t[0] == "description" for t in nostr_event.tags)
    assert not any(t[0] == "image" for t in nostr_event.tags)
    assert not any(t[0] == "author" for t in nostr_event.tags)
    t_tags = [t for t in nostr_event.tags if t[0] == "t"]
    assert len(t_tags) == 0
