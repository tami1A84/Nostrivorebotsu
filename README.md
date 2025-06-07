# Nostrivore

**Nostrivore** is a Python library designed to bridge the popular read-it-later service [Omnivore](https://omnivore.app/) with the decentralized [Nostr](https://nostr.com/) protocol. It enables Omnivore users to leverage Nostr's capabilities for managing, sharing, and potentially synchronizing their reading lists and article metadata in a distributed and censorship-resistant manner.

## Current Features

Nostrivore currently offers the following functionalities:

*   **Article Metadata Saving (Nostr Kind 30000):**
    *   Defines a Nostr event (Kind 30000) specifically for saving article metadata, including URL, title, author, publication date, and user-defined tags.
    *   Supports **NIP-04 encryption** to ensure the privacy of saved article metadata when desired.
*   **Nostr Client (`NostrClient`):**
    *   Provides a client class for preparing and formatting Nostr events.
    *   Facilitates connection to Nostr relays.
*   **Unit Tests:**
    *   Includes tests for event creation, NIP-04 encryption, and client operations.

## Getting Started

Follow these steps to get Nostrivore up and running on your local machine:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/nostrivore.git # Replace with the actual repository URL
    cd nostrivore
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    If a `requirements-dev.txt` file is present, you might want to install development dependencies as well for testing or contributing:
    ```bash
    pip install -r requirements-dev.txt
    ```

## Usage

Nostrivore is primarily a library. The core component for interacting with Nostr is the `NostrClient`. Here's a basic example of how to initialize and use it:

```python
from nostrivore.client import NostrClient

# Example: Initialize the client with a list of relay URLs
# Replace with your desired Nostr relay URLs
client = NostrClient(relay_urls=["wss://relay.damus.io", "wss://relay.primal.net"])

# Connect to the relays
client.connect()

if client.is_connected:
    print("Successfully connected to Nostr relays!")
    #
    # Example: Prepare an article event (details depend on your implementation)
    # from nostrivore.event import create_article_event, sign_event
    # from nostrivore.key import generate_key_pair
    #
    # private_key, public_key = generate_key_pair()
    # article_data = {
    # "url": "https://example.com/article",
    # "title": "My Awesome Article",
    # "author": "John Doe",
    # # ... other metadata
    # }
    #
    # # Create an unencrypted event
    # event = create_article_event(public_key, article_data)
    # signed_event = sign_event(event, private_key)
    #
    # # Send the event (actual sending logic might be part of the client or handled separately)
    # # client.publish_event(signed_event)
    # print(f"Prepared event: {signed_event.to_json()}")

else:
    print("Failed to connect to any Nostr relays.")

# Disconnect from relays when done
client.disconnect()
print("Disconnected from relays.")
```
*Note: The event creation and publishing parts in the snippet above are illustrative. Refer to the library's specific functions for actual implementation.*

## Running Tests

To run the suite of unit tests, ensure you have the development dependencies installed (including `pytest`), and then run:

```bash
pytest
```
This command will discover and execute all tests within the `tests/` directory.

## Contributing

Contributions to Nostrivore are welcome! Whether it's bug fixes, new features, or documentation improvements, please feel free to:

1.  Fork the repository.
2.  Create a new branch for your changes (`git checkout -b feature/your-feature-name`).
3.  Make your changes and ensure tests pass.
4.  Commit your changes (`git commit -am 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Create a new Pull Request.

We appreciate your help in making Nostrivore better!

## Future Goals (Roadmap)

While Nostrivore is in its early stages, here are some potential directions for future development:

*   **Expanding Nostr Feature Integration:** Incorporate more Nostr Improvement Proposals (NIPs) relevant to content sharing and management (e.g., NIP-23 for long-form content, NIP-51 for lists).
*   **Developing an Example Omnivore Plugin:** Create a proof-of-concept Omnivore plugin that utilizes Nostrivore to demonstrate practical integration.
*   **Enhanced Relay Management:** More sophisticated handling of relay connections, disconnections, and data synchronization.
*   **User Identity and Key Management:** Streamlined ways to manage user Nostr identities within the library or an associated application.
*   **Content Curation Features:** Exploring how Nostr lists or channels could be used for curating and discovering content.

Stay tuned for updates as the project evolves!
