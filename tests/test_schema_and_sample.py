import base64
import json

import pytest

from shared_code.tweet_schema import TweetValidationError, parse_and_validate, to_cosmos_document
from stream.sample import generate


def test_sample_is_deterministic_and_valid():
    a, b = generate(50), generate(50)
    assert a == b
    for t in a:
        parse_and_validate(json.dumps(t).encode())


def test_sample_images_are_png():
    imgs = [t["image_base64"] for t in generate(100) if "image_base64" in t]
    assert 40 < len(imgs) < 80
    assert base64.b64decode(imgs[0]).startswith(b"\x89PNG")


def test_missing_required_field_rejected():
    t = generate(1)[0]
    t.pop("latitude")
    with pytest.raises(TweetValidationError, match="latitude"):
        parse_and_validate(json.dumps(t))


def test_bad_json_rejected():
    with pytest.raises(TweetValidationError):
        parse_and_validate(b"{not json")


def test_cosmos_document_has_string_id():
    doc = to_cosmos_document(generate(1)[0])
    assert doc["id"] == str(doc["tweet_id"])
