import time
import hashlib

from app.config import settings
from app.models.ollama_client import OllamaClient

from app.fallback.cache import ResponseCache
from app.fallback.circuit_breaker import CircuitBreaker

from app.observability.metrics import (
    FALLBACK_COUNT,
    LLM_LATENCY
)


class FallbackRouter:
    """
    Resilient LLM Router with:
    - Circuit breakers
    - Retries
    - Cache fallback
    - Policy control hooks
    """

    def __init__(self):

        self.client = OllamaClient()

        # Models
        self.primary = settings.PRIMARY_MODEL
        self.secondary = settings.SECONDARY_MODEL

        # Circuit breakers (EXPOSED)
        self.primary_cb = CircuitBreaker()
        self.secondary_cb = CircuitBreaker()

        # Cache
        self.cache = ResponseCache(
            ttl=settings.CACHE_TTL,
            max_size=settings.CACHE_MAX_SIZE
        )

        # Retry config
        self.max_retries = settings.MAX_RETRIES

        # Policy flags
        self.force_cache_only = False
        self.primary_disabled = False

    # --------------------------------
    # Policy Control Hooks
    # --------------------------------

    def disable_primary(self):
        self.primary_disabled = True
        print("[ROUTER] Primary model disabled")

    def enable_primary(self):
        self.primary_disabled = False
        print("[ROUTER] Primary model enabled")

    def prefer_cache(self):
        self.force_cache_only = True
        print("[ROUTER] Cache-only mode enabled")

    def normal_mode(self):
        self.force_cache_only = False
        print("[ROUTER] Normal routing restored")

    # --------------------------------

    def _hash_prompt(self, prompt: str) -> str:

        return hashlib.sha256(
            prompt.encode()
        ).hexdigest()

    # --------------------------------

    def _call_model(self, model: str, prompt: str) -> str:

        start = time.time()

        result = self.client.generate(
            model,
            prompt
        )

        latency = time.time() - start

        LLM_LATENCY.observe(latency)

        return result

    # --------------------------------

    def _try_model(
        self,
        model: str,
        breaker: CircuitBreaker,
        prompt: str
    ):

        if not breaker.can_execute():
            raise RuntimeError("Circuit open")

        breaker.register_trial()

        try:

            result = self._call_model(
                model,
                prompt
            )

            breaker.record_success()

            return result

        except Exception:

            breaker.record_failure()

            raise

    # --------------------------------

    def generate(self, prompt: str) -> str:

        key = self._hash_prompt(prompt)

        # ----------------------------
        # Cache-first mode
        # ----------------------------

        if self.force_cache_only:

            cached = self.cache.get(key)

            if cached:
                return cached

            raise RuntimeError("Cache-only mode: no entry")

        # ----------------------------
        # Normal cache lookup
        # ----------------------------

        cached = self.cache.get(key)

        if cached:
            return cached

        last_error = None

        # ----------------------------
        # Primary model
        # ----------------------------

        if not self.primary_disabled:

            for _ in range(self.max_retries + 1):

                try:

                    result = self._try_model(
                        self.primary,
                        self.primary_cb,
                        prompt
                    )

                    self.cache.set(key, result)

                    return result

                except Exception as e:

                    last_error = e

                    FALLBACK_COUNT.inc()

        # ----------------------------
        # Secondary model
        # ----------------------------

        try:

            result = self._try_model(
                self.secondary,
                self.secondary_cb,
                prompt
            )

            self.cache.set(key, result)

            return result

        except Exception as e:

            last_error = e

            FALLBACK_COUNT.inc()

        # ----------------------------
        # Final cache fallback
        # ----------------------------

        cached = self.cache.get(key)

        if cached:
            return cached

        raise RuntimeError(
            f"All models failed: {last_error}"
        )
