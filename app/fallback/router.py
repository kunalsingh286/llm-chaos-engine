import time

from app.config import settings
from app.models.ollama_client import OllamaClient
from app.observability.metrics import (
    FALLBACK_COUNT,
    LLM_LATENCY
)


class FallbackRouter:
    def __init__(self):
        self.client = OllamaClient()

        self.primary = settings.PRIMARY_MODEL
        self.secondary = settings.SECONDARY_MODEL

    def _generate(self, model: str, prompt: str) -> str:
        start = time.time()

        result = self.client.generate(model, prompt)

        latency = time.time() - start
        LLM_LATENCY.observe(latency)

        return result

    def generate(self, prompt: str) -> str:
        try:
            return self._generate(self.primary, prompt)

        except Exception:
            FALLBACK_COUNT.inc()

            return self._generate(self.secondary, prompt)
