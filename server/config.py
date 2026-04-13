"""Configuration for the Redis clone server."""

import os

HOST = os.getenv("REDIS_HOST", "127.0.0.1")
PORT = 6379

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT_PATH = os.path.join(BASE_DIR, "..", "data", "snapshot.json")
