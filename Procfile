# Zeabur Procfile for Swarm TM
# Deploys FastAPI backend serving both frontend and API
# Build phase is handled by zbpack.json configuration

web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
