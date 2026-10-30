"""Deterministic SYNTHETIC tweet + satellite-tile stream in the pipeline's message schema.

The original Kaggle datasets (Hurricane Harvey tweets, hurricane-damage satellite
images) need a Kaggle login and are not redistributable here, so the local demo
replays generated messages instead. Text, coordinates and images are fabricated;
only the *shape* matches the real merged stream. To use the real data, run the
scripts in preprocessing/ and point SAMPLE_PATH at the merged JSON.
"""

import base64
import json
import os
import random
import struct
import zlib
from datetime import datetime, timezone

TEMPLATES = [
    "Water rising fast on {street} near {area}. Stay off the roads #HurricaneHarvey",
    "Power is out across {area}, wind gusts getting stronger #Harvey",
    "Shelter open at {area} community center, bring ID and medication #HarveyRelief",
    "Roof damage on our block in {area}, everyone safe for now #Harvey",
    "Rain bands keep coming over {area}. Bayou already over its banks #HoustonFlood",
    "Volunteers with boats needed on {street}, {area} #CajunNavy #Harvey",
    "Trees down across {street} in {area}, crews on the way",
    "{area} still dry but the sky looks terrible. Praying for the coast #HurricaneHarvey",
]
AREAS = ["Rockport", "Port Aransas", "Victoria", "Katy", "Kingwood", "Pearland",
         "Baytown", "Dickinson", "Beaumont", "Port Arthur", "Cypress", "Sugar Land"]
STREETS = ["Main St", "Westheimer Rd", "Memorial Dr", "FM 1960", "Hwy 35", "Bay Area Blvd"]


def _png(width: int, height: int, pixels: list[tuple[int, int, int]]) -> bytes:
    raw = b"".join(b"\x00" + b"".join(bytes(p) for p in pixels[y * width:(y + 1) * width])
                   for y in range(height))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def synthetic_tile(rng: random.Random, damage: bool, size: int = 24) -> str:
    """A tiny fake 'satellite' tile: greens for intact, browns/greys with debris for damage."""
    base = (96, 80, 62) if damage else (70, 120, 64)
    px = []
    for _ in range(size * size):
        j = rng.randint(-25, 25)
        if damage and rng.random() < 0.18:
            px.append(tuple(max(0, min(255, 170 + j)) for _ in range(3)))
        else:
            px.append(tuple(max(0, min(255, c + j)) for c in base))
    return base64.b64encode(_png(size, size, px)).decode()


def generate(n: int = 500, seed: int = 30) -> list[dict]:
    rng = random.Random(seed)
    start = int(datetime(2017, 8, 25, 6, tzinfo=timezone.utc).timestamp() * 1000)
    out = []
    for i in range(n):
        damage = rng.random() < 0.45
        area = rng.choice(AREAS)
        msg = {
            "tweet_id": 100_000 + i,
            "account_id": 1 + i // 100,  # same artificial grouping as process_tweets.py
            "likes": int(rng.expovariate(1 / 6)),
            "replies": int(rng.expovariate(1 / 2)),
            "retweets": int(rng.expovariate(1 / 4)),
            "tweet": rng.choice(TEMPLATES).format(area=area, street=rng.choice(STREETS)),
            "time": start + i * 37_000,
            "year_month_date": "2017-08-25",
            "damage_flag": "damage" if damage else "no_damage",
            "latitude": round(rng.uniform(28.9, 30.4), 6),
            "longitude": round(rng.uniform(-97.2, -93.8), 6),
        }
        if rng.random() < 0.6:  # about 60% of tweets carry an image, as in the merged stream
            msg["image_base64"] = synthetic_tile(rng, damage)
        out.append(msg)
    return out


def load_stream() -> list[dict]:
    path = os.getenv("SAMPLE_PATH")
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as fp:
            return json.load(fp)
    return generate()
