import random
import time
import yaml
import threading

from app.observability.metrics import CHAOS_EVENTS


class FaultInjector:
    """
    Chaos Engineering Fault Injection Engine for LLM Pipelines
    """

    def __init__(self, config_path: str):

        self.config_path = config_path

        self._lock = threading.Lock()

        self.config = self._load_config()

        self.enabled = self.config.get("enabled", False)

        self.faults = self.config.get("faults", {})

    # ----------------------------------
    # Config Management
    # ----------------------------------

    def _load_config(self) -> dict:

        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f) or {}

        except Exception as e:

            print(f"[CHAOS] Failed to load config: {e}")

            return {"enabled": False}

    def reload(self):
        """
        Reload chaos config at runtime
        """

        with self._lock:

            self.config = self._load_config()

            self.enabled = self.config.get("enabled", False)

            self.faults = self.config.get("faults", {})

    # ----------------------------------
    # Internal Helpers
    # ----------------------------------

    def _should_inject(self, fault_name: str) -> bool:

        if not self.enabled:
            return False

        fault = self.faults.get(fault_name, {})

        if not fault.get("enabled", False):
            return False

        probability = fault.get("probability", 0.0)

        return random.random() < probability

    def _record_event(self, fault_name: str):

        try:
            CHAOS_EVENTS.labels(fault_name).inc()
        except Exception:
            pass

    # ----------------------------------
    # Fault Injection Hooks
    # ----------------------------------

    def before_retrieval(self, query: str) -> str:

        # Latency Injection
        if self._should_inject("inject_latency"):

            delay_ms = self.faults["inject_latency"].get(
                "delay_ms", 1000
            )

            self._record_event("inject_latency")

            time.sleep(delay_ms / 1000)

        return query

    def after_retrieval(self, chunks):

        # Drop Retrieval
        if self._should_inject("drop_retrieval"):

            self._record_event("drop_retrieval")

            return []

        # Corrupt Context
        if self._should_inject("corrupt_context") and chunks:

            self._record_event("corrupt_context")

            corrupted = list(chunks)

            random.shuffle(corrupted)

            corrupted[0] = "### CORRUPTED CONTEXT ###"

            return corrupted

        return chunks

    def before_llm(self, prompt: str) -> str:

        # Token Overflow Simulation
        if self._should_inject("overflow_prompt"):

            max_tokens = self.faults["overflow_prompt"].get(
                "max_tokens", 200
            )

            self._record_event("overflow_prompt")

            if len(prompt) > 0:

                repeat_factor = max_tokens // max(len(prompt), 1) + 5

                prompt = prompt * repeat_factor

        return prompt

    def after_llm(self, response: str) -> str:

        # Simulate Model Crash
        if self._should_inject("kill_model"):

            self._record_event("kill_model")

            raise RuntimeError("Injected model crash (chaos testing)")

        return response
