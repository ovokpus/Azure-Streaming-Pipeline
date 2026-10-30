"""The deployed Azure Functions, exercised with azure-functions test doubles."""
import importlib
import json

import azure.functions as func

from stream.sample import generate

http_fn = importlib.import_module("TriggerTweetsToBlobAndEventHub")
eh_fn = importlib.import_module("EventHubTriggerTweetsToCosmosDB")


class Out:
    def __init__(self):
        self.value = None

    def set(self, v):
        self.value = v

    def get(self):
        return self.value


def _req(body: bytes) -> func.HttpRequest:
    return func.HttpRequest(method="POST", url="/api/tweets", body=body)


def test_http_function_writes_blob_and_event():
    body = json.dumps(generate(1)[0]).encode()
    blob, eh = Out(), Out()
    resp = http_fn.main(_req(body), blob, eh)
    assert resp.status_code == 200
    assert blob.value == body and eh.value == body


def test_http_function_rejects_invalid():
    t = generate(1)[0]
    t.pop("tweet")
    blob, eh = Out(), Out()
    resp = http_fn.main(_req(json.dumps(t).encode()), blob, eh)
    assert resp.status_code == 400
    assert blob.value is None and eh.value is None


def test_eventhub_function_keeps_whole_batch():
    tweets = generate(5)
    events = [func.EventHubEvent(body=json.dumps(t).encode()) for t in tweets]
    out = Out()
    eh_fn.main(events, out)
    assert [d["id"] for d in out.value] == [str(t["tweet_id"]) for t in tweets]
