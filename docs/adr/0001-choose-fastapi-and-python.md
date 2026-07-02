# ADR 0001 — Backend framework & language

Date: 2026-01-15  ·  Status: Accepted

## Context
We need a backend that (a) integrates well with the AI/ML ecosystem, (b) supports async I/O for streaming telemetry and LLM calls, (c) has a mature schema-first HTTP layer, and (d) will be maintainable by both platform and ML engineers.

## Decision
Use **Python 3.12 + FastAPI 0.115** for HTTP services. Use **Celery + Dramatiq** for long-running async work. Data access via **SQLAlchemy 2 async** with **asyncpg**.

## Alternatives considered
- **Go + chi** — fastest single-node throughput, but forces a separate ML runtime and duplicates schemas across languages. Rejected: the marginal RPS win is dwarfed by the pipeline latency cost.
- **Node + NestJS** — good ergonomics, but the Anthropic/vector/simulation ecosystem is Python-first.
- **Rust + Axum** — considered for the bridge-svc (hardware I/O). Kept as an option for that one service only.

## Consequences
- Uniform Python stack across API, worker, and simulation.
- Type hints + Pydantic 2 give us schema-first request/response with OpenAPI generation.
- We must invest in careful async patterns (no sync I/O in coroutine paths).
