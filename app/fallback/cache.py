import time


class ResponseCache:
    """
    Simple in-memory LRU-style cache
    """

    def __init__(self, ttl=300, max_size=200):

        self.ttl = ttl
        self.max_size = max_size

        self.cache = {}

    def get(self, key: str):

        entry = self.cache.get(key)

        if not entry:
            return None

        value, ts = entry

        if time.time() - ts > self.ttl:
            del self.cache[key]
            return None

        return value

    def set(self, key: str, value: str):

        if len(self.cache) >= self.max_size:

            # Remove oldest
            oldest = min(
                self.cache.items(),
                key=lambda x: x[1][1]
            )[0]

            del self.cache[oldest]

        self.cache[key] = (value, time.time())
