from app.config import settings


class PolicyActions:
    """
    System-level remediation actions
    """

    def __init__(
        self,
        chaos_engine,
        router
    ):

        self.chaos = chaos_engine
        self.router = router

    # -----------------------------

    def enable_safe_mode(self):

        settings.DEGRADED_MODE = True

        print("[POLICY] Safe mode enabled")

    def disable_safe_mode(self):

        settings.DEGRADED_MODE = False

        print("[POLICY] Safe mode disabled")

    def reduce_chaos(self):

        self.chaos.enabled = False

        print("[POLICY] Chaos disabled")

    def prefer_cache(self):

        self.router.prefer_cache()

        print("[POLICY] Prefer cache mode")

    def reduce_temperature(self):

        # Placeholder for Phase 7
        print("[POLICY] Reduce temperature")

    def rerank_retrieval(self):

        # Placeholder for Phase 7
        print("[POLICY] Rerank retrieval")

    def disable_primary_model(self):

        self.router.disable_primary()

        print("[POLICY] Primary model disabled")
