import json
import traceback

from app.replay.comparator import ReplayComparator


class ReplayRunner:
    """
    Replays shadow traffic under isolated conditions
    (best-effort, never crashes)
    """

    def __init__(
        self,
        client,
        chaos_engine,
        router,
        path="data/shadow_logs.jsonl"
    ):

        self.client = client
        self.chaos = chaos_engine
        self.router = router
        self.path = path

        self.comparator = ReplayComparator()

    # --------------------------------

    def _load(self):

        with open(self.path) as f:

            return [
                json.loads(line)
                for line in f
            ]

    # --------------------------------

    def _snapshot(self):

        return {
            "chaos": self.chaos.enabled,
            "cache_only": self.router.force_cache_only,
            "primary_disabled": self.router.primary_disabled
        }

    def _restore(self, snap):

        self.chaos.enabled = snap["chaos"]

        self.router.force_cache_only = snap["cache_only"]

        self.router.primary_disabled = snap["primary_disabled"]

    # --------------------------------

    def _safe_call(self, query):

        try:
            return self.client(query), None

        except Exception as e:

            return None, str(e)

    # --------------------------------

    def run(self):

        logs = self._load()

        results = []

        snapshot = self._snapshot()

        try:

            # Isolate replay
            self.chaos.enabled = False
            self.router.force_cache_only = False
            self.router.primary_disabled = False

            for entry in logs:

                query = entry["query"]

                # --------------------
                # Baseline
                # --------------------

                base, base_err = self._safe_call(query)

                # --------------------
                # Chaos
                # --------------------

                self.chaos.enabled = True

                chaos, chaos_err = self._safe_call(query)

                self.chaos.enabled = False

                # --------------------
                # Compare
                # --------------------

                if base and chaos:

                    diff = self.comparator.compare(
                        base,
                        chaos
                    )

                else:

                    diff = {
                        "similarity": 0.0,
                        "degraded": True,
                        "error": base_err or chaos_err
                    }

                results.append({
                    "query": query,
                    "baseline": base,
                    "chaos": chaos,
                    "comparison": diff,
                    "baseline_error": base_err,
                    "chaos_error": chaos_err
                })

        except Exception:

            traceback.print_exc()

        finally:

            self._restore(snapshot)

        return results
