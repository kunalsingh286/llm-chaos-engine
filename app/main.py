import time

from fastapi import FastAPI
from prometheus_client import generate_latest
from starlette.responses import Response

# Schemas
from app.schemas.request import QueryRequest
from app.schemas.response import QueryResponse

# Core components
from app.retrieval.vector_store import VectorStore
from app.chaos.fault_injector import FaultInjector
from app.fallback.router import FallbackRouter
from app.quality.evaluator import QualityEvaluator

# Metrics
from app.observability.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    RETRIEVAL_LATENCY,
    HALLUCINATION_COUNT,
    QUALITY_SCORE,
)


# ----------------------------------
# App Initialization
# ----------------------------------

app = FastAPI(
    title="LLM Chaos Engineering Platform",
    version="0.4.0"
)

# System Components
vector_store = VectorStore()

fault_injector = FaultInjector(
    "policies/chaos_config.yaml"
)

fallback_router = FallbackRouter()

quality_evaluator = QualityEvaluator()


# ----------------------------------
# Health Endpoint
# ----------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "llm-chaos-engine",
        "version": "0.4.0"
    }


# ----------------------------------
# Metrics Endpoint (Prometheus)
# ----------------------------------

@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )


# ----------------------------------
# Chaos Status Endpoint
# ----------------------------------

@app.get("/chaos")
def chaos_status():
    return {
        "enabled": fault_injector.enabled,
        "faults": fault_injector.faults
    }


# ----------------------------------
# Main Query Endpoint
# ----------------------------------

@app.post("/query", response_model=QueryResponse)
def query_llm(request: QueryRequest):

    # -------------------------------
    # Request Tracking
    # -------------------------------

    REQUEST_COUNT.inc()

    start_total = time.time()

    # -------------------------------
    # Retrieval Phase
    # -------------------------------

    start_retrieval = time.time()

    # Chaos before retrieval
    query = fault_injector.before_retrieval(
        request.query
    )

    chunks = vector_store.query(query)

    # Chaos after retrieval
    chunks = fault_injector.after_retrieval(
        chunks
    )

    retrieval_latency = time.time() - start_retrieval

    RETRIEVAL_LATENCY.observe(
        retrieval_latency
    )

    # -------------------------------
    # Prompt Construction
    # -------------------------------

    context = "\n".join(chunks)

    prompt = f"""
You are a reliable AI assistant.

Answer the question using ONLY the provided context.

If the answer is not in the context,
say "I don't know based on the given information."

Question:
{query}

Context:
{context}
"""

    # Chaos before LLM
    prompt = fault_injector.before_llm(
        prompt
    )

    # -------------------------------
    # Generation Phase
    # -------------------------------

    try:

        answer = fallback_router.generate(
            prompt
        )

        # Chaos after LLM
        answer = fault_injector.after_llm(
            answer
        )

    except Exception as e:

        # Hard failure fallback
        print("[PIPELINE ERROR]", e)

        answer = (
            "System temporarily unavailable due to "
            "simulated failure. Please retry."
        )

    # -------------------------------
    # Quality Evaluation
    # -------------------------------

    quality = quality_evaluator.evaluate(
        answer=answer,
        context_chunks=chunks,
        question=query
    )

    QUALITY_SCORE.observe(
        quality["groundedness"]
    )

    if quality["hallucinated"]:
        HALLUCINATION_COUNT.inc()

    # Optional debug logging (remove later)
    if quality["hallucinated"]:
        print("[QUALITY WARNING]", quality)

    # -------------------------------
    # Total Latency
    # -------------------------------

    total_latency = time.time() - start_total

    REQUEST_LATENCY.observe(
        total_latency
    )

    # -------------------------------
    # Response
    # -------------------------------

    return QueryResponse(
        answer=answer,
        retrieved_chunks=chunks,
        model_used="primary_or_secondary"
    )
