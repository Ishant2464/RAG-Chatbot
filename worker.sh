#!/bin/bash
set -e

# Start RQ worker in background
python -m app.worker &
WORKER_PID=$!

# Start health check endpoint to satisfy Render port requirement
# Verifies Redis connection is alive
uvicorn app.worker_health:app --host 0.0.0.0 --port 8000 &
HEALTH_PID=$!

# If either process dies, exit container so Render restarts it
wait -n
exit 1
