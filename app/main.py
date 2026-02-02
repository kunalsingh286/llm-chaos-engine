import time

from fastapi import FastAPI
from starlette.responses import Response
from prometheus_client import generate_latest


# -----------------------------
# Schemas
# -----------------------------

from app.schemas.request import QueryRequest
from app.schemas.response import QueryResponse


# -----------------------------
# Core
# -----------------------------

from app.retrieval.vector_store import VectorStore
from app.chaos.fault_injector import FaultInjector
from app.fallback.router import FallbackRouter


# -----------------------------
# Quality
# -----------------------------

from app.quality.evaluator import QualityEvaluator


# -----------------------------
# Governance
# -----------------------------

from app.governance.slo import SLOEvaluator


# -----------------------------
# Policy + Incidents
# -----------------------------

from app.policy.engine import PolicyEngine
from app.policy.actions import PolicyActions
from app.incidents.manager import IncidentManager


# -----------------------------
# Replay
# -----------------------------

from app.replay.logger import ShadowLogger
from app.replay.runner import ReplayRunner


# -----------------------------
# Metrics
# -----------------------------

from app.observability.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    RETRIEVAL_LATENCY,
    HALLUCINATION_COUNT,
    QUALITY_SCORE,
)


# ======================================================
# App Init
# ======================================================

app = FastAPI(
    title="LLM Chaos Engineering Platform",
    version="1.0.0"
)


# -----------------------------
# Components
# -----------------------------

vector_store = VectorStore()

fault_injector = FaultInjector(
    "policies/chaos_config.yaml"
)

fallback_router = FallbackRouter()

quality_evaluator = QualityEvaluator()

slo_evaluator = SLOEvaluator()


# -----------------------------
# Policy System
# -----------------------------

policy_actions = PolicyActions(
    fault_injector,
    fallback_router
)

policy_engine = PolicyEngine(policy_actions)

incident_manager = IncidentManager()


# -----------------------------
# Replay System
# -----------------------------

shadow_logger = ShadowLogger()


def replay_client(prompt: str):
    return fallback_router.generate(prompt)


replay_runner = ReplayRunner(
    replay_client,
    fault_injector,
    fallback_router
)


# ======================================================
# Endpoints
# ======================================================

# -----------------------------
# Health
# -----------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "llm-chaos-engine",
        "version": "1.0.0"
    }


# -----------------------------
# Metrics
# -----------------------------

@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )


# -----------------------------
# Chaos Status
# -----------------------------

@app.get("/chaos")
def chaos_status():
    return {
        "enabled": fault_injector.enabled,
        "faults": fault_injector.faults
    }


# -----------------------------
# SLO Status
# -----------------------------

@app.get("/slo")
def slo_status():
    return slo_evaluator.evaluate()


# -----------------------------
# Incidents
# -----------------------------

@app.get("/incidents")
def list_incidents():
    return incident_manager.list()


# -----------------------------
# Replay
# -----------------------------

@app.post("/replay")
def run_replay():
    return replay_runner.run()


# ======================================================
# Main Query Pipeline
# ======================================================

@app.post("/query", response_model=QueryResponse)
def query_llm(request: QueryRequest):

    # --------------------------------
    # Request Tracking
    # --------------------------------

    REQUEST_COUNT.inc()

    slo_evaluator.record_request(success=True)

    start_total = time.time()

    # --------------------------------
    # Retrieval Phase
    # --------------------------------

    start_retrieval = time.time()

    # Chaos before retrieval
    query = fault_injector.before_retrieval(
        request.query
    )

    # Shadow traffic logging
    shadow_logger.log(query)

    chunks = vector_store.query(query)

    # Chaos after retrieval
    chunks = fault_injector.after_retrieval(
        chunks
    )

    retrieval_latency = time.time() - start_retrieval

    RETRIEVAL_LATENCY.observe(
        retrieval_latency
    )

    # --------------------------------
    # Prompt Construction
    # --------------------------------

    context = "\n".join(chunks)

    prompt = f"""
You are a reliable AI assistant.

Answer ONLY using the provided context.
If the answer is not in the context, say "I don't know".

Question:
{query}

Context:
{context}
"""

    # Chaos before LLM
    prompt = fault_injector.before_llm(
        prompt
    )

    # --------------------------------
    # Generation Phase
    # --------------------------------

    try:

        answer = fallback_router.generate(
            prompt
        )

        # Chaos after LLM
        answer = fault_injector.after_llm(
            answer
        )

    except Exception as e:

        # Failure record
        slo_evaluator.record_request(
            success=False
        )

        answer = (
            "System temporarily unavailable. "
            "Please retry later."
        )

        print(f"[PIPELINE ERROR] {e}")

    # --------------------------------
    # Quality Evaluation
    # --------------------------------

    quality = quality_evaluator.evaluate(
        answer=answer,
        context_chunks=chunks,
        question=query
    )

    QUALITY_SCORE.observe(
        quality["groundedness"]
    )

    slo_evaluator.record_groundedness(
        quality["groundedness"]
    )

    if quality["hallucinated"]:

        HALLUCINATION_COUNT.inc()

        slo_evaluator.record_hallucination()

    # --------------------------------
    # Latency
    # --------------------------------

    total_latency = time.time() - start_total

    REQUEST_LATENCY.observe(
        total_latency
    )

    slo_evaluator.record_latency(
        total_latency
    )

    # --------------------------------
    # Policy Evaluation
    # --------------------------------

    slo_state = slo_evaluator.evaluate()

    applied_policies = policy_engine.evaluate(
        slo_state
    )

    if applied_policies:

        incident_manager.create(
            slo_state,
            applied_policies
        )

    # --------------------------------
    # Response
    # --------------------------------

    return QueryResponse(
        answer=answer,
        retrieved_chunks=chunks,
        model_used="primary_or_secondary"
    )
