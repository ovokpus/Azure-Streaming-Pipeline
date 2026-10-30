import json
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from stream import api
from stream.sample import generate


@pytest.fixture
def client(monkeypatch):
    blob = MagicMock()
    monkeypatch.setattr(api, "blob_service", lambda: blob)
    api.state.producer = MagicMock()
    api.state.ready.update(azurite=True, eventhub=True, cosmos=True)
    api.state.accepted = api.state.rejected = 0
    yield TestClient(api.app), blob
    api.state.producer = None


def test_ingest_valid_writes_blob_and_sends(client):
    c, blob = client
    r = c.post("/api/tweets", content=json.dumps(generate(1)[0]))
    assert r.status_code == 200 and "blob=tweets/" in r.text
    blob.get_blob_client.return_value.upload_blob.assert_called_once()
    api.state.producer.send_batch.assert_called_once()
    assert api.state.accepted == 1


def test_ingest_invalid_is_400_and_counted(client):
    c, blob = client
    t = generate(1)[0]
    t.pop("latitude")
    r = c.post("/api/tweets", content=json.dumps(t))
    assert r.status_code == 400
    assert api.state.rejected == 1
    blob.get_blob_client.assert_not_called()


def test_ingest_503_while_starting(client):
    c, _ = client
    api.state.producer = None
    assert c.post("/api/tweets", content=json.dumps(generate(1)[0])).status_code == 503


def test_health(client):
    c, _ = client
    assert c.get("/health").json()["status"] == "ok"
