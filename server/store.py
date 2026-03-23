"""server/store.py"""
import threading

class KeyValueStore:
    """
    A simple in-memory key-value store with methods to set, get, and delete
    values by key. Returns "OK" on successful set, the value or None on get,
    and 1 or 0 on delete to indicate success.
    """

    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()  # To ensure thread safety for concurrent access

    def set(self, key, value):
        """Set a key-value pair in the store."""
        with self.lock:
            self.data[key] = value
            return "OK"

    def get(self, key):
        """Get the value associated with a key."""
        with self.lock:
            return self.data.get(key)

    def delete(self, key):
        """Delete a key from the store. Returns 1 if deleted, 0 if not found."""
        with self.lock:
            if key in self.data:
                del self.data[key]
                return 1
            return 0

    def exists(self, key):
        """Check if a key exists in the store. Returns 1 if exists, 0 if not."""
        with self.lock:
            return 1 if key in self.data else 0

    def keys(self):
        """Return a list of all keys in the store."""
        with self.lock:
            return sorted(self.data.keys())

    def flushall(self):
        """Clear all key-value pairs from the store."""
        with self.lock:
          count = len(self.data)
          self.data.clear()
          return count

    def incr(self, key):
        """Increment the integer value of a key by one.
        If the key does not exist, it is set to 1."""
        with self.lock:
            if key not in self.data:
                self.data[key] = "1"
                return 1

            value = self.data[key]

            try:
                number = int(value)
            except ValueError as e:
                raise ValueError("value is not an integer") from e

            number += 1
            self.data[key] = str(number)
            return number
