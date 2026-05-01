# Zeabur Procfile for Swarm TM
# Builds frontend and deploys FastAPI backend serving both frontend and API

web: ./build.sh && cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
