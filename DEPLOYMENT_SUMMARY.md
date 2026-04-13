# Deployment Configuration Summary

This document summarizes all deployment files added to the Swarm TM project.

## Files Created

### 1. Docker Configuration

#### `backend/Dockerfile`
- **Base Image**: `python:3.11-slim`
- **Purpose**: Containerize the FastAPI backend service
- **Features**:
  - Multi-stage build optimization
  - System dependencies (build-essential)
  - Python dependencies from requirements.txt
  - Data directory for database and STIX cache
  - Health check endpoint
  - Port 8000 exposed

**Build Command**:
```bash
docker build -t swarm-tm-backend backend/
```

**Run Command**:
```bash
docker run -p 8000:8000 --env-file .env swarm-tm-backend
```

#### `frontend/Dockerfile`
- **Build Stage**: `node:20-slim`
- **Runtime Stage**: `nginx:alpine`
- **Purpose**: Multi-stage build for React SPA with Nginx serving
- **Features**:
  - Production build with Vite
  - Nginx for static file serving and API proxy
  - Gzip compression
  - Security headers
  - Health check endpoint
  - Port 80 exposed

**Build Command**:
```bash
docker build -t swarm-tm-frontend frontend/
```

**Run Command**:
```bash
docker run -p 3000:80 swarm-tm-frontend
```

#### `frontend/nginx.conf`
- **Purpose**: Nginx configuration for React SPA
- **Features**:
  - Serves React static files from `/usr/share/nginx/html`
  - Proxies `/api/*` to backend service at `http://backend:8000`
  - React Router support (all routes serve index.html)
  - Gzip compression for text assets
  - Static asset caching (1 year)
  - Security headers (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection)
  - Extended timeouts for long-running swarm operations (15 minutes)

**Key Configuration**:
```nginx
location /api/ {
    proxy_pass http://backend:8000;
    proxy_read_timeout 900s;  # 15 minutes for swarm operations
}
```

#### `backend/.dockerignore`
- Excludes: Python cache, virtual environments, tests, documentation
- Reduces image size and build time

#### `frontend/.dockerignore`
- Excludes: node_modules, build output, tests, documentation
- Reduces image size and build time

### 2. Docker Compose Configuration

#### `docker-compose.yml`
- **Purpose**: Orchestrate multi-service deployment
- **Services**:
  - **backend**: FastAPI application on port 8000
  - **frontend**: Nginx + React on port 3000
- **Features**:
  - Service dependency management (frontend depends on backend health)
  - Named volume for persistent backend data
  - Custom bridge network for service communication
  - Environment variables from `.env` file
  - Health checks for both services
  - Automatic restart policy

**Network Architecture**:
```
User → Frontend (port 3000)
  └─→ /api/* → Backend (port 8000)
        └─→ LLM Provider
```

**Usage**:
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### 3. Railway Configuration

#### `Procfile`
- **Purpose**: Configure Railway deployment
- **Command**: `web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Features**:
  - Automatic port detection from `$PORT` environment variable
  - Railway-specific process configuration
  - Backend-only deployment (frontend can be deployed separately)

**Deployment Steps**:
1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Set environment variables in Railway dashboard
5. Deploy: `railway up`

### 4. Documentation

#### `README.md` (Updated)
- **Sections Added**:
  - Features overview
  - Architecture (3-layer swarm system)
  - Technology stack
  - Quick start guide (local development)
  - Docker deployment instructions
  - Railway deployment guide
  - Configuration reference
  - LLM provider setup
  - Usage workflow
  - API endpoints reference
  - Project structure
  - Troubleshooting guide
  - Contributing guidelines

**Key Highlights**:
- Comprehensive quick start for developers
- Step-by-step Docker Compose setup
- Environment variable documentation
- Common troubleshooting scenarios

#### `DEPLOYMENT.md` (New)
- **Purpose**: Comprehensive deployment guide for all environments
- **Sections**:
  - Local development setup
  - Docker deployment (detailed)
  - Cloud deployment (Railway, AWS, GCP)
  - Production considerations (security, performance, scaling)
  - Monitoring and logging
  - High availability setup
  - Troubleshooting

**Deployment Options Covered**:
- Local development
- Docker Compose
- Railway (PaaS)
- AWS ECS/EC2
- GCP Cloud Run
- Kubernetes (reference)

### 5. Environment Configuration

#### `.env.example` (Updated)
- **Added**:
  ```bash
  # CORS Configuration (Production)
  CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
  ```

**Complete Environment Variables**:
```bash
# LLM Provider (choose one)
LLM_PROVIDER=ollama|bedrock|anthropic

# AWS Bedrock
AWS_BEARER_TOKEN_BEDROCK=your-token
AWS_REGION_NAME=us-east-1
BEDROCK_MODEL=bedrock/anthropic.claude-sonnet-4-20250514-v1:0

# Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:14b

# CORS (Production)
CORS_ORIGINS=https://yourdomain.com

# Database
DATABASE_URL=sqlite:///data/swarm_tm.db
```

## Deployment Workflows

### Local Development

```bash
# Terminal 1: Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

**Access**: Frontend at http://localhost:5173

### Docker Development

```bash
# One-line start
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop
docker-compose down
```

**Access**: Frontend at http://localhost:3000

### Production Deployment (Railway)

```bash
# Install and login
npm i -g @railway/cli
railway login

# Deploy
railway init
railway up

# Set environment in Railway dashboard
# Get URL
railway domain
```

### Production Deployment (AWS ECS)

```bash
# Build and push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.region.amazonaws.com
docker build -t swarm-tm-backend backend/
docker tag swarm-tm-backend:latest <account>.dkr.ecr.region.amazonaws.com/swarm-tm-backend:latest
docker push <account>.dkr.ecr.region.amazonaws.com/swarm-tm-backend:latest

# Create ECS task definition and service (via AWS Console or CLI)
```

## Docker Image Optimization

### Backend Image
- **Base**: Python 3.11 slim (smaller than full Python image)
- **Size**: ~500MB (with dependencies)
- **Optimizations**:
  - Multi-stage build not needed (Python doesn't compile)
  - `.dockerignore` excludes tests and docs
  - `--no-cache-dir` for pip to reduce layer size

### Frontend Image
- **Build Stage**: Node 20 slim
- **Runtime Stage**: Nginx alpine
- **Size**: ~25MB (final image)
- **Optimizations**:
  - Multi-stage build (node → nginx)
  - Production dependencies only (`npm ci --only=production`)
  - Alpine Linux for minimal size
  - Static files only in final image

**Size Comparison**:
- Backend: ~500MB
- Frontend: ~25MB
- Total: ~525MB

## Network Architecture

### Docker Compose Network

```
┌─────────────────────────────────────┐
│         swarm-network (bridge)       │
│                                      │
│  ┌──────────┐      ┌──────────┐    │
│  │ Frontend │─────▶│ Backend  │    │
│  │  :80     │      │  :8000   │    │
│  └────┬─────┘      └────┬─────┘    │
│       │                 │           │
└───────┼─────────────────┼───────────┘
        │                 │
        ▼                 ▼
    Host :3000       Host :8000
```

- Frontend container exposes port 80, mapped to host 3000
- Backend container exposes port 8000, mapped to host 8000
- Services communicate via internal network names
- Frontend proxies `/api/*` to `http://backend:8000`

### Production Network (AWS Example)

```
                Internet
                    │
                    ▼
             ┌──────────────┐
             │ Application  │
             │ Load Balancer│
             └──────┬───────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────┐       ┌───────────────┐
│   Frontend    │       │   Backend     │
│   ECS Task    │──────▶│   ECS Task    │
│   (Public)    │       │   (Private)   │
└───────────────┘       └──────┬────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │ RDS Database │
                        │  (Private)   │
                        └──────────────┘
```

## Security Considerations

### Docker Security

1. **Non-root User**: Consider adding non-root user in Dockerfiles
2. **Secrets Management**: Use Docker secrets or environment variables, never bake into images
3. **Network Isolation**: Use custom networks, avoid host networking
4. **Image Scanning**: Scan images for vulnerabilities (Trivy, Snyk)
5. **Minimal Base Images**: Use slim/alpine variants

### Production Security

1. **HTTPS**: Always use HTTPS in production (Let's Encrypt, CloudFlare)
2. **CORS**: Configure specific origins, not `*`
3. **API Keys**: Use secrets manager (AWS Secrets Manager, GCP Secret Manager)
4. **Rate Limiting**: Implement at API gateway or application level
5. **Firewall**: Restrict inbound traffic to necessary ports only

## Monitoring and Maintenance

### Health Checks

```bash
# Backend health
curl http://localhost:8000/api/health

# LLM status
curl http://localhost:8000/api/llm-status

# Docker health
docker-compose ps
```

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Updates

```bash
# Pull latest code
git pull

# Rebuild images
docker-compose build

# Restart with new images
docker-compose up -d
```

### Backups

```bash
# Backup database volume
docker run --rm -v swarm-tm_backend-data:/data -v $(pwd):/backup ubuntu tar czf /backup/backup.tar.gz /data

# Restore
docker run --rm -v swarm-tm_backend-data:/data -v $(pwd):/backup ubuntu tar xzf /backup/backup.tar.gz -C /
```

## Performance Optimization

### Backend
- Use PostgreSQL instead of SQLite for production
- Implement Redis for caching
- Use Gunicorn with multiple workers
- Enable connection pooling

### Frontend
- Enable Nginx caching
- Use CDN for static assets
- Implement service worker for offline support
- Optimize bundle size with code splitting

### Docker
- Use build cache effectively
- Multi-stage builds for smaller images
- Layer ordering (dependencies before code)
- Use `.dockerignore` files

## Troubleshooting

### Common Issues

**Backend won't start**:
```bash
# Check logs
docker-compose logs backend

# Check environment
docker-compose exec backend env | grep LLM
```

**Frontend can't reach backend**:
```bash
# Check network
docker network inspect swarm-tm_swarm-network

# Test from frontend container
docker-compose exec frontend wget -O- http://backend:8000/api/health
```

**Port conflicts**:
```bash
# Find what's using the port
lsof -i :8000

# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use different host port
```

## Next Steps

1. **Set up CI/CD**: GitHub Actions, GitLab CI
2. **Implement monitoring**: Prometheus, Grafana
3. **Add APM**: New Relic, DataDog
4. **Set up logging**: ELK Stack, CloudWatch
5. **Configure backups**: Automated database backups
6. **Load testing**: JMeter, k6

## Additional Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Railway Documentation](https://docs.railway.app/)
