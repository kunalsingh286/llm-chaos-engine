import json
import time
import os


class ShadowLogger:
    """
    Stores sampled real queries for replay
    """

    def __init__(self, path="data/shadow_logs.jsonl", sample_rate=0.1):

        self.path = path
        self.sample_rate = sample_rate

        os.makedirs(
            os.path.dirname(path),
            exist_ok=True
        )

    def log(self, query: str):

        import random

        if random.random() > self.sample_rate:
            return

        entry = {
            "timestamp": time.time(),
            "query": query
        }

        with open(self.path, "a") as f:
            f.write(json.dumps(entry) + "\n")
