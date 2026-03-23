"""server/store.py"""
import threading
import time


class KeyValueStore:
    """
    A simple in-memory key-value store with methods to set, get, and delete
    values by key. Returns "OK" on successful set, the value or None on get,
    and 1 or 0 on delete to indicate success.
    """

    def __init__(self):
        self.data = {}
        self.expiry = {}  # To store expiration times for keys
        self.lock = threading.Lock()  # To ensure thread safety for concurrent access

    def _is_expired(self, key):
        """Check if a key has expired."""
        if key not in self.expiry:
            return False
        return time.time() >= self.expiry[key]

    def _cleanup_if_expired(self, key):
        """Remove expired keys from the store."""
        if self._is_expired(key):
            self.data.pop(key, None)
            self.expiry.pop(key, None)
            return True
        return False

    def set(self, key, value):
        """Set a key-value pair in the store."""
        with self.lock:
            self.data[key] = value
            # Remove any existing expiry for the key
            self.expiry.pop(key, None)
            return "OK"

    def get(self, key):
        """Get the value associated with a key."""
        with self.lock:
            self._cleanup_if_expired(key)
            return self.data.get(key)

    def delete(self, key):
        """Delete a key from the store. Returns 1 if deleted, 0 if not found."""
        with self.lock:
            self._cleanup_if_expired(key)

            if key in self.data:
                del self.data[key]
                self.expiry.pop(key, None)
                return 1
            return 0

    def exists(self, key):
        """Check if a key exists in the store. Returns 1 if exists, 0 if not."""
        with self.lock:
            self._cleanup_if_expired(key)
            return 1 if key in self.data else 0

    def keys(self):
        """Return a list of all keys in the store."""
        with self.lock:
            expired_keys = [key for key in self.data if self._is_expired(key)]
            for key in expired_keys:
                self.data.pop(key, None)
                self.expiry.pop(key, None)

            return sorted(self.data.keys())

    def flushall(self):
        """Clear all key-value pairs from the store."""
        with self.lock:
            count = len(self.data)
            self.data.clear()
            self.expiry.clear()
            return count

    def incr(self, key):
        """Increment the integer value of a key by one.
        If the key does not exist, it is set to 1."""
        with self.lock:
            self._cleanup_if_expired(key)

            if key not in self.data:
                self.data[key] = "1"
                self.expiry.pop(key, None)  # Remove any existing expiry
                return 1

            value = self.data[key]

            try:
                number = int(value)
            except ValueError as e:
                raise ValueError("value is not an integer") from e

            number += 1
            self.data[key] = str(number)
            return number

    def expire(self, key, seconds):
        """Set a timeout on a key. Returns 1 if the timeout was set,
        0 if the key does not exist."""

        with self.lock:
            self._cleanup_if_expired(key)

            if key not in self.data:
                return 0

            self.expiry[key] = time.time() + seconds
            return 1

    def ttl(self, key):
        """Return the remaining time to live of a key in seconds.
        Returns -2 if the key does not exist."""

        with self.lock:
            self._cleanup_if_expired(key)

            if key not in self.data:
                return -2

            if key not in self.expiry:
                return -1

            remaining = int(self.expiry[key] - time.time())
            return max(remaining, 0)

    def debug_dump(self):
        with self.lock:
            return {
                "data": dict(self.data),
                "expiry": dict(self.expiry),
            }
