# Lesson 10: Scaling & Monitoring - From Local to Production Readiness

This comprehensive lesson guides you through preparing your agentic application for production deployment, using AWS as an example platform. You'll learn about containerization, modular architecture, deployment strategies, comprehensive logging, monitoring, and scaling strategies.

## Learning Objectives

By the end of this lesson, you will be able to:

1. Design and implement production-ready modular architectures for AI agents
2. Containerize applications using Docker with best practices
3. Deploy containerized applications on AWS using ECS, ECR, and ALB
4. Implement comprehensive logging and monitoring systems
5. Set up auto-scaling and load balancing for high availability
6. Configure CI/CD pipelines for automated deployments
7. Implement security best practices for production environments
8. Design disaster recovery and backup strategies

## Table of Contents

- [Why Production-Ready Architecture Matters](#why-production-ready-architecture-matters)
- [Modular Production Architecture](#modular-production-architecture)
- [Containerization with Docker](#containerization-with-docker)
- [AWS Deployment Strategy](#aws-deployment-strategy)
- [Infrastructure as Code](#infrastructure-as-code)
- [Comprehensive Logging System](#comprehensive-logging-system)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Auto-scaling and Load Balancing](#auto-scaling-and-load-balancing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Security and Compliance](#security-and-compliance)
- [Disaster Recovery](#disaster-recovery)
- [Cost Optimization](#cost-optimization)
- [Hands-on Project](#hands-on-project)
- [Best Practices](#best-practices)

## Why Production-Ready Architecture Matters

### The Challenge of Scaling AI Agents

**Development vs Production Challenges:**

| Development | Production |
|-------------|------------|
| Single user | Thousands of concurrent users |
| Local resources | Distributed infrastructure |
| Manual testing | Automated testing & deployment |
| Simple error handling | Comprehensive error recovery |
| Basic logging | Structured logging & monitoring |
| No security concerns | Enterprise-grade security |

**Production Requirements:**
- **High Availability**: 99.9% uptime or better
- **Scalability**: Handle traffic spikes automatically
- **Security**: Protect against attacks and data breaches
- **Observability**: Complete visibility into system behavior
- **Reliability**: Graceful failure handling and recovery
- **Performance**: Low latency and high throughput
- **Cost Efficiency**: Optimize resource usage

### Benefits of Containerization

**Why Docker for AI Applications?**

```
┌─────────────────────────────────────────────────────────────────┐
│                   CONTAINERIZATION BENEFITS                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   CONSISTENCY   │    │   PORTABILITY   │    │   ISOLATION     │ │
│  │                 │    │                 │    │                 │ │
│  │ • Same env      │    │ • Run anywhere  │    │ • Dependencies  │ │
│  │   everywhere    │    │ • Cloud/On-prem │    │   isolated      │ │
│  │ • Eliminates    │    │ • Easy migration│    │ • No conflicts  │ │
│  │   "works on my  │    │ • Vendor lock-in│    │ • Security      │ │
│  │   machine"      │    │   avoidance     │    │   boundaries    │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   EFFICIENCY    │    │   SCALABILITY   │    │   DEPLOYMENT    │ │
│  │                 │    │                 │    │                 │ │
│  │ • Resource      │    │ • Horizontal    │    │ • Fast startup  │ │
│  │   optimization │    │   scaling       │    │ • Blue-green    │ │
│  │ • Faster        │    │ • Load          │    │   deployments  │ │
│  │   startup       │    │   balancing     │    │ • Rollback      │ │
│  │ • Lower         │    │ • Auto-scaling  │    │   capability    │ │
│  │   overhead      │    │   policies      │    │ • Zero downtime │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Container vs Virtual Machine:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTAINERS VS VIRTUAL MACHINES              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│    CONTAINERS                     VIRTUAL MACHINES             │
│                                                                 │
│ ┌─────────────────┐             ┌─────────────────┐             │
│ │   Application   │             │   Application   │             │
│ ├─────────────────┤             ├─────────────────┤             │
│ │   Dependencies  │             │   Dependencies  │             │
│ ├─────────────────┤             ├─────────────────┤             │
│ │Container Runtime│             │  Guest OS       │             │
│ ├─────────────────┤             ├─────────────────┤             │
│ │   Host OS       │             │   Hypervisor    │             │
│ ├─────────────────┤             ├─────────────────┤             │
│ │   Hardware      │             │   Host OS       │             │
│ └─────────────────┘             ├─────────────────┤             │
│                                 │   Hardware      │             │
│ ✓ Lightweight                   └─────────────────┘             │
│ ✓ Fast startup                                                  │
│ ✓ Less overhead                 ✓ Complete isolation            │
│ ✓ Better resource               ✓ Different OS support          │
│   utilization                   ✗ Heavy resource usage         │
│                                 ✗ Slower startup               │
└─────────────────────────────────────────────────────────────────┘
```

## Modular Production Architecture

### Complete AWS Production Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                        AWS PRODUCTION ARCHITECTURE                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                                                                     │
│    ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐    │
│    │                                                      INTERNET GATEWAY                                                                                      │    │
│    └─────────────────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                │                                                                                     │
│    ┌──────────────────────────────────────────────────────────────────────────▼──────────────────────────────────────────────────────────────────────────────┐    │
│    │                                                         ROUTE 53 (DNS)                                                                                   │    │
│    └─────────────────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                │                                                                                     │
│    ┌──────────────────────────────────────────────────────────────────────────▼──────────────────────────────────────────────────────────────────────────────┐    │
│    │                                                    CLOUDFRONT (CDN)                                                                                       │    │
│    └─────────────────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                │                                                                                     │
│    ┌──────────────────────────────────────────────────────────────────────────▼──────────────────────────────────────────────────────────────────────────────┐    │
│    │                                                   WAF (Web Application Firewall)                                                                          │    │
│    └─────────────────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                │                                                                                     │
│    ┌──────────────────────────────────────────────────────────────────────────▼──────────────────────────────────────────────────────────────────────────────┐    │
│    │                                              APPLICATION LOAD BALANCER (ALB)                                                                             │    │
│    │                                                    ┌──────────────────────┐                                                                               │    │
│    │                                                    │   Target Groups      │                                                                               │    │
│    │                                                    │  - Health Checks     │                                                                               │    │
│    │                                                    │  - SSL Termination   │                                                                               │    │
│    │                                                    └──────────────────────┘                                                                               │    │
│    └─────────────────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                │                                                                                     │
│    ┌──────────────────────────────────────────────────────────────────────────▼──────────────────────────────────────────────────────────────────────────────┐    │
│    │                                                   VPC (Virtual Private Cloud)                                                                            │    │
│    │                                                                                                                                                           │    │
│    │  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │    │
│    │  │                                                  PUBLIC SUBNETS                                                                                     │  │    │
│    │  │                                                                                                                                                     │  │    │
│    │  │  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │  │    │
│    │  │  │                                              ECS CLUSTER                                                                                       │  │  │    │
│    │  │  │                                                                                                                                                 │  │  │    │
│    │  │  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                                    │  │  │    │
│    │  │  │  │   ECS SERVICE   │  │   ECS SERVICE   │  │   ECS SERVICE   │  │   ECS SERVICE   │  │   ECS SERVICE   │                                    │  │  │    │
│    │  │  │  │                 │  │                 │  │                 │  │                 │  │                 │                                    │  │  │    │
│    │  │  │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │                                    │  │  │    │
│    │  │  │  │ │FastAPI      │ │  │ │FastAPI      │ │  │ │FastAPI      │ │  │ │FastAPI      │ │  │ │FastAPI      │ │                                    │  │  │    │
│    │  │  │  │ │Container    │ │  │ │Container    │ │  │ │Container    │ │  │ │Container    │ │  │ │Container    │ │                                    │  │  │    │
│    │  │  │  │ │             │ │  │ │             │ │  │ │             │ │  │ │             │ │  │ │             │ │                                    │  │  │    │
│    │  │  │  │ │- Chat Agent │ │  │ │- RAG Agent  │ │  │ │- Search     │ │  │ │- Analysis   │ │  │ │- Batch      │ │                                    │  │  │    │
│    │  │  │  │ │- Auth       │ │  │ │- Vector DB  │ │  │ │  Agent      │ │  │ │  Agent      │ │  │ │  Processing │ │                                    │  │  │    │
│    │  │  │  │ │- Monitoring │ │  │ │- Embedding  │ │  │ │- Indexing   │ │  │ │- ML Models  │ │  │ │- Queue      │ │                                    │  │  │    │
│    │  │  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘                                    │  │  │    │
│    │  │  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘  │  │    │
│    │  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘  │    │
│    │                                                                                                                                                           │    │
│    │  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │    │
│    │  │                                                PRIVATE SUBNETS                                                                                      │  │    │
│    │  │                                                                                                                                                     │  │    │
│    │  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                                        │  │    │
│    │  │  │   RDS CLUSTER   │  │   ELASTICACHE   │  │   OPENSEARCH    │  │   DYNAMODB      │  │   S3 BUCKETS    │                                        │  │    │
│    │  │  │                 │  │                 │  │                 │  │                 │  │                 │                                        │  │    │
│    │  │  │ ┌─────────────┐ │  │ ┌─────────────┘ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │                                        │  │    │
│    │  │  │ │Primary DB   │ │  │ │Redis Cache  │ │  │ │Vector Store │ │  │ │Session Store│ │  │ │Model        │ │                                        │  │    │
│    │  │  │ │Read Replica │ │  │ │Session Store│ │  │ │Search Index │ │  │ │User Data    │ │  │ │Artifacts    │ │                                        │  │    │
│    │  │  │ │Backup       │ │  │ │Rate Limits │ │  │ │Analytics    │ │  │ │Logs         │ │  │ │Static Files │ │                                        │  │    │
│    │  │  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │                                        │  │    │
│    │  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘                                        │  │    │
│    │  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘  │    │
│    └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                │                                                                                     │
│    ┌──────────────────────────────────────────────────────────────────────────▼──────────────────────────────────────────────────────────────────────────────┐    │
│    │                                                   MONITORING & LOGGING                                                                                    │    │
│    │                                                                                                                                                           │    │
│    │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                                              │    │
│    │  │   CLOUDWATCH    │  │   X-RAY         │  │   CLOUDTRAIL    │  │   CONFIG        │  │   SYSTEMS       │                                              │    │
│    │  │                 │  │                 │  │                 │  │                 │  │   MANAGER       │                                              │    │
│    │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │                                              │    │
│    │  │ │Metrics      │ │  │ │Distributed  │ │  │ │API Calls    │ │  │ │Compliance   │ │  │ │Patch Mgmt   │ │                                              │    │
│    │  │ │Logs         │ │  │ │Tracing      │ │  │ │Audit Trail  │ │  │ │Config       │ │  │ │Secrets      │ │                                              │    │
│    │  │ │Alarms       │ │  │ │Performance  │ │  │ │Security     │ │  │ │Changes      │ │  │ │Parameters   │ │                                              │    │
│    │  │ │Dashboards   │ │  │ │Analysis     │ │  │ │Events       │ │  │ │Remediation  │ │  │ │Automation   │ │                                              │    │
│    │  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │                                              │    │
│    │  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘                                              │    │
│    └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Microservices Architecture Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                   MICROSERVICES ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                       API Gateway                              │
│                 ┌─────────────────┐                           │
│                 │   Route 53      │                           │
│                 │   CloudFront    │                           │
│                 │   ALB           │                           │
│                 └─────────────────┘                           │
│                           │                                    │
│              ┌────────────┼────────────┐                      │
│              │            │            │                      │
│              ▼            ▼            ▼                      │
│    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│    │   CHAT      │ │    RAG      │ │  ANALYTICS  │           │
│    │  SERVICE    │ │  SERVICE    │ │  SERVICE    │           │
│    │             │ │             │ │             │           │
│    │ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │           │
│    │ │FastAPI  │ │ │ │FastAPI  │ │ │ │FastAPI  │ │           │
│    │ │Container│ │ │ │Container│ │ │ │Container│ │           │
│    │ └─────────┘ │ │ └─────────┘ │ │ └─────────┘ │           │
│    │             │ │             │ │             │           │
│    │ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │           │
│    │ │Chat     │ │ │ │Vector   │ │ │ │ML       │ │           │
│    │ │Agent    │ │ │ │DB       │ │ │ │Models   │ │           │
│    │ └─────────┘ │ │ └─────────┘ │ │ └─────────┘ │           │
│    └─────────────┘ └─────────────┘ └─────────────┘           │
│              │            │            │                      │
│              └────────────┼────────────┘                      │
│                           │                                    │
│                           ▼                                    │
│                 ┌─────────────────┐                           │
│                 │  SHARED LAYER   │                           │
│                 │                 │                           │
│                 │ ┌─────────────┐ │                           │
│                 │ │Database     │ │                           │
│                 │ │Cache        │ │                           │
│                 │ │Message      │ │                           │
│                 │ │Queue        │ │                           │
│                 │ │Monitoring   │ │                           │
│                 │ └─────────────┘ │                           │
│                 └─────────────────┘                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Modular Design Principles

#### 1. Separation of Concerns
- **API Layer**: FastAPI endpoints and request/response handling
- **Business Logic**: AI agent processing and orchestration
- **Data Layer**: Database operations and caching
- **Infrastructure Layer**: Monitoring, logging, and configuration

#### 2. Stateless Design
- **No Session Storage**: Each request is independent
- **External State**: Store state in databases or caches
- **Horizontal Scaling**: Can add/remove instances freely

#### 3. Fault Tolerance
- **Circuit Breakers**: Prevent cascading failures
- **Retry Logic**: Automatic retry with exponential backoff
- **Graceful Degradation**: Maintain service with reduced functionality

#### 4. Observability
- **Distributed Tracing**: Track requests across services
- **Structured Logging**: Consistent log format across services
- **Metrics Collection**: Real-time system and business metrics

## Containerization with Docker

### Docker Fundamentals for AI Applications

#### Multi-Stage Docker Build

```dockerfile
# Dockerfile - Multi-stage build for production
# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser config/ ./config/
COPY --chown=appuser:appuser scripts/ ./scripts/

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### Docker Compose for Development

```yaml
# docker-compose.yml - Development environment
version: '3.8'

services:
  # Main API service
  api:
    build: 
      context: .
      dockerfile: Dockerfile
      target: builder  # Use builder stage for development
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/agentdb
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - redis
      - postgres
    volumes:
      - ./app:/app/app  # Mount for hot reloading
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - agent-network

  # Redis for caching and session storage
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - agent-network

  # PostgreSQL database
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=agentdb
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - agent-network

  # Monitoring with Prometheus
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    restart: unless-stopped
    networks:
      - agent-network

  # Grafana for visualization
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana:/etc/grafana/provisioning
    restart: unless-stopped
    networks:
      - agent-network

volumes:
  redis_data:
  postgres_data:
  prometheus_data:
  grafana_data:

networks:
  agent-network:
    driver: bridge
```

#### Production Docker Build Script

```bash
#!/bin/bash
# build.sh - Production build script

set -e

# Configuration
IMAGE_NAME="ai-agent-api"
REGISTRY="123456789012.dkr.ecr.us-east-1.amazonaws.com"
REGION="us-east-1"
VERSION=$(git rev-parse --short HEAD)
LATEST_TAG="latest"

echo "Building Docker image..."

# Build the image
docker build -t "${IMAGE_NAME}:${VERSION}" \
             -t "${IMAGE_NAME}:${LATEST_TAG}" \
             --target production \
             .

# Tag for registry
docker tag "${IMAGE_NAME}:${VERSION}" "${REGISTRY}/${IMAGE_NAME}:${VERSION}"
docker tag "${IMAGE_NAME}:${LATEST_TAG}" "${REGISTRY}/${IMAGE_NAME}:${LATEST_TAG}"

# Login to ECR
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${REGISTRY}

# Push to registry
echo "Pushing to ECR..."
docker push "${REGISTRY}/${IMAGE_NAME}:${VERSION}"
docker push "${REGISTRY}/${IMAGE_NAME}:${LATEST_TAG}"

echo "Build and push completed successfully!"
echo "Image: ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
```

### Container Optimization Strategies

#### Resource Optimization

```python
# app/config/container.py
import psutil
import os
from typing import Dict, Any

class ContainerOptimizer:
    """Container resource optimization"""
    
    def __init__(self):
        self.cpu_count = psutil.cpu_count()
        self.memory_gb = psutil.virtual_memory().total / (1024**3)
        self.container_limits = self.get_container_limits()
    
    def get_container_limits(self) -> Dict[str, Any]:
        """Get container resource limits"""
        limits = {}
        
        # CPU limits
        if os.path.exists('/sys/fs/cgroup/cpu/cpu.cfs_quota_us'):
            with open('/sys/fs/cgroup/cpu/cpu.cfs_quota_us', 'r') as f:
                quota = int(f.read().strip())
            with open('/sys/fs/cgroup/cpu/cpu.cfs_period_us', 'r') as f:
                period = int(f.read().strip())
            
            if quota > 0:
                limits['cpu_cores'] = quota / period
        
        # Memory limits
        if os.path.exists('/sys/fs/cgroup/memory/memory.limit_in_bytes'):
            with open('/sys/fs/cgroup/memory/memory.limit_in_bytes', 'r') as f:
                memory_limit = int(f.read().strip())
            
            if memory_limit < (1 << 62):  # Not unlimited
                limits['memory_gb'] = memory_limit / (1024**3)
        
        return limits
    
    def get_optimal_workers(self) -> int:
        """Calculate optimal number of workers"""
        cpu_cores = self.container_limits.get('cpu_cores', self.cpu_count)
        
        # Formula: (2 x CPU cores) + 1
        workers = int((2 * cpu_cores) + 1)
        
        # Ensure minimum and maximum
        workers = max(1, min(workers, 8))
        
        return workers
    
    def get_memory_per_worker(self) -> float:
        """Calculate memory per worker"""
        total_memory = self.container_limits.get('memory_gb', self.memory_gb)
        workers = self.get_optimal_workers()
        
        # Reserve 20% for system overhead
        available_memory = total_memory * 0.8
        memory_per_worker = available_memory / workers
        
        return memory_per_worker

# Usage in main application
optimizer = ContainerOptimizer()
WORKERS = optimizer.get_optimal_workers()
```

#### Startup Script

```bash
#!/bin/bash
# scripts/start.sh - Container startup script

set -e

# Wait for dependencies
echo "Waiting for dependencies..."
while ! nc -z redis 6379; do
    echo "Waiting for Redis..."
    sleep 2
done

while ! nc -z postgres 5432; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting FastAPI application..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers ${WORKERS:-4} \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-log \
    --access-log-format '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
```

## Logging & Monitoring

### Structured Logging Example
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        return json.dumps(log_record)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()
for handler in logger.handlers:
    handler.setFormatter(JSONFormatter())

logger.info("API started")
```

### Monitoring with CloudWatch (Pseudo-code)
```python
import boto3
cloudwatch = boto3.client('cloudwatch')

def publish_metric(name, value, unit="Count"):
    cloudwatch.put_metric_data(
        Namespace='AgentAPI',
        MetricData=[{
            'MetricName': name,
            'Value': value,
            'Unit': unit
        }]
    )

# Example usage
publish_metric('APIRequestCount', 1)
publish_metric('APIErrorCount', 0)
```

### Health Check Endpoint (FastAPI)
```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
```

---

## AWS Deployment Strategy

### AWS Services Architecture

#### Core Services
- **ECS (Elastic Container Service)**: Container orchestration
- **ECR (Elastic Container Registry)**: Docker image storage
- **ALB (Application Load Balancer)**: Traffic distribution
- **VPC (Virtual Private Cloud)**: Network isolation
- **Route 53**: DNS management
- **CloudFront**: CDN for global distribution

#### Data Services
- **RDS**: Relational database (PostgreSQL/MySQL)
- **DynamoDB**: NoSQL database for high-performance queries
- **ElastiCache**: Redis for caching and session storage
- **S3**: Object storage for files and artifacts
- **OpenSearch**: Full-text search and analytics

#### Monitoring & Security
- **CloudWatch**: Logging, metrics, and alerting
- **X-Ray**: Distributed tracing
- **CloudTrail**: API audit logging
- **IAM**: Identity and access management
- **WAF**: Web application firewall

### ECS Task Definition

```json
{
  "family": "ai-agent-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "ai-agent-api",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/ai-agent-api:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "AWS_REGION",
          "value": "us-east-1"
        },
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:openai-api-key"
        },
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:database-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-agent-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8000/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### ECS Service Configuration

```json
{
  "serviceName": "ai-agent-api-service",
  "cluster": "ai-agent-cluster",
  "taskDefinition": "ai-agent-api:1",
  "desiredCount": 3,
  "launchType": "FARGATE",
  "networkConfiguration": {
    "awsvpcConfiguration": {
      "subnets": [
        "subnet-12345678",
        "subnet-87654321"
      ],
      "securityGroups": [
        "sg-12345678"
      ],
      "assignPublicIp": "DISABLED"
    }
  },
  "loadBalancers": [
    {
      "targetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/ai-agent-api-tg/1234567890123456",
      "containerName": "ai-agent-api",
      "containerPort": 8000
    }
  ],
  "deploymentConfiguration": {
    "maximumPercent": 200,
    "minimumHealthyPercent": 100,
    "deploymentCircuitBreaker": {
      "enable": true,
      "rollback": true
    }
  },
  "serviceTags": [
    {
      "key": "Environment",
      "value": "production"
    },
    {
      "key": "Service",
      "value": "ai-agent-api"
    }
  ]
}
```

### Auto Scaling Configuration

```python
# infrastructure/auto_scaling.py
import boto3
from typing import Dict, Any

class AutoScalingManager:
    """ECS Auto Scaling configuration"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.autoscaling = boto3.client('application-autoscaling', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
    
    def register_scalable_target(self, service_name: str, cluster_name: str):
        """Register ECS service as scalable target"""
        return self.autoscaling.register_scalable_target(
            ServiceNamespace='ecs',
            ResourceId=f'service/{cluster_name}/{service_name}',
            ScalableDimension='ecs:service:DesiredCount',
            MinCapacity=2,
            MaxCapacity=20,
            RoleARN='arn:aws:iam::123456789012:role/application-autoscaling-ecs-service'
        )
    
    def create_scaling_policy(self, service_name: str, cluster_name: str, policy_type: str = 'TargetTrackingScaling'):
        """Create auto scaling policy"""
        if policy_type == 'TargetTrackingScaling':
            return self.autoscaling.put_scaling_policy(
                PolicyName=f'{service_name}-cpu-scaling',
                ServiceNamespace='ecs',
                ResourceId=f'service/{cluster_name}/{service_name}',
                ScalableDimension='ecs:service:DesiredCount',
                PolicyType='TargetTrackingScaling',
                TargetTrackingScalingPolicyConfiguration={
                    'TargetValue': 70.0,
                    'PredefinedMetricSpecification': {
                        'PredefinedMetricType': 'ECSServiceAverageCPUUtilization'
                    },
                    'ScaleOutCooldown': 300,
                    'ScaleInCooldown': 300
                }
            )
        
        elif policy_type == 'StepScaling':
            return self.autoscaling.put_scaling_policy(
                PolicyName=f'{service_name}-requests-scaling',
                ServiceNamespace='ecs',
                ResourceId=f'service/{cluster_name}/{service_name}',
                ScalableDimension='ecs:service:DesiredCount',
                PolicyType='StepScaling',
                StepScalingPolicyConfiguration={
                    'AdjustmentType': 'ChangeInCapacity',
                    'Cooldown': 300,
                    'StepAdjustments': [
                        {
                            'MetricIntervalLowerBound': 0.0,
                            'MetricIntervalUpperBound': 50.0,
                            'ScalingAdjustment': 1
                        },
                        {
                            'MetricIntervalLowerBound': 50.0,
                            'ScalingAdjustment': 2
                        }
                    ]
                }
            )
    
    def create_cloudwatch_alarm(self, service_name: str, cluster_name: str, policy_arn: str):
        """Create CloudWatch alarm for scaling"""
        return self.cloudwatch.put_metric_alarm(
            AlarmName=f'{service_name}-high-requests',
            ComparisonOperator='GreaterThanThreshold',
            EvaluationPeriods=2,
            MetricName='RequestCountPerTarget',
            Namespace='AWS/ApplicationELB',
            Period=300,
            Statistic='Sum',
            Threshold=1000.0,
            ActionsEnabled=True,
            AlarmActions=[policy_arn],
            AlarmDescription=f'High request count for {service_name}',
            Dimensions=[
                {
                    'Name': 'TargetGroup',
                    'Value': f'targetgroup/{service_name}-tg/1234567890123456'
                }
            ]
        )

# Usage example
autoscaling_manager = AutoScalingManager()
autoscaling_manager.register_scalable_target('ai-agent-api-service', 'ai-agent-cluster')
policy_response = autoscaling_manager.create_scaling_policy('ai-agent-api-service', 'ai-agent-cluster')
autoscaling_manager.create_cloudwatch_alarm('ai-agent-api-service', 'ai-agent-cluster', policy_response['PolicyARN'])
```

### Load Balancer Configuration

```python
# infrastructure/load_balancer.py
import boto3
from typing import List, Dict, Any

class LoadBalancerManager:
    """Application Load Balancer configuration"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.elbv2 = boto3.client('elbv2', region_name=region)
    
    def create_load_balancer(self, 
                           name: str,
                           subnets: List[str],
                           security_groups: List[str]) -> Dict[str, Any]:
        """Create Application Load Balancer"""
        response = self.elbv2.create_load_balancer(
            Name=name,
            Subnets=subnets,
            SecurityGroups=security_groups,
            Scheme='internet-facing',
            Type='application',
            IpAddressType='ipv4',
            Tags=[
                {'Key': 'Environment', 'Value': 'production'},
                {'Key': 'Service', 'Value': 'ai-agent-api'}
            ]
        )
        return response['LoadBalancers'][0]
    
    def create_target_group(self,
                          name: str,
                          vpc_id: str,
                          port: int = 8000) -> Dict[str, Any]:
        """Create target group for ECS service"""
        response = self.elbv2.create_target_group(
            Name=name,
            Protocol='HTTP',
            Port=port,
            VpcId=vpc_id,
            TargetType='ip',
            HealthCheckEnabled=True,
            HealthCheckIntervalSeconds=30,
            HealthCheckPath='/health',
            HealthCheckProtocol='HTTP',
            HealthCheckTimeoutSeconds=5,
            HealthyThresholdCount=2,
            UnhealthyThresholdCount=3,
            Matcher={'HttpCode': '200'}
        )
        return response['TargetGroups'][0]
    
    def create_listener(self,
                       load_balancer_arn: str,
                       target_group_arn: str,
                       certificate_arn: str = None) -> Dict[str, Any]:
        """Create listener for load balancer"""
        if certificate_arn:
            # HTTPS listener
            response = self.elbv2.create_listener(
                LoadBalancerArn=load_balancer_arn,
                Protocol='HTTPS',
                Port=443,
                Certificates=[{'CertificateArn': certificate_arn}],
                DefaultActions=[
                    {
                        'Type': 'forward',
                        'TargetGroupArn': target_group_arn
                    }
                ]
            )
        else:
            # HTTP listener
            response = self.elbv2.create_listener(
                LoadBalancerArn=load_balancer_arn,
                Protocol='HTTP',
                Port=80,
                DefaultActions=[
                    {
                        'Type': 'forward',
                        'TargetGroupArn': target_group_arn
                    }
                ]
            )
        return response['Listeners'][0]
    
    def create_listener_rules(self,
                            listener_arn: str,
                            rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create advanced routing rules"""
        created_rules = []
        
        for priority, rule in enumerate(rules, start=1):
            response = self.elbv2.create_rule(
                ListenerArn=listener_arn,
                Priority=priority,
                Conditions=rule['conditions'],
                Actions=rule['actions']
            )
            created_rules.append(response['Rules'][0])
        
        return created_rules

# Usage example
lb_manager = LoadBalancerManager()

# Create load balancer
lb = lb_manager.create_load_balancer(
    name='ai-agent-api-lb',
    subnets=['subnet-12345678', 'subnet-87654321'],
    security_groups=['sg-12345678']
)

# Create target group
tg = lb_manager.create_target_group(
    name='ai-agent-api-tg',
    vpc_id='vpc-12345678'
)

# Create listener
listener = lb_manager.create_listener(
    load_balancer_arn=lb['LoadBalancerArn'],
    target_group_arn=tg['TargetGroupArn'],
    certificate_arn='arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012'
)

# Create advanced routing rules
rules = [
    {
        'conditions': [
            {
                'Field': 'path-pattern',
                'Values': ['/api/v1/chat*']
            }
        ],
        'actions': [
            {
                'Type': 'forward',
                'TargetGroupArn': tg['TargetGroupArn']
            }
        ]
    }
]

lb_manager.create_listener_rules(listener['ListenerArn'], rules)
```

## Infrastructure as Code

### AWS CDK Implementation

```typescript
// infrastructure/lib/ai-agent-stack.ts
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as elasticache from 'aws-cdk-lib/aws-elasticache';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import { Construct } from 'constructs';

export class AIAgentStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // VPC Configuration
    const vpc = new ec2.Vpc(this, 'AIAgentVPC', {
      maxAzs: 2,
      natGateways: 1,
      subnetConfiguration: [
        {
          cidrMask: 24,
          name: 'Public',
          subnetType: ec2.SubnetType.PUBLIC,
        },
        {
          cidrMask: 24,
          name: 'Private',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
        },
        {
          cidrMask: 24,
          name: 'Database',
          subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
        },
      ],
    });

    // Security Groups
    const albSecurityGroup = new ec2.SecurityGroup(this, 'ALBSecurityGroup', {
      vpc,
      description: 'Security group for Application Load Balancer',
      allowAllOutbound: true,
    });
    albSecurityGroup.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(80));
    albSecurityGroup.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(443));

    const ecsSecurityGroup = new ec2.SecurityGroup(this, 'ECSSecurityGroup', {
      vpc,
      description: 'Security group for ECS tasks',
      allowAllOutbound: true,
    });
    ecsSecurityGroup.addIngressRule(albSecurityGroup, ec2.Port.tcp(8000));

    const databaseSecurityGroup = new ec2.SecurityGroup(this, 'DatabaseSecurityGroup', {
      vpc,
      description: 'Security group for RDS database',
      allowAllOutbound: false,
    });
    databaseSecurityGroup.addIngressRule(ecsSecurityGroup, ec2.Port.tcp(5432));

    // Secrets Manager
    const dbSecret = new secretsmanager.Secret(this, 'DatabaseSecret', {
      generateSecretString: {
        secretStringTemplate: JSON.stringify({ username: 'postgres' }),
        generateStringKey: 'password',
        excludeCharacters: '"@/\\',
      },
    });

    const apiSecret = new secretsmanager.Secret(this, 'APISecret', {
      secretStringValue: cdk.SecretValue.unsafePlainText(JSON.stringify({
        openai_api_key: 'your-openai-api-key',
        jwt_secret: 'your-jwt-secret',
      })),
    });

    // RDS Database
    const database = new rds.DatabaseInstance(this, 'AIAgentDatabase', {
      engine: rds.DatabaseInstanceEngine.postgres({
        version: rds.PostgresEngineVersion.VER_15_4,
      }),
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MEDIUM),
      vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
      },
      securityGroups: [databaseSecurityGroup],
      credentials: rds.Credentials.fromSecret(dbSecret),
      databaseName: 'agentdb',
      allocatedStorage: 100,
      storageType: rds.StorageType.GP2,
      backupRetention: cdk.Duration.days(7),
      deletionProtection: true,
      multiAz: true,
    });

    // ElastiCache Redis
    const redisSubnetGroup = new elasticache.CfnSubnetGroup(this, 'RedisSubnetGroup', {
      description: 'Subnet group for Redis',
      subnetIds: vpc.privateSubnets.map(subnet => subnet.subnetId),
    });

    const redis = new elasticache.CfnCacheCluster(this, 'RedisCluster', {
      cacheNodeType: 'cache.t3.micro',
      engine: 'redis',
      numCacheNodes: 1,
      cacheSubnetGroupName: redisSubnetGroup.ref,
      vpcSecurityGroupIds: [ecsSecurityGroup.securityGroupId],
    });

    // ECS Cluster
    const cluster = new ecs.Cluster(this, 'AIAgentCluster', {
      vpc,
      containerInsights: true,
    });

    // Task Definition
    const taskDefinition = new ecs.FargateTaskDefinition(this, 'AIAgentTaskDefinition', {
      memoryLimitMiB: 2048,
      cpu: 1024,
    });

    // Task Role
    const taskRole = new iam.Role(this, 'AIAgentTaskRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('CloudWatchAgentServerPolicy'),
      ],
    });

    dbSecret.grantRead(taskRole);
    apiSecret.grantRead(taskRole);

    // Log Group
    const logGroup = new logs.LogGroup(this, 'AIAgentLogGroup', {
      logGroupName: '/ecs/ai-agent-api',
      retention: logs.RetentionDays.ONE_WEEK,
    });

    // Container Definition
    const container = taskDefinition.addContainer('ai-agent-api', {
      image: ecs.ContainerImage.fromRegistry('123456789012.dkr.ecr.us-east-1.amazonaws.com/ai-agent-api:latest'),
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'ecs',
        logGroup,
      }),
      environment: {
        AWS_REGION: this.region,
        ENVIRONMENT: 'production',
        REDIS_URL: `redis://${redis.attrRedisEndpointAddress}:${redis.attrRedisEndpointPort}`,
      },
      secrets: {
        DATABASE_URL: ecs.Secret.fromSecretsManager(dbSecret, 'password'),
        OPENAI_API_KEY: ecs.Secret.fromSecretsManager(apiSecret, 'openai_api_key'),
        JWT_SECRET: ecs.Secret.fromSecretsManager(apiSecret, 'jwt_secret'),
      },
      healthCheck: {
        command: ['CMD-SHELL', 'curl -f http://localhost:8000/health || exit 1'],
        interval: cdk.Duration.seconds(30),
        timeout: cdk.Duration.seconds(5),
        retries: 3,
        startPeriod: cdk.Duration.seconds(60),
      },
    });

    container.addPortMappings({
      containerPort: 8000,
      protocol: ecs.Protocol.TCP,
    });

    // ECS Service
    const service = new ecs.FargateService(this, 'AIAgentService', {
      cluster,
      taskDefinition,
      desiredCount: 3,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
      securityGroups: [ecsSecurityGroup],
      enableLogging: true,
      circuitBreaker: {
        rollback: true,
      },
    });

    // Application Load Balancer
    const alb = new elbv2.ApplicationLoadBalancer(this, 'AIAgentALB', {
      vpc,
      internetFacing: true,
      securityGroup: albSecurityGroup,
    });

    // Target Group
    const targetGroup = new elbv2.ApplicationTargetGroup(this, 'AIAgentTargetGroup', {
      vpc,
      port: 8000,
      protocol: elbv2.ApplicationProtocol.HTTP,
      targetType: elbv2.TargetType.IP,
      healthCheck: {
        path: '/health',
        interval: cdk.Duration.seconds(30),
        timeout: cdk.Duration.seconds(5),
        healthyThresholdCount: 2,
        unhealthyThresholdCount: 3,
      },
    });

    // Add service to target group
    service.attachToApplicationTargetGroup(targetGroup);

    // Listener
    const listener = alb.addListener('AIAgentListener', {
      port: 80,
      defaultTargetGroups: [targetGroup],
    });

    // Auto Scaling
    const scaling = service.autoScaleTaskCount({
      minCapacity: 2,
      maxCapacity: 20,
    });

    scaling.scaleOnCpuUtilization('CPUScaling', {
      targetUtilizationPercent: 70,
      scaleInCooldown: cdk.Duration.minutes(5),
      scaleOutCooldown: cdk.Duration.minutes(5),
    });

    scaling.scaleOnMemoryUtilization('MemoryScaling', {
      targetUtilizationPercent: 80,
      scaleInCooldown: cdk.Duration.minutes(5),
      scaleOutCooldown: cdk.Duration.minutes(5),
    });

    // Outputs
    new cdk.CfnOutput(this, 'LoadBalancerDNS', {
      value: alb.loadBalancerDnsName,
      description: 'DNS name of the load balancer',
    });

    new cdk.CfnOutput(this, 'DatabaseEndpoint', {
      value: database.instanceEndpoint.hostname,
      description: 'RDS database endpoint',
    });
  }
}
```

### Terraform Alternative

```hcl
# infrastructure/main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "ai-agent-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "ai-agent-igw"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count = 2

  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "ai-agent-public-${count.index + 1}"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count = 2

  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"