# Nostrivore

Nostrivore aims to integrate [Nostr](https://nostr.com/) protocol features into [Omnivore](https://omnivore.app/), the open-source read-it-later service. This project will allow Omnivore users to manage, share, and synchronize their reading lists in a decentralized manner using Nostr.

## Current Status

The project is in its initial development phase. Currently implemented features include:

*   **Article Metadata Saving (Nostr Kind 30000):**
    *   Definition of the Nostr event for saving article metadata (URL, title, description, tags, etc.).
    *   NIP-04 encryption for private article metadata.
    *   Basic client functionality to prepare these events for sending to Nostr relays.
    *   Unit tests for event creation and encryption.

## Development Setup

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository-url>
    cd nostrivore
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running Tests

To run the unit tests, use pytest:

```bash
pytest
```

## Contributing

Details on contributing will be added as the project matures.
