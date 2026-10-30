"""Settings for the local stand-ins. Defaults target the docker compose network.

Every value can point at real Azure instead: swap the connection strings in .env.
The defaults below are the *publicly documented* emulator credentials, not secrets.
"""

import os

EVENTHUB_CONN = os.getenv(
    "EVENTHUB_CONNECTION_STRING",
    "Endpoint=sb://eventhubs-emulator;SharedAccessKeyName=RootManageSharedAccessKey;"
    "SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;",
)
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME", "tweet-stream-eh1")
COSMOS_GROUP = os.getenv("EVENTHUB_COSMOS_CONSUMER_GROUP", "cosmos-writer")
LIVE_GROUP = os.getenv("EVENTHUB_LIVE_CONSUMER_GROUP", "live-view")

STORAGE_CONN = os.getenv(
    "STORAGE_CONNECTION_STRING",
    "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://azurite:10000/devstoreaccount1;",
)
BLOB_CONTAINER = os.getenv("BLOB_CONTAINER", "tweets")
CHECKPOINT_CONTAINER = os.getenv("CHECKPOINT_CONTAINER", "eventhub-checkpoints")

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT", "http://cosmos:8081")
COSMOS_KEY = os.getenv(
    "COSMOS_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)
COSMOS_DATABASE = os.getenv("COSMOS_DATABASE", "hurricane")
COSMOS_CONTAINER = os.getenv("COSMOS_CONTAINER", "tweets")

INGEST_URL = os.getenv("INGEST_URL", "http://api:8000/api/tweets")
