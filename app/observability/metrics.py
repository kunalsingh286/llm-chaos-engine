from prometheus_client import Counter, Histogram


REQUEST_COUNT = Counter(
    "llm_requests_total",
    "Total number of LLM requests"
)

REQUEST_LATENCY = Histogram(
    "llm_request_latency_seconds",
    "Latency of full pipeline"
)

RETRIEVAL_LATENCY = Histogram(
    "retrieval_latency_seconds",
    "Latency of vector retrieval"
)

LLM_LATENCY = Histogram(
    "llm_latency_seconds",
    "Latency of LLM generation"
)

FALLBACK_COUNT = Counter(
    "llm_fallback_total",
    "Number of fallback executions"
)

CHAOS_EVENTS = Counter(
    "chaos_events_total",
    "Total chaos fault injections",
    ["fault_type"]
)
