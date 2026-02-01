import yaml
import time


class SLOEvaluator:
    """
    Evaluates SLO compliance and error budgets
    """

    def __init__(self, config_path="policies/slo_config.yaml"):

        self.config_path = config_path

        self.config = self._load()

        # In-memory metrics history (Phase 6 → DB)
        self.history = {
            "requests": [],
            "failures": [],
            "latency": [],
            "groundedness": [],
            "hallucinations": [],
            "fallbacks": []
        }

    # --------------------------------

    def _load(self):

        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    # --------------------------------
    # Recording
    # --------------------------------

    def record_request(self, success=True):

        self.history["requests"].append(time.time())

        if not success:
            self.history["failures"].append(time.time())

    def record_latency(self, value):

        self.history["latency"].append(
            (time.time(), value)
        )

    def record_groundedness(self, value):

        self.history["groundedness"].append(
            (time.time(), value)
        )

    def record_hallucination(self):

        self.history["hallucinations"].append(
            time.time()
        )

    def record_fallback(self):

        self.history["fallbacks"].append(
            time.time()
        )

    # --------------------------------
    # Helpers
    # --------------------------------

    def _window(self, data, days):

        cutoff = time.time() - days * 86400

        return [
            x for x in data
            if (x if isinstance(x, float) else x[0]) >= cutoff
        ]

    # --------------------------------
    # SLO Evaluation
    # --------------------------------

    def availability_slo(self):

        cfg = self.config["slo"]["availability"]

        window = cfg["window_days"]

        req = self._window(self.history["requests"], window)
        fail = self._window(self.history["failures"], window)

        total = len(req)

        if total == 0:
            return 1.0

        return (total - len(fail)) / total

    def latency_slo(self):

        cfg = self.config["slo"]["latency"]

        window = cfg["window_days"]

        limit = cfg["p95_ms"] / 1000

        data = self._window(
            self.history["latency"],
            window
        )

        if not data:
            return True

        values = sorted([x[1] for x in data])

        p95 = values[int(0.95 * len(values))]

        return p95 <= limit

    def hallucination_rate(self):

        cfg = self.config["slo"]["hallucination_rate"]

        window = cfg["window_days"]

        req = self._window(self.history["requests"], window)

        hall = self._window(
            self.history["hallucinations"],
            window
        )

        if not req:
            return 0.0

        return len(hall) / len(req)

    def fallback_rate(self):

        cfg = self.config["slo"]["fallback_rate"]

        window = cfg["window_days"]

        req = self._window(self.history["requests"], window)

        fb = self._window(
            self.history["fallbacks"],
            window
        )

        if not req:
            return 0.0

        return len(fb) / len(req)

    # --------------------------------
    # Summary
    # --------------------------------

    def evaluate(self):

        availability = self.availability_slo()

        hallucination = self.hallucination_rate()

        fallback = self.fallback_rate()

        latency_ok = self.latency_slo()

        return {
            "availability": availability,
            "availability_ok": availability >=
            self.config["slo"]["availability"]["target"],

            "latency_ok": latency_ok,

            "hallucination_rate": hallucination,
            "hallucination_ok": hallucination <=
            self.config["slo"]["hallucination_rate"]["max_rate"],

            "fallback_rate": fallback,
            "fallback_ok": fallback <=
            self.config["slo"]["fallback_rate"]["max_rate"],
        }
