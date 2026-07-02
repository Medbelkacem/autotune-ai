#!/usr/bin/env bash
# One-shot local dev: start data services in Docker, run the API on host Python.
#
# Usage:
#   ./scripts/run-local.sh          # first-time setup + start
#   ./scripts/run-local.sh restart  # skip install, just run migrations + start
#
# Requires: python3.12+, docker (as user or with sudo), network for pip install.

set -euo pipefail
cd "$(dirname "$0")/.."

# ─── 0. pick docker command ──────────────────────────────────────────
DOCKER_CMD="docker-compose"
if docker compose version >/dev/null 2>&1; then DOCKER_CMD="docker compose"; fi

SUDO=""
if ! docker ps >/dev/null 2>&1; then
  echo "→ using sudo for docker (you may be prompted for your password)"
  SUDO="sudo"
fi

COMPOSE="$SUDO $DOCKER_CMD -f infra/docker/docker-compose.minimal.yml --env-file .env"

# ─── 1. .env ────────────────────────────────────────────────────────
if [ ! -f .env ]; then
  cp .env.example .env
  echo "→ created .env from .env.example"
fi

# Point local API at the host-published ports (localhost, not container names).
export DATABASE_URL="postgresql+asyncpg://autotune:autotune@localhost:5432/autotune"
export REDIS_URL="redis://localhost:6379/0"
export RABBITMQ_URL="amqp://autotune:autotune@localhost:5672//"
export CELERY_BROKER_URL="$RABBITMQ_URL"
export CELERY_RESULT_BACKEND="redis://localhost:6379/2"
export QDRANT_URL="http://localhost:6333"
export NEO4J_URI="bolt://localhost:7687"
export SECRET_KEY="local-dev-secret-key-32-bytes-min-1234"
export PASSWORD_PEPPER="local-pepper-1234"
export APP_ENV="local"
export LOG_LEVEL="INFO"

# ─── 2. start data services ─────────────────────────────────────────
echo "→ starting postgres, redis, rabbitmq …"
$COMPOSE up -d

echo -n "→ waiting for postgres "
until $COMPOSE exec -T postgres pg_isready -U autotune -d autotune >/dev/null 2>&1; do
  echo -n "."; sleep 1
done
echo " ready"

# ─── 3. python venv ─────────────────────────────────────────────────
if [ ! -d .venv ]; then
  echo "→ creating virtualenv .venv/"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -q --upgrade pip

if [ "${1:-}" != "restart" ]; then
  echo "→ installing API dependencies (first time — a few minutes)…"
  pip install -q \
    "fastapi==0.115.0" "uvicorn[standard]==0.32.0" \
    "pydantic==2.9.2" "pydantic-settings==2.6.0" \
    "sqlalchemy[asyncio]==2.0.36" "asyncpg==0.29.0" "alembic==1.13.3" "psycopg2-binary==2.9.9" \
    "redis==5.1.1" "httpx==0.27.2" "python-jose[cryptography]==3.3.0" "passlib[argon2]==1.7.4" \
    "pynacl==1.5.0" "prometheus-fastapi-instrumentator==7.0.0" "slowapi==0.1.9" \
    "email-validator==2.2.0" "python-multipart==0.0.12" "structlog==24.4.0" \
    "celery[redis]==5.4.0" "anthropic==0.39.0" "pgvector==0.3.6"
  pip install -q -e packages/shared-schemas/python
fi

# ─── 4. migrate + seed ──────────────────────────────────────────────
cd services/api
export PYTHONPATH="$PWD:$PYTHONPATH"

echo "→ running alembic migrations…"
alembic upgrade head

echo "→ seeding demo data…"
python -m app.scripts.seed || echo "  (seed already applied — continuing)"

# ─── 5. start API ───────────────────────────────────────────────────
echo
echo "════════════════════════════════════════════════════════════════"
echo " ✓ AutoTune AI is running"
echo "   API docs   → http://localhost:8000/docs"
echo "   Health     → http://localhost:8000/v1/healthz"
echo
echo "   Demo login:"
echo "     owner@demo.autotune.ai / demo-owner-Pass!23"
echo "     tuner@demo.autotune.ai / demo-tuner-Pass!23"
echo
echo "   Ctrl-C to stop the API. Data services keep running."
echo "   Stop them later:  $DOCKER_CMD -f infra/docker/docker-compose.minimal.yml down"
echo "════════════════════════════════════════════════════════════════"
echo

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
