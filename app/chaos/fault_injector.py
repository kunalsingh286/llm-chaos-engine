import random
import time
import yaml
import threading

from app.observability.metrics import CHAOS_EVENTS


class FaultInjector:
    """
    Chaos Engineering Fault Injection Engine
    """

    def __init__(self, config_path: str):

        self.config_path = config_path

        self._lock = threading.Lock()

        self._load()

    # ----------------------------------
    # Config Handling
    # ----------------------------------

    def _load(self):

        try:
            with open(self.config_path, "r") as f:
                self.config = yaml.safe_load(f) or {}

        except Exception as e:

            print(f"[CHAOS] Config load failed: {e}")

            self.config = {}

        self.enabled = self.config.get("enabled", False)

        self.faults = self.config.get("faults", {})

    def reload(self):
        """
        Reload chaos configuration
        """

        with self._lock:
            self._load()

    # ----------------------------------
    # Internal Helpers
    # ----------------------------------

    def _should_inject(self, name: str) -> bool:

        if not self.enabled:
            return False

        fault = self.faults.get(name, {})

        if not fault.get("enabled", False):
            return False

        prob = fault.get("probability", 0.0)

        return random.random() < prob

    def _record(self, name: str):

        try:
            CHAOS_EVENTS.labels(name).inc()
        except Exception:
            pass

    # ----------------------------------
    # Hooks
    # ----------------------------------

    def before_retrieval(self, query: str) -> str:

        # Latency
        if self._should_inject("inject_latency"):

            delay = self.faults["inject_latency"].get(
                "delay_ms", 1000
            )

            self._record("inject_latency")

            time.sleep(delay / 1000)

        return query

    def after_retrieval(self, chunks):

        # Drop retrieval
        if self._should_inject("drop_retrieval"):

            self._record("drop_retrieval")

            return []

        # Corrupt context
        if self._should_inject("corrupt_context") and chunks:

            self._record("corrupt_context")

            corrupted = list(chunks)

            random.shuffle(corrupted)

            corrupted[0] = "### CORRUPTED CONTEXT ###"

            return corrupted

        return chunks

    def before_llm(self, prompt: str) -> str:

        # Overflow
        if self._should_inject("overflow_prompt"):

            max_tokens = self.faults["overflow_prompt"].get(
                "max_tokens", 200
            )

            self._record("overflow_prompt")

            if len(prompt) > 0:

                repeat = max_tokens // max(len(prompt), 1) + 5

                prompt = prompt * repeat

        return prompt

    def after_llm(self, response: str) -> str:

        # Kill model
        if self._should_inject("kill_model"):

            self._record("kill_model")

            raise RuntimeError("Injected model crash")

        return response
