#!/bin/bash
# Quick backend restart script

cd "$(dirname "$0")/backend"

# Stop existing backend
pkill -f "uvicorn app.main:app" 2>/dev/null
sleep 1

# Activate venv and start
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &

echo "Backend restarting... (PID: $!)"
echo "Logs: tail -f logs/backend.log"
sleep 2

# Check if started
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✓ Backend started successfully"
else
    echo "⚠ Backend starting... wait a few seconds"
fi
