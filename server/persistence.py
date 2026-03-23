"""Persistence layer for the Redis clone server."""

import json
import os


class SnapshotManager:
    """Manages saving and loading the key-value store data to and
    from a file."""

    def __init__(self, filepath):
        self.filepath = filepath

    def save(self, data, expiry):
        """Save the current state of the key-value store to a file."""

        payload = {
            "data": data,
            "expiry": expiry,
        }

        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

        with open(self.filepath, "w", encoding="utf-8") as file:
            json.dump(payload, file)

    def load(self):
        """Load the key-value store data from a file."""

        if not os.path.exists(self.filepath):
            return {}, {}

        with open(self.filepath, "r", encoding="utf-8") as file:
            payload = json.load(file)

        data = payload.get("data", {})
        expiry = payload.get("expiry", {})

        return data, expiry
