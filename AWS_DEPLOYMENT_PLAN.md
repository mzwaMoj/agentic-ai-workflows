# Text2SQL AI Analyst - AWS Production Deployment Plan

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Current State Assessment](#current-state-assessment)
3. [AWS Architecture Design](#aws-architecture-design)
4. [Security and Authentication](#security-and-authentication)
5. [Production Readiness Checklist](#production-readiness-checklist)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [MLOps Strategy](#mlops-strategy)
8. [Monitoring and Observability](#monitoring-and-observability)
9. [Cost Optimization](#cost-optimization)
10. [Step-by-Step Implementation Guide](#step-by-step-implementation-guide)
11. [Risk Management](#risk-management)
12. [Migration Strategy](#migration-strategy)

---

## Executive Summary

This document outlines a comprehensive strategy for deploying the Text2SQL AI Analyst application from a Proof of Concept (POC) to a production-ready system on AWS. The application consists of a Python FastAPI backend with SQL Server integration and a React frontend, providing natural language to SQL conversion capabilities with chart visualization.

### Key Objectives
- **Scalability**: Handle 100+concurrent users
- **Security**: Enterprise-grade authentication and data protection
- **Reliability**: 99.9% uptime with disaster recovery
- **Performance**: Sub-3 second response times
- **Compliance**: SOC 2, ISO 27001 ready architecture
- **Cost Efficiency**: Optimized AWS resource utilization

---

## Current State Assessment

### Technology Stack Analysis
- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Frontend**: React 18.2.0, Plotly.js for charts
- **Database**: SQL Server with Windows/SQL authentication
- **AI/ML**: Azure OpenAI integration, LlamaIndex, ChromaDB vector store
- **Configuration**: Environment-based with .env files
- **Containerization**: Docker ready with existing Dockerfile

### Identified Gaps for Production
1. **Authentication**: No enterprise SSO integration
2. **Database**: SQL Server needs cloud migration strategy
3. **Secrets Management**: Environment variables not secure
4. **Monitoring**: Basic health checks only
5. **Session Management**: No distributed session handling
6. **Prompt Management**: Hardcoded prompts need versioning
7. **Rate Limiting**: No API throttling implemented
8. **Error Handling**: Limited production error management
9. **Logging**: Basic logging needs centralization
10. **Backup/Recovery**: No backup strategy defined

---

## AWS Architecture Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          AWS Production Architecture              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    │
│  │   Route 53  │────│   CloudFront │────│   AWS WAF       │    │
│  │   (DNS)     │    │   (CDN)      │    │   (Security)    │    │
│  └─────────────┘    └──────────────┘    └─────────────────┘    │
│                              │                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                  Application Load Balancer                  ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                     Amazon ECS Fargate                     ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ ││
│  │  │   React     │  │   FastAPI   │  │   Background        │ ││
│  │  │   Frontend  │  │   Backend   │  │   Workers           │ ││
│  │  │             │  │             │  │   (Async Tasks)     │ ││
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                      Data Layer                            ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ ││
│  │  │   RDS SQL   │  │   Redis     │  │   OpenSearch        │ ││
│  │  │   Server    │  │   Cache     │  │   (Vector Store)    │ ││
│  │  │             │  │             │  │                     │ ││
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Supporting Services                      ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ ││
│  │  │   Cognito   │  │   Secrets   │  │   CloudWatch        │ ││
│  │  │   (Auth)    │  │   Manager   │  │   (Monitoring)      │ ││
│  │  │             │  │             │  │                     │ ││
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Core AWS Services

#### 1. Compute Layer
- **Amazon ECS with Fargate**: Serverless container orchestration
  - Backend containers: 2-10 instances (auto-scaling)
  - Frontend containers: 2-5 instances
  - Task definitions with health checks
  - Service mesh with AWS App Mesh for advanced traffic management

#### 2. Networking & Security
- **Application Load Balancer (ALB)**: Traffic distribution and SSL termination
- **AWS WAF**: Web application firewall for OWASP protection
- **CloudFront**: Global CDN for static assets and API caching
- **VPC**: Isolated network with public/private subnets across AZs
- **Route 53**: DNS management with health checks

#### 3. Data Storage
- **Amazon RDS SQL Server**: Managed SQL Server with Multi-AZ deployment
  - Instance type: db.r6i.2xlarge (8 vCPU, 64GB RAM)
  - Storage: 1TB GP3 SSD with encryption at rest
  - Automated backups with 30-day retention
- **Amazon ElastiCache (Redis)**: Session storage and API caching
- **Amazon OpenSearch**: Vector embeddings and semantic search
- **Amazon S3**: Static assets, logs, and backup storage

#### 4. Authentication & Authorization
- **Amazon Cognito**: User pool with SAML/OIDC integration
- **AWS Secrets Manager**: Secure API keys and database credentials
- **AWS IAM**: Fine-grained service permissions

---

## Security and Authentication

### Enterprise Authentication Strategy

#### 1. Microsoft Authentication Integration
```python
# Cognito SAML Configuration
COGNITO_USER_POOL_CONFIG = {
    "UserPoolName": "text2sql-users",
    "Policies": {
        "PasswordPolicy": {
            "MinimumLength": 12,
            "RequireUppercase": True,
            "RequireLowercase": True,
            "RequireNumbers": True,
            "RequireSymbols": True
        }
    },
    "MfaConfiguration": "ON",
    "SmsConfiguration": {
        "SnsCallerArn": "arn:aws:iam::account:role/service-role/Cognito-SMS-Role"
    },
    "UserPoolTags": {
        "Environment": "production",
        "Application": "text2sql"
    }
}
```

#### 2. Two-Factor Authentication (2FA)
- **SMS-based MFA**: Primary method using Amazon SNS
- **TOTP-based MFA**: Secondary method with authenticator apps
- **Backup codes**: Emergency access codes stored securely

#### 3. API Security
```python
# JWT Token Validation Middleware
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import jwt
import boto3

security = HTTPBearer()
cognito_client = boto3.client('cognito-idp')

async def verify_token(token: str = Depends(security)):
    try:
        # Validate JWT token with Cognito
        response = cognito_client.get_user(AccessToken=token.credentials)
        return response['Username']
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
```

#### 4. Data Encryption
- **At Rest**: AES-256 encryption for all storage
- **In Transit**: TLS 1.3 for all communications
- **Application Level**: Field-level encryption for sensitive data

### Session State Management

#### Distributed Session Storage
```python
# Redis Session Management
import redis
import json
from datetime import timedelta

class SessionManager:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.session_timeout = timedelta(hours=8)
    
    async def create_session(self, user_id: str, session_data: dict):
        session_id = f"session:{user_id}:{uuid.uuid4()}"
        session_data['created_at'] = datetime.utcnow().isoformat()
        session_data['user_id'] = user_id
        
        await self.redis_client.setex(
            session_id,
            self.session_timeout,
            json.dumps(session_data)
        )
        return session_id
    
    async def get_session(self, session_id: str):
        session_data = await self.redis_client.get(session_id)
        return json.loads(session_data) if session_data else None
```

---

## Production Readiness Checklist

### 1. Application Code Requirements

#### Backend Enhancements Needed
- [ ] **Environment Configuration Management**
  ```python
  # Replace current .env approach with AWS Parameter Store
  from aws_lambda_powertools import Logger
  import boto3
  
  class ParameterStore:
      def __init__(self):
          self.ssm = boto3.client('ssm')
          self.logger = Logger()
      
      def get_parameter(self, name: str, decrypt: bool = True):
          try:
              response = self.ssm.get_parameter(
                  Name=f"/text2sql/prod/{name}",
                  WithDecryption=decrypt
              )
              return response['Parameter']['Value']
          except Exception as e:
              self.logger.error(f"Failed to get parameter {name}: {e}")
              raise
  ```

- [ ] **Connection Pooling Implementation**
  ```python
  # Database connection pooling
  from sqlalchemy import create_engine
  from sqlalchemy.pool import QueuePool
  
  engine = create_engine(
      database_url,
      poolclass=QueuePool,
      pool_size=20,
      max_overflow=30,
      pool_pre_ping=True,
      pool_recycle=3600,
      echo=False
  )
  ```

- [ ] **Rate Limiting Implementation**
  ```python
  from slowapi import Limiter, _rate_limit_exceeded_handler
  from slowapi.util import get_remote_address
  
  limiter = Limiter(key_func=get_remote_address)
  app.state.limiter = limiter
  app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
  
  @app.post("/api/v1/text2sql/generate")
  @limiter.limit("10/minute")
  async def generate_sql(request: Request, query: QueryRequest):
      # Implementation
      pass
  ```

- [ ] **Comprehensive Error Handling**
  ```python
  from aws_lambda_powertools import Logger, Tracer
  
  logger = Logger()
  tracer = Tracer()
  
  class ProductionErrorHandler:
      @staticmethod
      async def handle_database_error(error: Exception):
          logger.error("Database error", extra={"error": str(error)})
          # Alert to monitoring system
          await send_alert("database_error", str(error))
          return {"error": "Database temporarily unavailable"}
  ```

#### Frontend Enhancements Needed
- [ ] **Service Worker for Offline Support**
- [ ] **Progressive Web App (PWA) Configuration**
- [ ] **Performance Monitoring Integration**
- [ ] **Error Boundary Components**
- [ ] **Accessibility (WCAG 2.1 AA) Compliance**

### 2. Infrastructure Requirements

#### Container Optimization
```dockerfile
# Production-optimized Dockerfile
FROM node:18-alpine AS frontend-build
WORKDIR /app
COPY src_frontend/package*.json ./
RUN npm ci --only=production
COPY src_frontend/ ./
RUN npm run build

FROM python:3.11-slim-bullseye AS backend
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ unixodbc unixodbc-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Install ODBC Driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY --from=frontend-build /app/build ./static/

# Create non-root user
RUN useradd -m -u 1001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### ECS Task Definition
```json
{
  "family": "text2sql-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/text2sql-task-role",
  "containerDefinitions": [
    {
      "name": "text2sql-app",
      "image": "your-account.dkr.ecr.region.amazonaws.com/text2sql:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "AZURE_OPENAI_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:text2sql/azure-openai-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/text2sql",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/api/v1/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to AWS Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: text2sql
  ECS_SERVICE: text2sql-service
  ECS_CLUSTER: text2sql-cluster

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
          
      - name: Run tests
        run: |
          pytest --cov=app --cov-report=xml --cov-report=term-missing
          
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          
      - name: Upload Trivy scan results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  build-and-deploy:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

      - name: Deploy to ECS
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          aws ecs update-service \
            --cluster $ECS_CLUSTER \
            --service $ECS_SERVICE \
            --force-new-deployment \
            --task-definition text2sql-backend:LATEST

      - name: Wait for deployment
        run: |
          aws ecs wait services-stable \
            --cluster $ECS_CLUSTER \
            --services $ECS_SERVICE
```

### Infrastructure as Code (Terraform)

```hcl
# infrastructure/main.tf
terraform {
  required_version = ">= 1.0"
  backend "s3" {
    bucket = "text2sql-terraform-state"
    key    = "production/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "text2sql"
      Environment = "production"
      ManagedBy   = "terraform"
    }
  }
}

# VPC Configuration
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "text2sql-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  
  enable_nat_gateway = true
  enable_vpn_gateway = false
  enable_dns_hostnames = true
  enable_dns_support = true
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "text2sql-cluster"
  
  configuration {
    execute_command_configuration {
      logging = "OVERRIDE"
      
      log_configuration {
        cloud_watch_log_group_name = aws_cloudwatch_log_group.ecs.name
      }
    }
  }
}

# RDS SQL Server
resource "aws_db_instance" "main" {
  identifier = "text2sql-db"
  
  engine         = "sqlserver-ex"
  engine_version = "15.00.4236.7.v1"
  instance_class = "db.t3.small"
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type          = "gp3"
  storage_encrypted     = true
  
  db_name  = "text2sql"
  username = "admin"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = false
  final_snapshot_identifier = "text2sql-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"
  
  performance_insights_enabled = true
  monitoring_interval         = 60
  monitoring_role_arn         = aws_iam_role.rds_monitoring.arn
}
```

---

## MLOps Strategy

### Prompt Management System

```python
# Prompt versioning and management
class PromptManager:
    def __init__(self, s3_bucket: str):
        self.s3_client = boto3.client('s3')
        self.bucket = s3_bucket
        self.cache = {}
    
    async def get_prompt(self, prompt_id: str, version: str = "latest"):
        cache_key = f"{prompt_id}:{version}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket,
                Key=f"prompts/{prompt_id}/{version}.txt"
            )
            prompt_content = response['Body'].read().decode('utf-8')
            self.cache[cache_key] = prompt_content
            return prompt_content
        except Exception as e:
            logger.error(f"Failed to get prompt {prompt_id}:{version}: {e}")
            raise
    
    async def update_prompt(self, prompt_id: str, content: str):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        version = f"v{timestamp}"
        
        # Store versioned prompt
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=f"prompts/{prompt_id}/{version}.txt",
            Body=content.encode('utf-8'),
            Metadata={
                'updated_by': 'system',
                'timestamp': timestamp
            }
        )
        
        # Update latest pointer
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=f"prompts/{prompt_id}/latest.txt",
            Body=content.encode('utf-8')
        )
```

### Model Performance Monitoring

```python
# Query performance tracking
class QueryPerformanceTracker:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
    
    async def track_query_performance(self, query_metadata: dict):
        metrics = [
            {
                'MetricName': 'QueryResponseTime',
                'Value': query_metadata['response_time_ms'],
                'Unit': 'Milliseconds',
                'Dimensions': [
                    {'Name': 'QueryType', 'Value': query_metadata['query_type']},
                    {'Name': 'DatabaseTable', 'Value': query_metadata['primary_table']}
                ]
            },
            {
                'MetricName': 'QueryAccuracy',
                'Value': query_metadata['accuracy_score'],
                'Unit': 'Percent',
                'Dimensions': [
                    {'Name': 'ModelVersion', 'Value': query_metadata['model_version']}
                ]
            }
        ]
        
        self.cloudwatch.put_metric_data(
            Namespace='TextToSQL',
            MetricData=metrics
        )
```

### A/B Testing Framework

```python
# Prompt A/B testing
class PromptABTesting:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.experiments = {}
    
    async def get_prompt_variant(self, user_id: str, experiment_id: str):
        user_hash = hashlib.md5(user_id.encode()).hexdigest()
        variant_number = int(user_hash, 16) % 100
        
        experiment_config = await self.get_experiment_config(experiment_id)
        
        if variant_number < experiment_config['control_percentage']:
            return 'control'
        else:
            return 'variant'
    
    async def record_experiment_result(self, user_id: str, experiment_id: str, 
                                     variant: str, success: bool):
        key = f"experiment:{experiment_id}:{variant}"
        await self.redis.hincrby(key, 'total_queries', 1)
        if success:
            await self.redis.hincrby(key, 'successful_queries', 1)
```

---

## Monitoring and Observability

### CloudWatch Dashboard Configuration

```python
# Custom CloudWatch dashboard
def create_monitoring_dashboard():
    cloudwatch = boto3.client('cloudwatch')
    
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/ECS", "CPUUtilization", "ServiceName", "text2sql-service"],
                        [".", "MemoryUtilization", ".", "."]
                    ],
                    "period": 300,
                    "stat": "Average",
                    "region": "us-east-1",
                    "title": "ECS Performance"
                }
            },
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["TextToSQL", "QueryResponseTime"],
                        [".", "QueryAccuracy"],
                        [".", "DatabaseConnectionErrors"]
                    ],
                    "period": 300,
                    "stat": "Average",
                    "region": "us-east-1",
                    "title": "Application Metrics"
                }
            }
        ]
    }
    
    cloudwatch.put_dashboard(
        DashboardName='Text2SQL-Production',
        DashboardBody=json.dumps(dashboard_body)
    )
```

### Alerting Strategy

```yaml
# CloudFormation template for alerts
Resources:
  HighErrorRateAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: Text2SQL-HighErrorRate
      AlarmDescription: Alert when error rate exceeds 5%
      MetricName: ErrorRate
      Namespace: AWS/ApplicationELB
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 5
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref SNSTopicArn
      
  DatabaseConnectionAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: Text2SQL-DatabaseConnectionFailure
      AlarmDescription: Alert when database connections fail
      MetricName: DatabaseConnectionErrors
      Namespace: TextToSQL
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 1
      Threshold: 5
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref SNSTopicArn
```

---

## Step-by-Step Implementation Guide

### Phase 1: Foundation Setup (Weeks 1-2)

#### Week 1: AWS Account and Basic Infrastructure
1. **Day 1-2: AWS Account Setup**
   ```bash
   # Install AWS CLI and Terraform
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip && sudo ./aws/install
   
   # Configure AWS CLI
   aws configure set region us-east-1
   aws configure set output json
   ```

2. **Day 3-4: VPC and Networking**
   ```bash
   # Apply base infrastructure
   cd infrastructure/
   terraform init
   terraform plan -var-file="production.tfvars"
   terraform apply
   ```

3. **Day 5: Security Groups and IAM**
   ```bash
   # Create IAM roles and policies
   aws iam create-role --role-name text2sql-ecs-task-role \
     --assume-role-policy-document file://ecs-task-role-policy.json
   
   aws iam attach-role-policy --role-name text2sql-ecs-task-role \
     --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite
   ```

#### Week 2: Database and Core Services
1. **Day 1-2: RDS SQL Server Setup**
   ```bash
   # Create database subnet group
   aws rds create-db-subnet-group \
     --db-subnet-group-name text2sql-subnet-group \
     --db-subnet-group-description "Subnet group for Text2SQL" \
     --subnet-ids subnet-12345 subnet-67890
   
   # Create RDS instance
   aws rds create-db-instance \
     --db-instance-identifier text2sql-prod-db \
     --db-instance-class db.r6i.large \
     --engine sqlserver-ex \
     --allocated-storage 500 \
     --db-name text2sql \
     --master-username admin \
     --master-user-password $(aws secretsmanager get-secret-value --secret-id rds-password --query SecretString --output text)
   ```

2. **Day 3-4: Redis Cache and OpenSearch**
   ```bash
   # Create ElastiCache Redis cluster
   aws elasticache create-cache-cluster \
     --cache-cluster-id text2sql-cache \
     --cache-node-type cache.r6g.large \
     --engine redis \
     --num-cache-nodes 1 \
     --cache-subnet-group-name text2sql-cache-subnet
   ```

3. **Day 5: Secrets Manager Setup**
   ```bash
   # Store Azure OpenAI credentials
   aws secretsmanager create-secret \
     --name text2sql/azure-openai \
     --description "Azure OpenAI API credentials" \
     --secret-string '{
       "endpoint": "https://your-endpoint.openai.azure.com/",
       "key": "your-api-key",
       "deployment_name": "gpt-4"
     }'
   ```

### Phase 2: Application Migration (Weeks 3-4)

#### Week 3: Backend Migration
1. **Day 1-2: Code Refactoring**
   ```python
   # Update configuration to use AWS services
   # app/config/aws_settings.py
   import boto3
   from botocore.exceptions import ClientError
   
   class AWSSettings:
       def __init__(self):
           self.secrets_client = boto3.client('secretsmanager')
           self.ssm_client = boto3.client('ssm')
       
       def get_secret(self, secret_name: str):
           try:
               response = self.secrets_client.get_secret_value(SecretId=secret_name)
               return json.loads(response['SecretString'])
           except ClientError as e:
               logger.error(f"Failed to retrieve secret {secret_name}: {e}")
               raise
   ```

2. **Day 3-4: Container Optimization**
   ```dockerfile
   # Multi-stage production Dockerfile
   FROM node:18-alpine AS frontend-builder
   WORKDIR /app
   COPY src_frontend/package*.json ./
   RUN npm ci --only=production && npm cache clean --force
   COPY src_frontend/ ./
   RUN npm run build
   
   FROM python:3.11-slim AS backend
   # Copy frontend build and setup backend
   COPY --from=frontend-builder /app/build ./static/
   # ... rest of backend setup
   ```

3. **Day 5: Database Migration**
   ```sql
   -- Migration script for production database
   USE [text2sql]
   GO
   
   -- Create production tables with optimizations
   CREATE TABLE [transaction_history] (
       [transaction_id] UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
       [customer_id] UNIQUEIDENTIFIER NOT NULL,
       [transaction_date] DATETIME2 NOT NULL,
       [amount] DECIMAL(18,2) NOT NULL,
       [transaction_type] NVARCHAR(50) NOT NULL,
       [created_at] DATETIME2 DEFAULT GETUTCDATE(),
       INDEX IX_transaction_date (transaction_date),
       INDEX IX_customer_id (customer_id)
   )
   GO
   ```

#### Week 4: ECS Deployment
1. **Day 1-2: ECS Task Definition**
   ```json
   {
     "family": "text2sql-backend",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "2048",
     "memory": "4096",
     "taskRoleArn": "arn:aws:iam::account:role/text2sql-task-role",
     "executionRoleArn": "arn:aws:iam::account:role/text2sql-execution-role"
   }
   ```

2. **Day 3-4: Service Configuration**
   ```bash
   # Create ECS service
   aws ecs create-service \
     --cluster text2sql-cluster \
     --service-name text2sql-service \
     --task-definition text2sql-backend:1 \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-12345],assignPublicIp=DISABLED}"
   ```

3. **Day 5: Load Balancer Setup**
   ```bash
   # Create Application Load Balancer
   aws elbv2 create-load-balancer \
     --name text2sql-alb \
     --subnets subnet-12345 subnet-67890 \
     --security-groups sg-alb-12345
   ```

### Phase 3: Production Hardening (Weeks 5-6)

#### Week 5: Security Implementation
1. **Day 1-2: Cognito Setup**
   ```bash
   # Create Cognito User Pool
   aws cognito-idp create-user-pool \
     --pool-name text2sql-users \
     --policies '{
       "PasswordPolicy": {
         "MinimumLength": 12,
         "RequireUppercase": true,
         "RequireLowercase": true,
         "RequireNumbers": true,
         "RequireSymbols": true
       }
     }' \
     --mfa-configuration ON
   ```

2. **Day 3-4: WAF Configuration**
   ```bash
   # Create WAF rules
   aws wafv2 create-web-acl \
     --name text2sql-waf \
     --description "WAF for Text2SQL application" \
     --default-action Allow={} \
     --rules file://waf-rules.json
   ```

3. **Day 5: SSL/TLS Setup**
   ```bash
   # Request SSL certificate
   aws acm request-certificate \
     --domain-name text2sql.yourdomain.com \
     --validation-method DNS \
     --subject-alternative-names "*.text2sql.yourdomain.com"
   ```

#### Week 6: Monitoring and Alerting
1. **Day 1-2: CloudWatch Setup**
   ```python
   # Custom metrics implementation
   def send_custom_metric(metric_name: str, value: float, unit: str = 'Count'):
       cloudwatch = boto3.client('cloudwatch')
       cloudwatch.put_metric_data(
           Namespace='TextToSQL',
           MetricData=[{
               'MetricName': metric_name,
               'Value': value,
               'Unit': unit,
               'Timestamp': datetime.utcnow()
           }]
       )
   ```

2. **Day 3-4: Log Aggregation**
   ```bash
   # Create CloudWatch Log Groups
   aws logs create-log-group --log-group-name /ecs/text2sql
   aws logs create-log-group --log-group-name /aws/rds/instance/text2sql-db/error
   ```

3. **Day 5: Performance Testing**
   ```bash
   # Load testing with k6
   k6 run --vus 100 --duration 30s load-test.js
   ```

### Phase 4: Go-Live and Optimization (Weeks 7-8)

#### Week 7: Production Deployment
1. **Day 1-2: Final Testing**
2. **Day 3-4: DNS and CDN Setup**
3. **Day 5: Production Cutover**

#### Week 8: Post-Deployment Optimization
1. **Day 1-2: Performance Monitoring**
2. **Day 3-4: Cost Optimization**
3. **Day 5: Documentation and Handover**

---

## Cost Optimization

### Monthly Cost Estimation

| Service | Configuration | Monthly Cost (USD) |
|---------|---------------|-------------------|
| **Compute** | | |
| ECS Fargate | 4 vCPU, 8GB RAM, 2 tasks | $180 |
| ALB | Standard load balancer | $20 |
| **Storage** | | |
| RDS SQL Server | db.r6i.large, 500GB | $450 |
| ElastiCache Redis | cache.r6g.large | $150 |
| OpenSearch | t3.small.search, 3 nodes | $180 |
| S3 | 100GB standard storage | $25 |
| **Networking** | | |
| CloudFront | 1TB data transfer | $85 |
| Route 53 | 1M queries | $0.50 |
| **Security & Monitoring** | | |
| Secrets Manager | 10 secrets | $4 |
| CloudWatch | Standard monitoring | $30 |
| WAF | 10M requests | $60 |
| **Total Estimated Monthly Cost** | | **$1,184.50** |

### Cost Optimization Strategies

1. **Reserved Instances**: 40% savings on RDS
2. **Spot Instances**: Use for non-critical workloads
3. **Auto Scaling**: Scale down during off-hours
4. **S3 Lifecycle Policies**: Archive old data to Glacier
5. **CloudFront Caching**: Reduce backend load

---

## Risk Management

### Risk Assessment Matrix

| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| Azure OpenAI Service Outage | Medium | High | Implement circuit breaker pattern, fallback to cached responses |
| Database Connection Failure | Low | High | Connection pooling, retry logic, read replicas |
| Container Memory Issues | Medium | Medium | Memory monitoring, auto-scaling, health checks |
| Security Breach | Low | High | WAF, encryption, regular security audits |
| Data Loss | Low | High | Multi-AZ backups, point-in-time recovery |
| Performance Degradation | Medium | Medium | Auto-scaling, performance monitoring, caching |

### Disaster Recovery Plan

#### RTO/RPO Targets
- **Recovery Time Objective (RTO)**: 4 hours
- **Recovery Point Objective (RPO)**: 1 hour

#### Backup Strategy
```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
aws rds create-db-snapshot \
  --db-instance-identifier text2sql-prod-db \
  --db-snapshot-identifier text2sql-backup-$DATE

# Application data backup
aws s3 sync s3://text2sql-data/ s3://text2sql-backup/data/$DATE/

# Configuration backup
aws s3 cp s3://text2sql-config/ s3://text2sql-backup/config/$DATE/ --recursive
```

---

## Post-Deployment Operations

### Health Check Endpoints

```python
# Comprehensive health check
@app.get("/api/v1/health/detailed")
async def detailed_health_check():
    health_status = {
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "production",
        "version": "1.0.0",
        "services": {}
    }
    
    # Database health
    try:
        async with get_db_connection() as conn:
            await conn.execute("SELECT 1")
        health_status["services"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["services"]["database"] = {"status": "unhealthy", "error": str(e)}
    
    # Azure OpenAI health
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Health check"}],
            max_tokens=1
        )
        health_status["services"]["azure_openai"] = {"status": "healthy"}
    except Exception as e:
        health_status["services"]["azure_openai"] = {"status": "unhealthy", "error": str(e)}
    
    # Redis health
    try:
        await redis_client.ping()
        health_status["services"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health_status["services"]["redis"] = {"status": "unhealthy", "error": str(e)}
    
    return health_status
```

### Maintenance Procedures

#### Database Maintenance
```sql
-- Weekly maintenance script
USE [text2sql]
GO

-- Update statistics
UPDATE STATISTICS [transaction_history]
UPDATE STATISTICS [customer_information]

-- Reindex fragmented indexes
ALTER INDEX ALL ON [transaction_history] REORGANIZE
ALTER INDEX ALL ON [customer_information] REORGANIZE

-- Clean up old sessions
DELETE FROM [user_sessions] 
WHERE [last_activity] < DATEADD(DAY, -30, GETUTCDATE())
```

#### Application Maintenance
```bash
#!/bin/bash
# Monthly maintenance script

# Clear old logs
aws logs delete-log-stream \
  --log-group-name /ecs/text2sql \
  --log-stream-name old-stream-name

# Update container images
aws ecs update-service \
  --cluster text2sql-cluster \
  --service text2sql-service \
  --force-new-deployment

# Restart cache
aws elasticache reboot-cache-cluster \
  --cache-cluster-id text2sql-cache
```

---

## Conclusion

This comprehensive deployment plan provides a roadmap for migrating the Text2SQL AI Analyst application from a POC to a production-ready system on AWS. The plan addresses:

1. **Scalability**: Auto-scaling ECS services and RDS read replicas
2. **Security**: Enterprise authentication, encryption, and WAF protection
3. **Reliability**: Multi-AZ deployment with disaster recovery
4. **Performance**: Caching, CDN, and database optimization
5. **Cost Efficiency**: Right-sized resources with optimization strategies
6. **Operational Excellence**: Comprehensive monitoring and automated deployment

### Next Steps

1. **Week 1**: Begin AWS account setup and infrastructure provisioning
2. **Week 2**: Start application code refactoring for cloud deployment
3. **Week 3**: Implement security and authentication changes
4. **Week 4**: Begin migration testing in staging environment
5. **Week 5**: Production deployment and go-live
6. **Week 6**: Post-deployment optimization and monitoring setup

This plan ensures a smooth transition from POC to production while maintaining high standards for security, performance, and reliability required for enterprise deployment.
