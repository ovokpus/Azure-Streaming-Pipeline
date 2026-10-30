"""Local stand-in for the EventHubTriggerTweetsToCosmosDB function.

Consumes tweet-stream-eh1 (consumer group cosmos-writer), checkpoints in Azurite
blob storage, and upserts each tweet into Cosmos DB (hurricane/tweets, pk /account_id).
"""

import json
import logging
import time

from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore

from shared_code.tweet_schema import to_cosmos_document

from . import config
from .clients import cosmos_container, ensure_containers

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s worker: %(message)s")
logging.getLogger("azure").setLevel(logging.WARNING)
log = logging.getLogger("worker")


def wait_for(fn, what: str, attempts: int = 60):
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            log.info("waiting for %s (%s: %s)", what, type(e).__name__, str(e)[:120])
            time.sleep(3)
    raise RuntimeError(f"{what} not ready")


def main() -> None:
    wait_for(ensure_containers, "Azurite")
    container = wait_for(cosmos_container, "Cosmos DB emulator")
    store = BlobCheckpointStore.from_connection_string(config.STORAGE_CONN, config.CHECKPOINT_CONTAINER)
    client = EventHubConsumerClient.from_connection_string(
        config.EVENTHUB_CONN, consumer_group=config.COSMOS_GROUP,
        eventhub_name=config.EVENTHUB_NAME, checkpoint_store=store)
    written = 0

    def on_event_batch(partition_context, events):
        nonlocal written
        for event in events:
            doc = to_cosmos_document(json.loads(event.body_as_str()))
            container.upsert_item(doc)
            written += 1
        if events:
            partition_context.update_checkpoint(events[-1])
            log.info("partition %s: wrote %d tweets to Cosmos (total %d)",
                     partition_context.partition_id, len(events), written)

    log.info("consuming %s / %s", config.EVENTHUB_NAME, config.COSMOS_GROUP)
    with client:
        client.receive_batch(on_event_batch=on_event_batch, max_batch_size=50,
                             max_wait_time=2, starting_position="-1")


if __name__ == "__main__":
    main()
