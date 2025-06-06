import pytest
from pytest_mock import MockerFixture # For type hinting if needed, not strictly necessary for mocker fixture

from nostrivore.models.events import ArticleSaveEvent, ArticleContentEvent
from nostrivore.client.nostr_client import NostrClient
from nostr.key import PrivateKey # This should be the one from nostr.key
from nostr.event import Event # The actual Event class from nostr.event

# Unit Tests for ArticleContentEvent.to_nostr_event()

def test_create_public_article_content_event():
    test_private_key_obj = PrivateKey() # Using the constructor from nostr.key
    test_pk_hex = test_private_key_obj.hex()
    # The PublicKey object is available as test_private_key_obj.public_key
    test_pubkey_hex = test_private_key_obj.public_key.hex()

    parent_event_id = "test_parent_event_id_123"
    article_text = "Hello public world"

    content_event_model = ArticleContentEvent(
        article_content=article_text,
        parent_event_id=parent_event_id,
        is_private=False
    )

    nostr_event = content_event_model.to_nostr_event(test_pk_hex)

    assert nostr_event.kind == 30001
    assert nostr_event.content == article_text
    assert ["e", parent_event_id] in nostr_event.tags

    p_tags = [tag for tag in nostr_event.tags if tag[0] == "p"]
    assert not p_tags, "Public event should not have 'p' tags for self-encryption"

    assert nostr_event.public_key == test_pubkey_hex
    assert nostr_event.id is not None
    assert nostr_event.signature is not None

def test_create_private_article_content_event():
    test_private_key_obj = PrivateKey()
    test_pk_hex = test_private_key_obj.hex()
    test_pubkey_hex = test_private_key_obj.public_key.hex()

    parent_event_id = "test_parent_event_id_456"
    article_text = "Hello secret world"

    content_event_model = ArticleContentEvent(
        article_content=article_text,
        parent_event_id=parent_event_id,
        is_private=True
    )

    nostr_event = content_event_model.to_nostr_event(test_pk_hex)

    assert nostr_event.kind == 30001
    assert nostr_event.content != article_text, "Private event content should be encrypted"

    # Decrypt content using the PrivateKey's decrypt_message method
    decrypted_content = test_private_key_obj.decrypt_message(
        encoded_message=nostr_event.content,
        public_key_hex=test_pubkey_hex # Decrypting message encrypted by self to self
    )
    assert decrypted_content == article_text

    assert ["e", parent_event_id] in nostr_event.tags
    assert ["p", test_pubkey_hex] in nostr_event.tags, "Private event should have 'p' tag for recipient (self)"

    assert nostr_event.public_key == test_pubkey_hex
    assert nostr_event.id is not None
    assert nostr_event.signature is not None

# Tests for NostrClient.publish_article_with_content() workflow

def test_publish_article_workflow(mocker: MockerFixture):
    test_private_key_obj = PrivateKey()
    test_pk_hex = test_private_key_obj.hex()

    nostr_client_instance = NostrClient(relay_urls=["wss://dummy.relay.com"])
    mock_publish = mocker.patch.object(nostr_client_instance, 'publish_event')

    save_model = ArticleSaveEvent(
        title="Test Title",
        url="http://example.com/article", # Corrected URL
        omnivore_id="omni123",
        privacy_kind="public"
    )
    content_model = ArticleContentEvent(
        article_content="Test content.",
        parent_event_id="", # Will be set by the method
        is_private=False # Will be set by the method
    )

    save_event_nostr, content_event_nostr = nostr_client_instance.publish_article_with_content(
        test_pk_hex, save_model, content_model
    )

    assert mock_publish.call_count == 2

    # Check calls to publish_event
    call1_args, call2_args = mock_publish.call_args_list

    published_save_event: Event = call1_args[0][0]
    assert published_save_event.kind == 30000
    assert published_save_event.id is not None
    assert published_save_event.content == save_model.title # Public event

    published_content_event: Event = call2_args[0][0]
    assert published_content_event.kind == 30001
    assert published_content_event.content == content_model.article_content # Public event

    assert ["e", published_save_event.id] in published_content_event.tags
    assert content_model.parent_event_id == published_save_event.id
    assert not content_model.is_private # Should be set to False

    assert save_event_nostr is not None
    assert content_event_nostr is not None
    assert save_event_nostr == published_save_event
    assert content_event_nostr == published_content_event

def test_publish_private_article_workflow(mocker: MockerFixture):
    test_private_key_obj = PrivateKey()
    test_pk_hex = test_private_key_obj.hex()
    test_pubkey_hex = test_private_key_obj.public_key.hex()

    nostr_client_instance = NostrClient(relay_urls=["wss://dummy.relay.com"])
    mock_publish = mocker.patch.object(nostr_client_instance, 'publish_event')

    save_model = ArticleSaveEvent(
        title="Secret Test Title",
        url="http://example.com/secret-article",
        omnivore_id="omni-secret-456",
        privacy_kind="private" # Private article
    )
    # Initial is_private for content_model doesn't matter, should be overridden
    content_model = ArticleContentEvent(
        article_content="Secret test content.",
        parent_event_id="",
        is_private=False
    )

    save_event_nostr, content_event_nostr = nostr_client_instance.publish_article_with_content(
        test_pk_hex, save_model, content_model
    )

    assert mock_publish.call_count == 2
    call1_args, call2_args = mock_publish.call_args_list

    # Check Save Event (Kind 30000)
    published_save_event: Event = call1_args[0][0]
    assert published_save_event.kind == 30000
    assert published_save_event.id is not None
    assert published_save_event.content != save_model.title # Should be encrypted
    decrypted_title = test_private_key_obj.decrypt_message(published_save_event.content, test_pubkey_hex)
    assert decrypted_title == save_model.title
    assert ["p", test_pubkey_hex] in published_save_event.tags

    # Check Content Event (Kind 30001)
    published_content_event: Event = call2_args[0][0]
    assert published_content_event.kind == 30001
    assert published_content_event.content != content_model.article_content # Should be encrypted
    decrypted_content = test_private_key_obj.decrypt_message(published_content_event.content, test_pubkey_hex)
    assert decrypted_content == "Secret test content." # Original content
    assert ["p", test_pubkey_hex] in published_content_event.tags

    assert ["e", published_save_event.id] in published_content_event.tags
    assert content_model.parent_event_id == published_save_event.id
    assert content_model.is_private # Should have been set to True by the method

    assert save_event_nostr is not None
    assert content_event_nostr is not None
    assert save_event_nostr == published_save_event
    assert content_event_nostr == published_content_event
