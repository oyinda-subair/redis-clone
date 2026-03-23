"""server/store.py"""


class KeyValueStore:
    """
    A simple in-memory key-value store with methods to set, get, and delete
    values by key. Returns "OK" on successful set, the value or None on get,
    and 1 or 0 on delete to indicate success.
    """

    def __init__(self):
        self.data = {}

    def set(self, key, value):
        """Set a key-value pair in the store."""
        self.data[key] = value
        return "OK"

    def get(self, key):
        """Get the value associated with a key."""
        return self.data.get(key)

    def delete(self, key):
        """Delete a key from the store. Returns 1 if deleted, 0 if not found."""
        if key in self.data:
            del self.data[key]
            return 1
        return 0

    def exists(self, key):
        """Check if a key exists in the store. Returns 1 if exists, 0 if not."""
        return 1 if key in self.data else 0
