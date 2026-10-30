"""Settings for the local stand-ins. Defaults target the docker compose network.

Every value can point at real Azure instead: swap the connection strings in .env.
Emulator credentials are read from the environment; docker compose provides local-only defaults.
"""

import os

# Emulator credentials come from the environment (docker compose supplies ${VAR:-default}); none are hard-coded here.
EVENTHUBS_SAS_KEY = os.getenv("EVENTHUBS_SAS_KEY", "")
EVENTHUB_CONN = os.getenv(
    "EVENTHUB_CONNECTION_STRING",
    "Endpoint=sb://eventhubs-emulator;SharedAccessKeyName=RootManageSharedAccessKey;"
    f"SharedAccessKey={EVENTHUBS_SAS_KEY};UseDevelopmentEmulator=true;",
)
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME", "tweet-stream-eh1")
COSMOS_GROUP = os.getenv("EVENTHUB_COSMOS_CONSUMER_GROUP", "cosmos-writer")
LIVE_GROUP = os.getenv("EVENTHUB_LIVE_CONSUMER_GROUP", "live-view")

AZURITE_ACCOUNT_NAME = os.getenv("AZURITE_ACCOUNT_NAME", "devstoreaccount1")
AZURITE_ACCOUNT_KEY = os.getenv("AZURITE_ACCOUNT_KEY", "")
STORAGE_CONN = os.getenv(
    "STORAGE_CONNECTION_STRING",
    f"DefaultEndpointsProtocol=http;AccountName={AZURITE_ACCOUNT_NAME};"
    f"AccountKey={AZURITE_ACCOUNT_KEY};"
    f"BlobEndpoint=http://azurite:10000/{AZURITE_ACCOUNT_NAME};",
)
BLOB_CONTAINER = os.getenv("BLOB_CONTAINER", "tweets")
CHECKPOINT_CONTAINER = os.getenv("CHECKPOINT_CONTAINER", "eventhub-checkpoints")

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT", "http://cosmos:8081")
COSMOS_KEY = os.getenv("COSMOS_KEY", "")
COSMOS_DATABASE = os.getenv("COSMOS_DATABASE", "hurricane")
COSMOS_CONTAINER = os.getenv("COSMOS_CONTAINER", "tweets")

INGEST_URL = os.getenv("INGEST_URL", "http://api:8000/api/tweets")
