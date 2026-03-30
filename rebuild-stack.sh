#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="compose.yml"
ENV_FILE=".env"

echo "--- stopping existing stack"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down

echo "--- rebuilding images and starting"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --build

echo "--- tailing backend logs (ctrl+c to exit)"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs -f --no-log-prefix backend