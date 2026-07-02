SHELL := /bin/bash
# Auto-pick docker compose (v2 plugin) or docker-compose (v1 binary). Prefix sudo if needed.
DOCKER_CMD := $(shell if docker compose version >/dev/null 2>&1; then echo "docker compose"; else echo "docker-compose"; fi)
SUDO := $(shell docker ps >/dev/null 2>&1 || echo sudo)
COMPOSE := $(SUDO) $(DOCKER_CMD) -f infra/docker/docker-compose.yml --env-file .env

.DEFAULT_GOAL := help

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

bootstrap: ## One-time local setup
	@command -v pnpm >/dev/null || npm i -g pnpm@9
	@command -v poetry >/dev/null || pip install poetry
	cp -n .env.example .env || true
	cd services/api && poetry install
	cd services/analysis-worker && poetry install
	cd apps/web && pnpm install
	cd apps/mobile && pnpm install
	$(COMPOSE) build

up: ## Start the full stack
	$(COMPOSE) up -d
	@echo "API   → http://localhost:8000/docs"
	@echo "Web   → http://localhost:3000"
	@echo "MinIO → http://localhost:9001"
	@echo "Neo4j → http://localhost:7474"

down: ## Stop the stack
	$(COMPOSE) down

logs: ## Tail compose logs
	$(COMPOSE) logs -f --tail=200

ps: ## List running services
	$(COMPOSE) ps

migrate: ## Apply Alembic migrations
	$(COMPOSE) exec api alembic upgrade head

revision: ## Generate a new Alembic revision: make revision name="add foo"
	$(COMPOSE) exec api alembic revision --autogenerate -m "$(name)"

seed: ## Seed demo vehicles + KG
	$(COMPOSE) exec api python -m app.scripts.seed

test: ## Run all tests
	cd services/api && poetry run pytest -q
	cd apps/web && pnpm test --run

lint: ## Lint everything
	cd services/api && poetry run ruff check .
	cd apps/web && pnpm lint

typecheck: ## Static analysis
	cd services/api && poetry run mypy app
	cd apps/web && pnpm typecheck

format: ## Auto-format
	cd services/api && poetry run ruff format .
	cd apps/web && pnpm format

ai-eval: ## Run AI orchestrator golden-set eval
	$(COMPOSE) exec api python -m app.ai.eval.run

shell-api: ## Shell into API container
	$(COMPOSE) exec api bash

psql: ## Open psql to the OLTP db
	$(COMPOSE) exec postgres psql -U autotune -d autotune

clean: ## Remove containers + volumes (DESTRUCTIVE)
	$(COMPOSE) down -v --remove-orphans

.PHONY: help bootstrap up down logs ps migrate revision seed test lint typecheck format ai-eval shell-api psql clean
