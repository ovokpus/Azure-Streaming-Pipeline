"""The Azure Functions app (Python v2 model), exercised with azure-functions test doubles."""
import json
from pathlib import Path

import azure.functions as func

import function_app
from stream.sample import generate

FUNC_DIR = Path(__file__).resolve().parents[1] / "azure-func"


def _user_fn(name: str):
    """Unwrap the decorated function the way Microsoft Learn's unit-testing guide shows."""
    return getattr(function_app, name).build().get_user_function()


http_fn = _user_fn("tweets_to_blob_and_event_hub")
eh_fn = _user_fn("event_hub_to_cosmos")


class Out:
    def __init__(self):
        self.value = None

    def set(self, v):
        self.value = v

    def get(self):
        return self.value


def _req(body: bytes) -> func.HttpRequest:
    return func.HttpRequest(method="POST", url="/api/TriggerTweetsToBlobAndEventHub", body=body)


def test_http_function_writes_blob_and_event():
    body = json.dumps(generate(1)[0]).encode()
    blob, eh = Out(), Out()
    resp = http_fn(_req(body), blob, eh)
    assert resp.status_code == 200
    assert blob.value == body and eh.value == body


def test_http_function_rejects_invalid():
    t = generate(1)[0]
    t.pop("tweet")
    blob, eh = Out(), Out()
    resp = http_fn(_req(json.dumps(t).encode()), blob, eh)
    assert resp.status_code == 400
    assert blob.value is None and eh.value is None


def test_eventhub_function_keeps_whole_batch():
    tweets = generate(5)
    events = [func.EventHubEvent(body=json.dumps(t).encode()) for t in tweets]
    out = Out()
    eh_fn(events, out)
    assert [d["id"] for d in out.value] == [str(t["tweet_id"]) for t in tweets]


def test_v2_model_registers_both_functions_with_expected_bindings():
    fns = {f.get_function_name(): json.loads(f.get_function_json()) for f in function_app.app.get_functions()}
    assert set(fns) == {"TriggerTweetsToBlobAndEventHub", "EventHubTriggerTweetsToCosmosDB"}
    http_types = {b["type"] for b in fns["TriggerTweetsToBlobAndEventHub"]["bindings"]}
    assert http_types == {"httpTrigger", "http", "blob", "eventHub"}
    eh = {b["type"]: b for b in fns["EventHubTriggerTweetsToCosmosDB"]["bindings"]}
    assert eh["eventHubTrigger"]["cardinality"].lower() == "many"
    assert eh["cosmosDB"]["containerName"] == "%COSMOS_CONTAINER%"


def test_no_function_json_and_bundle_4x():
    assert not list(FUNC_DIR.rglob("function.json"))
    host = json.loads((FUNC_DIR / "host.json").read_text())
    assert host["extensionBundle"]["version"] == "[4.0.0, 5.0.0)"


def test_event_hub_annotation_uses_typing_list():
    # The worker indexer silently drops a function annotated with list[...] (see function_app.py).
    src = (FUNC_DIR / "function_app.py").read_text()
    assert "typing.List[func.EventHubEvent]" in src
