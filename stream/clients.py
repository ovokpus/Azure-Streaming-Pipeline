"""Thin factories for the Azure SDK clients (pointed at emulators by default)."""

import logging

from azure.core.exceptions import ResourceExistsError
from azure.cosmos import CosmosClient, PartitionKey
from azure.storage.blob import BlobServiceClient

from . import config

log = logging.getLogger(__name__)


def blob_service() -> BlobServiceClient:
    return BlobServiceClient.from_connection_string(config.STORAGE_CONN)


def ensure_containers() -> None:
    svc = blob_service()
    for name in (config.BLOB_CONTAINER, config.CHECKPOINT_CONTAINER):
        try:
            svc.create_container(name)
        except ResourceExistsError:
            pass


def cosmos_container():
    client = CosmosClient(config.COSMOS_ENDPOINT, credential=config.COSMOS_KEY)
    db = client.create_database_if_not_exists(config.COSMOS_DATABASE)
    return db.create_container_if_not_exists(
        id=config.COSMOS_CONTAINER, partition_key=PartitionKey(path="/account_id"))
