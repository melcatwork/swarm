# Swarm TM Deployment Guide

This guide covers deployment options for Swarm TM in various environments.

## Table of Contents

- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Production Considerations](#production-considerations)
- [Monitoring](#monitoring)

## Local Development

### Backend Development

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp ../.env.example ../.env
# Edit .env with your configuration

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Hot Reloading**: The `--reload` flag enables automatic restart on code changes.

### Frontend Development

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

**Hot Module Replacement**: Vite provides instant updates without full page reload.

### Running Both Services

**Terminal 1 (Backend):**
```bash
cd backend && source venv/bin/activate && uvicorn app.main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend && npm run dev
```

## Docker Deployment

### Quick Start with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Configuration

Create `.env` file in project root:

```bash
# LLM Configuration
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen3:14b

# Or use Anthropic
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# CORS for production
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

**Note**: When using Ollama on the host machine, use `http://host.docker.internal:11434` instead of `http://localhost:11434`.

### Access Points

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Docker Networking

Services communicate via the `swarm-network` bridge network:
- Frontend → Backend: `http://backend:8000`
- Nginx proxies `/api/*` to backend

### Persistent Data

Backend data is stored in a named volume:

```bash
# View volume
docker volume inspect swarm-tm_backend-data

# Backup volume
docker run --rm -v swarm-tm_backend-data:/data -v $(pwd):/backup ubuntu tar czf /backup/backup.tar.gz /data

# Restore volume
docker run --rm -v swarm-tm_backend-data:/data -v $(pwd):/backup ubuntu tar xzf /backup/backup.tar.gz -C /
```

## Cloud Deployment

### Railway

Railway is ideal for backend deployment with automatic HTTPS and domain management.

#### Prerequisites
- Railway account
- Railway CLI installed

#### Deployment Steps

1. **Install CLI**
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Initialize Project**
   ```bash
   cd swarm-tm
   railway init
   ```

3. **Configure Environment Variables**

   In Railway dashboard, add:
   ```
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   CORS_ORIGINS=https://your-frontend-domain.com
   ```

4. **Deploy**
   ```bash
   railway up
   ```

5. **Get URL**
   ```bash
   railway domain
   ```

#### Railway Configuration

The `Procfile` configures the service:
```
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Railway automatically sets `$PORT` and provides SSL termination.

### AWS Deployment

#### Option 1: ECS with Fargate

1. **Build and push images to ECR**
   ```bash
   # Authenticate
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

   # Build and tag
   docker build -t swarm-tm-backend backend/
   docker tag swarm-tm-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/swarm-tm-backend:latest

   # Push
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/swarm-tm-backend:latest
   ```

2. **Create ECS task definition** with:
   - Environment variables from Secrets Manager
   - ALB for load balancing
   - Fargate for serverless containers

3. **Create ECS service**
   - Auto-scaling based on CPU/memory
   - Health checks on `/api/health`

#### Option 2: EC2 with Docker Compose

1. **Launch EC2 instance** (t3.medium or larger)
2. **Install Docker and Docker Compose**
   ```bash
   sudo yum update -y
   sudo yum install docker -y
   sudo systemctl start docker
   sudo usermod -a -G docker ec2-user

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Deploy application**
   ```bash
   git clone <repository>
   cd swarm-tm
   cp .env.example .env
   # Edit .env
   docker-compose up -d
   ```

4. **Configure security groups**
   - Allow inbound 80 (frontend)
   - Allow inbound 8000 (backend API)
   - Allow inbound 22 (SSH)

### GCP Deployment (Cloud Run)

#### Backend on Cloud Run

1. **Build and push to GCR**
   ```bash
   gcloud builds submit --tag gcr.io/<project-id>/swarm-tm-backend backend/
   ```

2. **Deploy**
   ```bash
   gcloud run deploy swarm-tm-backend \
     --image gcr.io/<project-id>/swarm-tm-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars LLM_PROVIDER=anthropic \
     --set-secrets ANTHROPIC_API_KEY=swarm-tm-api-key:latest
   ```

#### Frontend on Cloud Storage + Cloud CDN

1. **Build frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Upload to Cloud Storage**
   ```bash
   gsutil -m cp -r dist/* gs://<bucket-name>/
   gsutil web set -m index.html -e index.html gs://<bucket-name>
   ```

3. **Configure Cloud CDN** for caching and HTTPS

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests (if needed).

## Production Considerations

### Security

1. **Environment Variables**
   - Never commit `.env` files
   - Use secrets management (AWS Secrets Manager, GCP Secret Manager)
   - Rotate API keys regularly

2. **CORS Configuration**
   ```bash
   CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
   ```

3. **HTTPS/TLS**
   - Use reverse proxy (nginx, Cloudflare)
   - Enable HSTS headers
   - Use certificate auto-renewal (Let's Encrypt)

4. **API Rate Limiting**
   - Implement rate limiting on sensitive endpoints
   - Use API gateway for throttling

5. **Input Validation**
   - File size limits enforced (1MB)
   - File type validation
   - Content validation

### Performance

1. **Caching**
   - Redis for session caching
   - CDN for static assets
   - Browser caching headers (nginx.conf)

2. **Database**
   - Use PostgreSQL for production (instead of SQLite)
   - Connection pooling
   - Regular backups

3. **LLM Provider**
   - Monitor API quotas
   - Implement retry logic with exponential backoff
   - Use queue system for long-running jobs

### Scaling

1. **Horizontal Scaling**
   ```yaml
   # docker-compose.yml
   backend:
     deploy:
       replicas: 3
   ```

2. **Load Balancing**
   - Nginx upstream for multiple backends
   - AWS ALB/NLB for cloud deployments

3. **Auto-scaling**
   - ECS/Kubernetes auto-scaling based on CPU/memory
   - Queue-based scaling for threat modeling jobs

### High Availability

1. **Multiple Availability Zones**
   - Deploy across 3+ AZs
   - RDS Multi-AZ for database

2. **Health Checks**
   - Backend: `/api/health`
   - Frontend: nginx status
   - LLM provider connectivity

3. **Backups**
   - Automated database backups
   - Configuration backups
   - Disaster recovery plan

## Monitoring

### Logging

1. **Application Logs**
   ```bash
   # Docker
   docker-compose logs -f backend

   # Production - send to centralized logging
   # AWS CloudWatch, GCP Cloud Logging, ELK Stack
   ```

2. **Access Logs**
   - Nginx access logs
   - API request logs
   - Error tracking (Sentry)

3. **Log Levels**
   - INFO: Normal operations
   - WARNING: Retries, degraded performance
   - ERROR: Failures, exceptions

### Metrics

1. **System Metrics**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network traffic

2. **Application Metrics**
   - Request rate
   - Response time
   - Error rate
   - Queue depth

3. **Business Metrics**
   - Threat models generated
   - Average paths per model
   - LLM API usage
   - User engagement

### Health Checks

```bash
# Backend health
curl http://localhost:8000/api/health

# LLM status
curl http://localhost:8000/api/llm-status

# Frontend
curl http://localhost:3000/
```

### Alerting

Set up alerts for:
- API error rate > 5%
- Response time > 5s
- LLM provider failures
- Disk usage > 80%
- Memory usage > 85%

Tools: CloudWatch Alarms, PagerDuty, Grafana

## Troubleshooting

### Container Issues

**Problem**: Container won't start

```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Rebuild
docker-compose up -d --build
```

**Problem**: Out of memory

```yaml
# docker-compose.yml
backend:
  deploy:
    resources:
      limits:
        memory: 2G
```

### Network Issues

**Problem**: Frontend can't reach backend

```bash
# Check network
docker network inspect swarm-tm_swarm-network

# Test backend from frontend container
docker-compose exec frontend wget -O- http://backend:8000/api/health
```

### Database Issues

**Problem**: Database locked (SQLite)

- Use PostgreSQL for production
- Or enable WAL mode for SQLite

### LLM Issues

**Problem**: Ollama not reachable from Docker

```bash
# Use host.docker.internal
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

**Problem**: API rate limit exceeded

- Implement request queuing
- Add retry logic with backoff
- Monitor usage

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Railway Documentation](https://docs.railway.app/)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
