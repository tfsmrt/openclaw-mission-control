#!/bin/bash
# Auto-deploy script for openclaw-mission-control
set -e

REPO_DIR="/root/.openclaw/workspace/mission-control"
LOG="/tmp/mc-deploy.log"

echo "[$(date)] Deploy triggered" >> "$LOG"

cd "$REPO_DIR"

# Pull latest
git pull origin master >> "$LOG" 2>&1

# Rebuild + restart (frontend needs rebuild if Next.js changed, backend always)
docker compose -f compose.yml --env-file .env up -d --build >> "$LOG" 2>&1

echo "[$(date)] Deploy complete" >> "$LOG"
