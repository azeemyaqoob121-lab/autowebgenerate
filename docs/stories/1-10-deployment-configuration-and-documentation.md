# Story 1.10: Deployment Configuration and Documentation

Status: todo

## Story

As a DevOps engineer,
I want deployment configuration and documentation,
So that the application can be deployed to production environment.

## Acceptance Criteria

1. Dockerfile created for FastAPI backend with multi-stage build
2. Docker Compose production configuration created
3. Environment variable documentation complete with all required settings
4. Database migration instructions documented
5. Deployment guide created covering: environment setup, database initialization, application startup
6. Health check endpoint verified for container orchestration
7. Application successfully runs in Docker container locally

## Tasks / Subtasks

- [ ] Create production Dockerfile for backend (AC: 1)
  - [ ] Create `backend/Dockerfile` with multi-stage build
  - [ ] Stage 1 (builder): Install dependencies and compile
  - [ ] Stage 2 (runtime): Copy only necessary files for smaller image
  - [ ] Use Python 3.11-slim base image for minimal size
  - [ ] Set non-root user for security
  - [ ] Expose port 8000 for FastAPI application
  - [ ] Configure CMD to run with uvicorn using production settings
  - [ ] Add health check instruction

- [ ] Optimize Docker image size and security
  - [ ] Use .dockerignore to exclude unnecessary files
  - [ ] Copy requirements.txt first for better layer caching
  - [ ] Combine RUN commands to reduce layers
  - [ ] Remove build dependencies in runtime stage
  - [ ] Set appropriate file permissions
  - [ ] Test image build: `docker build -t autoweb-backend:latest .`
  - [ ] Verify image size (target: <500MB)

- [ ] Create Docker Compose production config (AC: 2)
  - [ ] Create `docker-compose.prod.yml` file
  - [ ] Configure backend service using production Dockerfile
  - [ ] Configure PostgreSQL with persistent volume
  - [ ] Configure Redis with persistent volume
  - [ ] Add environment variables from .env file
  - [ ] Configure networking between services
  - [ ] Add restart policies (unless-stopped)
  - [ ] Configure health checks for all services

- [ ] Document all environment variables (AC: 3)
  - [ ] Update `backend/.env.example` with all variables
  - [ ] Group variables by category (database, auth, AI, redis)
  - [ ] Add comments explaining purpose of each variable
  - [ ] Document required vs optional variables
  - [ ] Specify valid values or format for each variable
  - [ ] Document production security requirements (secrets management)
  - [ ] Create `docs/environment-variables.md` with detailed reference

- [ ] Create database migration guide (AC: 4)
  - [ ] Document initial setup: `alembic upgrade head`
  - [ ] Document creating new migrations: `alembic revision --autogenerate`
  - [ ] Document checking migration status: `alembic current`
  - [ ] Document rollback procedure: `alembic downgrade -1`
  - [ ] Explain migration naming conventions
  - [ ] Document backup strategy before migrations
  - [ ] Add migration troubleshooting section

- [ ] Create comprehensive deployment guide (AC: 5)
  - [ ] Create `docs/deployment-guide.md`
  - [ ] **Prerequisites Section**: Server requirements (CPU, RAM, disk), software (Docker, Docker Compose)
  - [ ] **Environment Setup**: Clone repo, configure .env, generate JWT secret
  - [ ] **Database Initialization**: Start PostgreSQL, create database, run migrations
  - [ ] **Application Startup**: Build images, start containers, verify health
  - [ ] **Verification Steps**: Test health endpoint, check logs, test API
  - [ ] **Monitoring**: Log locations, metrics endpoints
  - [ ] **Backup Strategy**: Database backups, data persistence

- [ ] Document production best practices
  - [ ] Add section on secrets management (don't commit .env files)
  - [ ] Document HTTPS/SSL configuration (reverse proxy setup)
  - [ ] Explain database connection pooling configuration
  - [ ] Document log aggregation and monitoring
  - [ ] Explain scaling considerations (horizontal scaling, load balancing)
  - [ ] Document backup and disaster recovery procedures
  - [ ] Add security hardening checklist

- [ ] Create startup and initialization scripts
  - [ ] Create `backend/scripts/start.sh` for production startup
  - [ ] Script checks environment variables are set
  - [ ] Script waits for database to be ready (retry with timeout)
  - [ ] Script runs pending migrations automatically
  - [ ] Script starts uvicorn with production settings
  - [ ] Make script executable: `chmod +x scripts/start.sh`
  - [ ] Test script in Docker container

- [ ] Configure production uvicorn settings
  - [ ] Create production start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`
  - [ ] Configure worker count based on CPU cores (2 * cores + 1)
  - [ ] Disable auto-reload in production (--no-reload)
  - [ ] Configure access logging for monitoring
  - [ ] Set appropriate timeouts (keep-alive, timeout-keep-alive)
  - [ ] Test with production-like load

- [ ] Verify health check endpoint (AC: 6)
  - [ ] Ensure GET /api/health returns 200 OK when healthy
  - [ ] Health check validates database connectivity
  - [ ] Health check responds quickly (< 1 second)
  - [ ] Configure Docker HEALTHCHECK instruction in Dockerfile
  - [ ] Test health check in Docker container
  - [ ] Document health check endpoint for load balancers

- [ ] Create docker-compose quick start
  - [ ] Update root README.md with quick start section
  - [ ] Single command to start all services: `docker-compose up -d`
  - [ ] Document accessing API: http://localhost:8000
  - [ ] Document accessing docs: http://localhost:8000/docs
  - [ ] Document viewing logs: `docker-compose logs -f backend`
  - [ ] Document stopping services: `docker-compose down`

- [ ] Test production deployment locally (AC: 7)
  - [ ] Build production Docker images
  - [ ] Start services with docker-compose.prod.yml
  - [ ] Verify all containers start successfully
  - [ ] Run database migrations in container
  - [ ] Test health endpoint: `curl http://localhost:8000/api/health`
  - [ ] Test authentication endpoints
  - [ ] Test business CRUD endpoints
  - [ ] Check container logs for errors
  - [ ] Verify data persists after container restart

- [ ] Create production troubleshooting guide
  - [ ] Document common deployment issues
  - [ ] Database connection failures (check network, credentials)
  - [ ] Migration failures (check permissions, schema conflicts)
  - [ ] Container startup failures (check logs, env vars)
  - [ ] Performance issues (check resources, connection pool)
  - [ ] Add debugging commands (docker logs, docker exec, psql access)

- [ ] Document deployment to cloud platforms (optional enhancement)
  - [ ] Add section for AWS deployment (ECS, RDS, ElastiCache)
  - [ ] Add section for Google Cloud deployment (Cloud Run, Cloud SQL)
  - [ ] Add section for Azure deployment (Container Instances, Azure Database)
  - [ ] Add section for DigitalOcean deployment (App Platform, Managed Databases)
  - [ ] Include infrastructure-as-code examples (Terraform, CloudFormation)

## Dev Notes

### Learnings from Previous Stories

**From Story 1.1 (Status: review)**
- **Docker Compose**: Basic docker-compose.yml already exists for development
- **Environment Variables**: .env.example files created for backend and frontend
- **README**: Root README.md exists with basic setup instructions

**From Story 1.3 (Status: review)**
- **Health Check**: GET /api/health endpoint implemented with database connectivity check
- **Configuration**: Settings class loads from environment variables
- **CORS**: CORS_ORIGINS configured via environment variable

**From Story 1.2 (Status: review)**
- **Alembic Migrations**: Migration system configured and ready
- **Database**: PostgreSQL 14 required, schemas defined

[Source: stories/1-1-project-initialization-and-environment-setup.md#Dev-Agent-Record]

### Project Structure

```
backend/
├── Dockerfile            # NEW: Production Docker image
├── .dockerignore         # NEW: Exclude unnecessary files
├── scripts/
│   └── start.sh          # NEW: Production startup script
├── docker-compose.prod.yml  # NEW: Production compose config
└── ...

docs/
├── deployment-guide.md        # NEW: Comprehensive deployment guide
├── environment-variables.md   # NEW: Environment variable reference
└── troubleshooting.md         # NEW: Deployment troubleshooting

README.md                 # UPDATE: Add quick start section
```

### Technical Constraints

- **Python Version**: 3.11+ (match development environment)
- **Base Image**: python:3.11-slim (minimal, secure)
- **Non-Root User**: Run application as non-root for security
- **Port**: Expose 8000 for FastAPI application
- **Workers**: 4 Uvicorn workers for production (adjust based on CPU)
- **Image Size**: Target <500MB for efficient deployment

### Multi-Stage Dockerfile Pattern

**Benefits:**
- Smaller runtime image (excludes build tools)
- Better layer caching (dependencies change less frequently)
- Security (only runtime dependencies in final image)

**Structure:**
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Dockerfile

```dockerfile
# Multi-stage build for smaller final image
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Make PATH include local Python packages
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start application
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"]
```

### .dockerignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Testing
.pytest_cache/
htmlcov/
.coverage
*.cover

# Development
.env
.env.local
*.db
*.sqlite

# Documentation
docs/
*.md

# IDE
.vscode/
.idea/
*.swp
*.swo

# Git
.git/
.gitignore

# Alembic (keep only necessary files)
alembic/versions/*.pyc
```

### Production Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: autoweb-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/autoweb_db
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET=${JWT_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENVIRONMENT=production
      - DEBUG=false
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - autoweb-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:14-alpine
    container_name: autoweb-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=autoweb_db
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - autoweb-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: autoweb-redis
    restart: unless-stopped
    volumes:
      - redis-data:/data
    networks:
      - autoweb-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres-data:
    driver: local
  redis-data:
    driver: local

networks:
  autoweb-network:
    driver: bridge
```

### Environment Variables Reference

**Required Variables:**
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database
POSTGRES_PASSWORD=<strong-password>  # For docker-compose

# Redis
REDIS_URL=redis://host:port/db

# Authentication
JWT_SECRET=<32+ character random string>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours

# OpenAI API
OPENAI_API_KEY=<your-api-key>

# Application
ENVIRONMENT=production
DEBUG=false
APP_NAME=AutoWeb Outreach AI
API_VERSION=0.1.0

# CORS (comma-separated)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Optional Variables:**
```bash
# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Connection Pool
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
```

### Startup Script (start.sh)

```bash
#!/bin/bash
set -e

echo "AutoWeb Outreach AI - Starting..."

# Check required environment variables
required_vars=("DATABASE_URL" "REDIS_URL" "JWT_SECRET")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var environment variable is not set"
        exit 1
    fi
done

# Wait for database to be ready
echo "Waiting for database..."
max_attempts=30
attempt=0
until pg_isready -h postgres -p 5432 -U postgres || [ $attempt -eq $max_attempts ]; do
    attempt=$((attempt + 1))
    echo "Database not ready, attempt $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "Error: Database failed to become ready"
    exit 1
fi

echo "Database is ready!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start application
echo "Starting FastAPI application..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --no-access-log \
    --proxy-headers \
    --forwarded-allow-ips='*'
```

### Production Checklist

**Before Deployment:**
- [ ] Generate strong JWT_SECRET (32+ random characters)
- [ ] Configure strong database password
- [ ] Set DEBUG=false and ENVIRONMENT=production
- [ ] Configure CORS_ORIGINS with actual frontend domain
- [ ] Obtain OpenAI API key
- [ ] Review and set all environment variables
- [ ] Run security audit on dependencies
- [ ] Review Docker image for vulnerabilities

**After Deployment:**
- [ ] Test health check endpoint
- [ ] Verify database migrations applied
- [ ] Test authentication flow
- [ ] Test API endpoints
- [ ] Check application logs for errors
- [ ] Monitor resource usage (CPU, memory)
- [ ] Setup log aggregation
- [ ] Configure backups
- [ ] Setup monitoring/alerting

### References

- [Source: docs/epics.md#Story-1.10]
- [Source: docs/PRD.md#NFR005] (Deployment security)
- Docker Multi-Stage Builds: https://docs.docker.com/build/building/multi-stage/
- Docker Compose Production: https://docs.docker.com/compose/production/
- Uvicorn Deployment: https://www.uvicorn.org/deployment/

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

<!-- Will be filled during implementation -->

### Debug Log References

<!-- Will be filled during implementation -->

### Completion Notes List

<!-- Will be filled during implementation -->

### File List

<!-- Will be filled during implementation -->

## Change Log

- 2025-11-01: Story created from Epic 1, Story 10 in epics.md
