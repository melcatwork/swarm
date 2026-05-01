# Zeabur Deployment Guide

## Overview

This application is configured for single-service deployment on Zeabur. The FastAPI backend serves both the API (`/api/*`) and the React frontend (`/`) from a single service.

## Architecture

```
Zeabur Service (trax.zeabur.app)
├── / → React frontend (SPA)
├── /assets/* → Frontend static files (CSS, JS, images)
└── /api/* → FastAPI backend API
```

## Deployment Configuration

### Files Involved

1. **`zbpack.json`** - Zeabur build configuration (PRIMARY)
   - Defines build, install, and start commands
   - Ensures Node.js is available for frontend build
   - Builds frontend → copies to `backend/static/` → installs Python deps → starts server

2. **`.buildpacks`** - Buildpack specification (FALLBACK)
   - Specifies Node.js buildpack first, then Python buildpack
   - Ensures both runtimes are available during build

3. **`package.json` (root)** - Node.js detection
   - Signals to Zeabur that Node.js 20.x is required
   - Provides npm build script as alternative build method

4. **`backend/runtime.txt`** - Python version specification
   - Explicitly requests Python 3.11

5. **`Procfile`** - Start command
   - Starts uvicorn backend server only (build handled by zbpack.json)

6. **`backend/app/main.py`** - FastAPI application
   - Mounts `/assets` for static files
   - Serves `index.html` for all non-API routes (SPA routing)
   - Enhanced logging to verify static directory status

7. **`frontend/src/api/client.js`** - API client
   - Uses relative URLs in production (`import.meta.env.DEV`)
   - Uses `http://localhost:8000` in development

8. **`build.sh`** - Local/Docker build script (NOT used by Zeabur)
   - For local development and Docker Compose only

## Environment Variables (Zeabur)

Set these in your Zeabur service settings:

```bash
# LLM Provider Configuration
LLM_PROVIDER=bedrock  # or 'anthropic' or 'ollama'

# AWS Bedrock (if using bedrock provider)
AWS_BEARER_TOKEN_BEDROCK=your-bedrock-token
AWS_REGION_NAME=us-east-1
BEDROCK_MODEL=bedrock/anthropic.claude-sonnet-4-20250514-v1:0

# Anthropic API (if using anthropic provider)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# CORS (should be empty for single-service deployment)
CORS_ORIGINS=

# Database (SQLite, no configuration needed)
DATABASE_URL=sqlite:///data/swarm_tm.db
```

## Deployment Steps

### 1. Connect Repository to Zeabur

1. Go to [Zeabur Dashboard](https://zeabur.com)
2. Create new project
3. Add new service → Deploy from GitHub
4. Select `melcatwork/swarm` repository
5. Select `main` branch

### 2. Configure Service

1. **Service Name**: `swarm-tm` (or any name)
2. **Build Command**: Automatically detected from `Procfile`
3. **Port**: Zeabur auto-detects from `$PORT` variable
4. **Environment Variables**: Add all required variables from above

### 3. Deploy

1. Click "Deploy"
2. Zeabur will:
   - Clone the repository
   - Detect multi-language project from `zbpack.json` and `.buildpacks`
   - Run Node.js buildpack: `npm ci --prefix frontend && npm run build --prefix frontend`
   - Copy frontend build: `cp -r frontend/dist/* backend/static/`
   - Run Python buildpack: `pip install -r backend/requirements.txt`
   - Start backend with `uvicorn app.main:app` (serves frontend at `/` and API at `/api/*`)

### 4. Access Application

- Frontend: `https://your-service.zeabur.app/`
- API Health: `https://your-service.zeabur.app/api/health`
- API Docs: `https://your-service.zeabur.app/docs`

## Troubleshooting

### 404 Errors on All Routes (FIXED in latest commit)

**Symptom**: All requests return 404, including `/api/health`

**Root Cause**: Node.js buildpack wasn't configured, so `npm` wasn't available during build. Frontend build failed, `backend/static/` was never created, and the catch-all route was never registered.

**Fix Applied**:
- Added `zbpack.json` with explicit build commands
- Added `.buildpacks` to specify Node.js + Python buildpack order
- Added root `package.json` for Node.js detection
- Added `backend/runtime.txt` for Python 3.11
- Enhanced logging to verify static directory status

**Verification**:
1. Check Zeabur build logs for:
   - "Installing Node.js" or "Node.js buildpack"
   - "npm ci --prefix frontend" success
   - "npm run build --prefix frontend" success
   - "cp -r frontend/dist/*" success

2. Check application startup logs for:
   ```
   Checking frontend static directory at: /app/backend/static
   Static directory exists: True
   Static directory contents (X items): ['index.html', 'assets', ...]
   Mounting frontend static files from: /app/backend/static
   ```

3. If still 404, trigger manual redeploy in Zeabur dashboard

### Frontend Loads But API Calls Fail

**Symptom**: Frontend loads but shows "Cannot connect to backend"

**Causes**:
1. API routes not registered before catch-all route
2. CORS misconfiguration

**Solution**:
- Check backend logs for errors
- Verify API routes are accessible: `/api/health`, `/api/llm/models`
- Ensure `CORS_ORIGINS` is empty or contains your domain

### LLM Configuration Issues

**Symptom**: "LLM provider not configured" errors

**Solution**:
- Verify environment variables are set in Zeabur
- Check provider-specific credentials:
  - Bedrock: `AWS_BEARER_TOKEN_BEDROCK`
  - Anthropic: `ANTHROPIC_API_KEY`
- Check backend startup logs for validation errors

## Local Development

### Frontend (Vite Dev Server)

```bash
cd frontend
npm install
npm run dev  # http://localhost:5173
```

Frontend will proxy API calls to `http://localhost:8000`

### Backend (FastAPI)

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Backend serves API at `http://localhost:8000/api/*`

### Full Stack (Docker Compose)

```bash
docker-compose up
```

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`

## Build Verification

To verify the build works:

```bash
# Build frontend
./build.sh

# Check static files were copied
ls -la backend/static/
# Should show: index.html, assets/, etc.

# Start backend (serves both frontend and API)
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Test
curl http://localhost:8000/           # Should return index.html
curl http://localhost:8000/api/health # Should return {"status":"ok"}
```

## Monitoring

### Health Check

```bash
curl https://your-service.zeabur.app/api/health
```

Expected response:
```json
{"status": "ok", "version": "0.1.0"}
```

### LLM Status

```bash
curl https://your-service.zeabur.app/api/llm/status
```

Returns LLM provider configuration and availability.

## Rollback

If deployment fails, rollback via Zeabur dashboard:

1. Go to service → Deployments
2. Find last working deployment
3. Click "Redeploy"

## Support

- GitHub Issues: https://github.com/melcatwork/swarm/issues
- Zeabur Docs: https://zeabur.com/docs
