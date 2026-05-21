#!/bin/bash
set -e

# Start RQ worker in background
python -m app.worker &
WORKER_PID=$!

# Start dummy HTTP server to satisfy Render port requirement
python -m http.server 8000 --directory /tmp &
HTTP_PID=$!

# If either process dies, exit container so Render restarts it
wait -n
exit 1
