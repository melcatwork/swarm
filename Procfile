# Zeabur Procfile for Swarm TM
# Deploys FastAPI backend serving both frontend and API
# Build phase is handled by multi-stage Dockerfile

web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
