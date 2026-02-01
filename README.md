# LLM Chaos Engineering & Reliability Platform

## Overview
A production-style chaos engineering framework for LLM systems that intentionally
injects failures to test resilience, reliability, and observability of AI pipelines.

## Why This Exists
LLMs are probabilistic, brittle systems.
Most teams build demos. This platform builds failure-aware AI.

## Core Features
- Fault injection framework (Phase 2)
- Automatic fallback routing (Phase 3)
- Circuit breakers (Phase 3)
- Hallucination detection (Phase 4)
- SLO monitoring (Phase 5)
- Reliability dashboards (Phase 5)
- Policy-driven behavior control (Phase 6)
- Auto-generated incident postmortems (Phase 6)
- Shadow traffic replay testing (Phase 7)

## Architecture
FastAPI → Retrieval → LLM Router → Fallback → Metrics → Dashboards

## Failure Modes Simulated
- Hallucinations
- Empty retrieval
- Latency spikes
- Model crashes
- Token overflows

## Tech Stack
- LLMs: Ollama (llama3, mistral, phi-3)
- Backend: FastAPI
- Vector DB: Chroma / FAISS
- Metrics: Prometheus, Grafana
- Tracing: OpenTelemetry
- Storage: Postgres
- Policy Engine: YAML + Python
- Evaluation: LLM-as-judge

## How to Run (Phase 0)

1. Start Ollama locally:
   ```bash
   ollama run llama3
   ollama run mistral
