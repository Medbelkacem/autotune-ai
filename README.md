# AutoTune AI

> AI-powered ECU intelligence platform — explainable, safety-bounded, human-in-the-loop.

[![CI](https://github.com/autotune-ai/autotune/actions/workflows/ci.yml/badge.svg)](./.github/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](./LICENSE)

---

## What is this?

AutoTune AI helps professional tuners, workshops, OEMs, and fleet operators **understand** ECU calibrations rather than blindly edit them. It identifies vehicles, reads ECU metadata, reasons over calibration data with an LLM-grounded knowledge base, and produces safety-scored, traceable recommendations.

See [`AUTOTUNE_AI_ARCHITECTURE.md`](./AUTOTUNE_AI_ARCHITECTURE.md) for the full architecture spec.

## Monorepo Layout

```
.
├── services/
│   ├── api/                # FastAPI backend (auth, vehicles, ecu, analysis, recommend, telemetry)
│   └── analysis-worker/    # Celery worker for long-running AI/sim jobs
├── apps/
│   ├── web/                # Next.js 15 workshop dashboard
│   └── mobile/             # React Native tuner app (iOS + Android)
├── packages/
│   └── shared-schemas/     # Pydantic + TypeScript types shared across stack
├── infra/
│   ├── docker/             # Dockerfiles + docker-compose for local dev
│   ├── k8s/                # Kubernetes manifests + Helm chart
│   └── terraform/          # AWS + Azure IaC
├── scripts/                # Bootstrap, seed, dev-loop scripts
└── docs/adr/               # Architecture Decision Records
```

## Quick Start (local dev)

Requirements: Docker 24+, Make, Python 3.12, Node 20+, pnpm 9+.

```bash
# 1. clone + bootstrap
git clone <repo> && cd auto
cp .env.example .env
make bootstrap          # installs deps + pulls model weights + builds containers

# 2. start the stack
make up                 # postgres, redis, rabbitmq, qdrant, neo4j, api, worker, web
make migrate            # apply Alembic migrations
make seed               # load demo vehicles + knowledge graph

# 3. open
open http://localhost:3000   # web dashboard
open http://localhost:8000/docs   # API (Swagger)
```

## Service Map

| Service | Port | Tech | Purpose |
|---|---|---|---|
| api | 8000 | FastAPI 0.115 | REST + WebSocket gateway |
| analysis-worker | — | Celery + Dramatiq | Async AI / sim jobs |
| web | 3000 | Next.js 15 | Workshop dashboard |
| postgres | 5432 | Postgres 16 + pgvector | OLTP + vectors |
| timescaledb | 5433 | Timescale 2.x | Telemetry time-series |
| redis | 6379 | Redis 7 | Cache + sessions + rate-limit |
| rabbitmq | 5672 | RabbitMQ 3.13 | Command queue |
| qdrant | 6333 | Qdrant 1.x | High-recall vector search |
| neo4j | 7687 | Neo4j 5 Community | Calibration knowledge graph |
| minio | 9000 | MinIO | S3-compatible blob (firmware, A2L) |

## Make Targets

```
make help          # list all targets
make bootstrap     # one-time setup
make up / down     # start / stop stack
make migrate       # alembic upgrade head
make seed          # demo data
make test          # backend + frontend tests
make lint          # ruff + eslint + prettier
make typecheck     # mypy + tsc
make ai-eval       # golden-set evaluation of the AI orchestrator
```

## Security Notes

- This repository contains **no** ECU write routines bundled by default. Writing to ECUs requires a credentialed `tuner` role and a hardware-backed signature.
- All AI outputs are simulation-only until signed. See `services/api/app/core/policy.py`.
- The platform refuses to generate defeat-device modifications (DPF/EGR/AdBlue removal).

## License

Proprietary. © AutoTune AI, Inc. All rights reserved.
