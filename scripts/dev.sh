#!/usr/bin/env bash
# Dev helper: bring the stack up, migrate, seed, and tail api logs.
set -euo pipefail
cd "$(dirname "$0")/.."

make up
sleep 3
make migrate
make seed
echo
echo "Stack is up:"
echo "  API   → http://localhost:8000/docs"
echo "  Web   → http://localhost:3000"
echo "  MinIO → http://localhost:9001 (minio / minio12345)"
echo "  Neo4j → http://localhost:7474 (neo4j / autotune-graph)"
echo
docker compose -f infra/docker/docker-compose.yml logs -f api worker
