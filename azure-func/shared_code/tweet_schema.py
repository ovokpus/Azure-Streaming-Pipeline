"""Tweet message contract shared by the Azure Function and the local stand-in API."""

import json
from typing import Any

import jsonschema

tweet_schema = {
    "type": "object",
    "properties": {
        "tweet_id": {"type": "integer"},
        "account_id": {"type": "integer"},
        "likes": {"type": "integer"},
        "replies": {"type": "integer"},
        "retweets": {"type": "integer"},
        "tweet": {"type": "string"},
        "time": {"type": "integer"},
        "year_month_date": {"type": "string"},
        "damage_flag": {"type": "string"},
        "image_base64": {"type": "string"},
        "latitude": {"type": "number"},
        "longitude": {"type": "number"},
    },
    "required": [
        "tweet_id", "account_id", "likes", "replies", "retweets",
        "tweet", "time", "damage_flag", "latitude", "longitude",
    ],
}


class TweetValidationError(ValueError):
    """Raised for invalid JSON or a schema violation; maps to HTTP 400."""


def parse_and_validate(body: bytes | str) -> dict[str, Any]:
    try:
        doc = json.loads(body)
    except json.JSONDecodeError as err:
        raise TweetValidationError(f"Invalid json passed! Error: {err}") from err
    try:
        jsonschema.validate(instance=doc, schema=tweet_schema)
    except jsonschema.exceptions.ValidationError as err:
        raise TweetValidationError(f"JSON Schema is not valid! Error: {err.message}") from err
    return doc


def to_cosmos_document(doc: dict[str, Any]) -> dict[str, Any]:
    """Cosmos needs a string `id`; the Functions binding generated one, we derive it."""
    return {**doc, "id": str(doc["tweet_id"])}
