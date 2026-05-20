#!/bin/bash
set -e
python -m app.worker &
exec uvicorn app.api.main:app --host 0.0.0.0 --port $PORT
