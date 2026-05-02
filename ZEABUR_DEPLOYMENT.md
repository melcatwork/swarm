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

1. **`Dockerfile`** - Multi-stage Docker build (PRIMARY)
   - Stage 1: Builds React frontend with Node.js 20
   - Stage 2: Python 3.11 backend + copies built frontend to `static/`
   - Final image serves both frontend and API from one container
   - Zeabur auto-detects and uses this Dockerfile

2. **`.dockerignore`** - Docker build optimization
   - Excludes node_modules, venv, .git, etc. from build context
   - Speeds up builds and reduces image size

3. **`.buildpacks`** - Buildpack fallback (kept for compatibility)
   - Specifies Node.js + Python buildpack order
   - Used if Dockerfile detection fails

4. **`package.json` (root)** - Node.js version specification
   - Declares Node.js 20.x and npm 10.x requirements
   - Used by Dockerfile and buildpacks

5. **`backend/runtime.txt`** - Python version specification
   - Explicitly requests Python 3.11

6. **`Procfile`** - Start command override (optional)
   - Overrides Dockerfile CMD if needed
   - Currently matches Dockerfile CMD

7. **`backend/app/main.py`** - FastAPI application
   - Mounts `/assets` for static files
   - Serves `index.html` for all non-API routes (SPA routing)
   - Enhanced logging to verify static directory status

8. **`frontend/src/api/client.js`** - API client
   - Uses relative URLs in production (`import.meta.env.DEV`)
   - Uses `http://localhost:8000` in development

9. **`build.sh`** - Local build script (NOT used by Zeabur)
   - For local development and docker-compose only

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
   - Detect `Dockerfile` in root directory
   - Build Stage 1 (frontend-builder):
     * Use node:20-slim image
     * `npm ci` to install dependencies
     * `npm run build` to build React app
   - Build Stage 2 (final image):
     * Use python:3.11-slim image
     * `pip install -r requirements.txt`
     * Copy backend code
     * Copy built frontend from Stage 1 to `/app/static`
   - Run container: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Result: Single container serving frontend at `/` and API at `/api/*`

### 4. Access Application

- Frontend: `https://your-service.zeabur.app/`
- API Health: `https://your-service.zeabur.app/api/health`
- API Docs: `https://your-service.zeabur.app/docs`

## Troubleshooting

### 404 Errors on All Routes (FIXED)

**Symptom**: All requests return 404, including `/api/health`

**Root Cause**: Initially tried buildpack approach, but Zeabur's working directory management made relative paths break. Switched to multi-stage Dockerfile for reliability.

**Fix Applied** (Latest):
- Multi-stage Dockerfile: Stage 1 builds frontend, Stage 2 serves backend
- All paths absolute within Docker context (no cd issues)
- `.dockerignore` optimizes build (excludes node_modules, venv, etc.)
- Enhanced logging to verify static directory status

**Verification**:
1. Check Zeabur build logs for:
   - "Building Dockerfile" or "Dockerfile detected"
   - Stage 1: `[frontend-builder X/Y]` steps completing
   - Stage 2: `[stage-1 X/Y]` steps completing
   - No errors in npm build or pip install

2. Check application startup logs for:
   ```
   Checking frontend static directory at: /app/static
   Static directory exists: True
   Static directory contents (X items): ['index.html', 'assets', ...]
   Mounting frontend static files from: /app/static
   ```

3. Test endpoints:
   - `curl https://trax.zeabur.app/api/health` → `{"status":"ok"}`
   - `curl -I https://trax.zeabur.app/` → HTTP 200

4. If still failing, check Zeabur logs for Docker build errors

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
