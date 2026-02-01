from fastapi import FastAPI
from app.schemas.request import QueryRequest
from app.schemas.response import QueryResponse
from app.models.ollama_client import OllamaClient
from app.retrieval.vector_store import VectorStore
from app.chaos.fault_injector import FaultInjector
from app.fallback.router import FallbackRouter
from app.observability.metrics import REQUEST_COUNT, REQUEST_LATENCY
from prometheus_client import generate_latest

import time

app = FastAPI(title="LLM Chaos Engineering Platform")

ollama_client = OllamaClient()
vector_store = VectorStore()
fault_injector = FaultInjector()
fallback_router = FallbackRouter()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return generate_latest()


@app.post("/query", response_model=QueryResponse)
def query_llm(request: QueryRequest):
    REQUEST_COUNT.inc()
    start_time = time.time()

    query = fault_injector.before_retrieval(request.query)
    chunks = vector_store.query(query)
    chunks = fault_injector.after_retrieval(chunks)

    prompt = f"Answer the question:\n{query}\n\nContext:\n{chunks}"
    prompt = fault_injector.before_llm(prompt)

    answer = fallback_router.generate(prompt)
    answer = fault_injector.after_llm(answer)

    latency = time.time() - start_time
    REQUEST_LATENCY.observe(latency)

    return QueryResponse(
        answer=answer,
        retrieved_chunks=chunks,
        model_used="primary_or_secondary"
    )
