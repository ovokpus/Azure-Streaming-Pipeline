"""Local stand-in for APIM + the TriggerTweetsToBlobAndEventHub function, plus a live view API.

POST /api/tweets   validate -> write blob tweets/{guid}.json (Azurite) -> send to Event Hub (emulator)
GET  /api/live     Server-Sent Events: tweets as they come off Event Hub (consumer group live-view)
GET  /api/stats    counters for each pipeline stage
GET  /api/tweets   latest documents persisted in Cosmos DB by the worker
"""

import asyncio
import json
import logging
import threading
import time
import uuid
from collections import Counter, deque
from contextlib import asynccontextmanager

from azure.eventhub import EventData, EventHubConsumerClient, EventHubProducerClient
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse

from shared_code.tweet_schema import TweetValidationError, parse_and_validate

from . import config
from .clients import blob_service, cosmos_container, ensure_containers

log = logging.getLogger("api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s api: %(message)s")
logging.getLogger("azure").setLevel(logging.WARNING)


class State:
    def __init__(self):
        self.accepted = 0
        self.rejected = 0
        self.last_rejection: str | None = None
        self.live_seen = 0
        self.damage = Counter()
        self.recent = deque(maxlen=200)  # messages seen on Event Hub (without image bytes)
        self.per_second = deque(maxlen=120)  # (epoch_second, count)
        self.subscribers: set[asyncio.Queue] = set()
        self.loop: asyncio.AbstractEventLoop | None = None
        self.producer: EventHubProducerClient | None = None
        self.cosmos = None
        self.blob_cache = (0.0, 0)
        self.cosmos_cache = (0.0, 0)
        self.ready = {"azurite": False, "eventhub": False, "cosmos": False}


state = State()


def _bump_rate():
    now = int(time.time())
    if state.per_second and state.per_second[-1][0] == now:
        state.per_second[-1] = (now, state.per_second[-1][1] + 1)
    else:
        state.per_second.append((now, 1))


def _live_consumer():
    """Background thread: tail Event Hub and fan messages out to SSE subscribers."""
    while True:
        try:
            client = EventHubConsumerClient.from_connection_string(
                config.EVENTHUB_CONN, consumer_group=config.LIVE_GROUP, eventhub_name=config.EVENTHUB_NAME)

            def on_event(partition_context, event):
                if event is None:
                    return
                state.ready["eventhub"] = True
                msg = json.loads(event.body_as_str())
                msg["has_image"] = bool(msg.get("image_base64"))
                msg["partition"] = partition_context.partition_id
                msg["enqueued_time"] = event.enqueued_time.isoformat() if event.enqueued_time else None
                state.live_seen += 1
                state.damage[msg.get("damage_flag", "unknown")] += 1
                _bump_rate()
                light = {k: v for k, v in msg.items() if k != "image_base64"}
                state.recent.appendleft(light)
                if state.loop:
                    for q in list(state.subscribers):
                        state.loop.call_soon_threadsafe(q.put_nowait, msg)

            with client:
                client.receive(on_event=on_event, starting_position="@latest", max_wait_time=5)
        except Exception as e:  # noqa: BLE001
            log.info("live consumer waiting for Event Hub: %s", str(e)[:150])
            time.sleep(3)


def _connect_backends():
    while not all(state.ready.values()) or state.cosmos is None:
        try:
            if not state.ready["azurite"]:
                ensure_containers()
                state.ready["azurite"] = True
            if state.producer is None:
                state.producer = EventHubProducerClient.from_connection_string(
                    config.EVENTHUB_CONN, eventhub_name=config.EVENTHUB_NAME)
                state.producer.get_partition_ids()
                state.ready["eventhub"] = True
            if state.cosmos is None:
                state.cosmos = cosmos_container()
                state.ready["cosmos"] = True
        except Exception as e:  # noqa: BLE001
            state.producer = None if not state.ready["eventhub"] else state.producer
            log.info("waiting for emulators: %s: %s", type(e).__name__, str(e)[:150])
            time.sleep(3)
    log.info("all emulators connected")


@asynccontextmanager
async def lifespan(app: FastAPI):
    state.loop = asyncio.get_running_loop()
    threading.Thread(target=_connect_backends, daemon=True).start()
    threading.Thread(target=_live_consumer, daemon=True).start()
    yield
    if state.producer:
        state.producer.close()


app = FastAPI(title="Hurricane tweet stream (local Azure stand-ins)", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"status": "ok" if all(state.ready.values()) else "starting", **state.ready}


def ingest(body: bytes) -> str:
    """Same steps as the TriggerTweetsToBlobAndEventHub function, minus the APIM hop."""
    if state.producer is None or not state.ready["azurite"]:
        raise HTTPException(503, "emulators still starting")
    parse_and_validate(body)  # raises TweetValidationError -> 400
    blob_name = f"{uuid.uuid4()}.json"
    blob_service().get_blob_client(config.BLOB_CONTAINER, blob_name).upload_blob(body)
    batch = state.producer.create_batch()
    batch.add(EventData(body))
    state.producer.send_batch(batch)
    return blob_name


@app.post("/api/tweets", response_class=PlainTextResponse)
async def post_tweet(request: Request):
    body = await request.body()
    try:
        blob = await asyncio.to_thread(ingest, body)
    except TweetValidationError as err:
        state.rejected += 1
        state.last_rejection = str(err)[:300]
        raise HTTPException(400, str(err)) from err
    state.accepted += 1
    return PlainTextResponse(f"This HTTP triggered function executed successfully. blob=tweets/{blob}")


def _blob_count() -> int:
    ts, n = state.blob_cache
    if time.time() - ts > 3 and state.ready["azurite"]:
        n = sum(1 for _ in blob_service().get_container_client(config.BLOB_CONTAINER).list_blob_names())
        state.blob_cache = (time.time(), n)
    return n


def _cosmos_count() -> int:
    ts, n = state.cosmos_cache
    if time.time() - ts > 3 and state.cosmos is not None:
        n = list(state.cosmos.query_items("SELECT VALUE COUNT(1) FROM c", enable_cross_partition_query=True))[0]
        state.cosmos_cache = (time.time(), n)
    return n


@app.get("/api/stats")
async def stats():
    blobs, docs = await asyncio.gather(asyncio.to_thread(_blob_count), asyncio.to_thread(_cosmos_count))
    now = int(time.time())
    window = {s: c for s, c in state.per_second}
    return {
        "accepted": state.accepted,
        "rejected": state.rejected,
        "last_rejection": state.last_rejection,
        "blobs": blobs,
        "eventhub_seen": state.live_seen,
        "cosmos_documents": docs,
        "damage": dict(state.damage),
        "rate": [window.get(now - i, 0) for i in range(60, 0, -1)],
        "emulators": state.ready,
    }


@app.get("/api/recent")
def recent(limit: int = 100):
    return list(state.recent)[:limit]


@app.get("/api/tweets")
async def cosmos_tweets(limit: int = 20):
    if state.cosmos is None:
        return []
    q = (f"SELECT TOP {int(limit)} c.id, c.tweet_id, c.account_id, c.tweet, c.damage_flag, c.likes, "
         "c.retweets, c.latitude, c.longitude, c._ts FROM c ORDER BY c._ts DESC")
    return await asyncio.to_thread(lambda: list(state.cosmos.query_items(q, enable_cross_partition_query=True)))


@app.get("/api/live")
async def live(request: Request):
    q: asyncio.Queue = asyncio.Queue(maxsize=500)
    state.subscribers.add(q)

    async def events():
        try:
            yield "retry: 2000\n\n"
            while not await request.is_disconnected():
                try:
                    msg = await asyncio.wait_for(q.get(), timeout=15)
                    yield f"data: {json.dumps(msg)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            state.subscribers.discard(q)

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
