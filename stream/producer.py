"""Replays the tweet stream into the ingest API, like push_tweets.py did against APIM."""

import logging
import os
import time

import httpx

from . import config
from .sample import load_stream

logging.basicConfig(level=logging.INFO, format="%(asctime)s producer: %(message)s")
log = logging.getLogger("producer")

RATE = float(os.getenv("PRODUCER_TWEETS_PER_SECOND", "2"))
LOOP = os.getenv("PRODUCER_LOOP", "true").lower() == "true"
INVALID_EVERY = int(os.getenv("PRODUCER_INVALID_EVERY", "25"))  # 0 disables


def main() -> None:
    stream = load_stream()
    log.info("replaying %d tweets at %.1f/s into %s", len(stream), RATE, config.INGEST_URL)
    sent = 0
    with httpx.Client(timeout=10) as http:
        while True:
            for msg in stream:
                body = dict(msg)
                if INVALID_EVERY and sent and sent % INVALID_EVERY == 0:
                    body.pop("latitude")  # exercise schema validation (expect HTTP 400)
                try:
                    r = http.post(config.INGEST_URL, json=body)
                    if r.status_code != 200:
                        log.info("tweet %s rejected: %s", body["tweet_id"], r.status_code)
                except httpx.HTTPError as e:
                    log.info("ingest not reachable yet: %s", e)
                    time.sleep(3)
                sent += 1
                time.sleep(1 / RATE)
            if not LOOP:
                break
            # Re-stamp ids so the next pass creates new documents instead of upserts.
            stream = [{**m, "tweet_id": m["tweet_id"] + len(stream)} for m in stream]


if __name__ == "__main__":
    main()
