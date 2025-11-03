# Lesson 8: Productionizing Your Agent - API Deployment with FastAPI

This lesson teaches you how to transform your AI agents from prototype notebooks into production-ready web services using FastAPI. You'll learn to build robust, scalable APIs that can serve your AI agents to users and applications.

## Learning Objectives

By the end of this lesson, you will be able to:

1. Design and implement RESTful APIs for AI agent services
2. Use FastAPI to create high-performance, async web services
3. Implement proper request/response models with Pydantic
4. Handle authentication and authorization for API endpoints
5. Add comprehensive error handling and logging
6. Deploy APIs with proper monitoring and health checks
7. Implement rate limiting and security best practices

## Table of Contents

- [Why API Deployment Matters](#why-api-deployment-matters)
- [FastAPI vs Other Frameworks](#fastapi-vs-other-frameworks)
- [API Architecture Design](#api-architecture-design)
- [Core Implementation](#core-implementation)
- [1. Basic FastAPI Setup](#1-basic-fastapi-setup)
- [2. Request/Response Models](#2-requestresponse-models)
- [3. AI Agent Integration](#3-ai-agent-integration)
- [4. Async Operations](#4-async-operations)
- [5. Error Handling](#5-error-handling)
- [6. Authentication & Security](#6-authentication--security)
- [7. Monitoring & Logging](#7-monitoring--logging)
- [8. Rate Limiting](#8-rate-limiting)
- [Production Deployment](#production-deployment)
- [Best Practices](#best-practices)

## Why API Deployment Matters

### From Prototype to Production

**Prototype Limitations:**
- **Limited Access**: Only available in development environment
- **No Scalability**: Can't handle multiple concurrent users
- **No Integration**: Difficult to integrate with other applications
- **No Monitoring**: No visibility into usage and performance
- **No Security**: No authentication or authorization controls

**Production API Benefits:**
- **Universal Access**: Available to users and applications anywhere
- **Scalability**: Handle thousands of concurrent requests
- **Integration Ready**: Easy to integrate with web apps, mobile apps, and other services
- **Monitoring**: Complete visibility into usage, performance, and errors
- **Security**: Proper authentication, authorization, and rate limiting
- **Reliability**: Error handling, retries, and graceful degradation

## FastAPI vs Other Frameworks

### Framework Comparison

| Feature | FastAPI | Flask | Django REST |
|---------|---------|-------|-------------|
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Async Support** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Auto Documentation** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| **Type Safety** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Learning Curve** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Data Validation** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |

### Why FastAPI for AI Services

- **High Performance**: Built on Starlette and Pydantic for maximum speed
- **Async Native**: Perfect for I/O-bound AI operations
- **Automatic Documentation**: Interactive API docs with Swagger UI
- **Type Safety**: Catch errors at development time
- **Modern Python**: Leverages Python 3.6+ features like type hints

## API Architecture Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI AGENT API ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                       Client Requests                          │
│                           │                                    │
│                           ▼                                    │
│                 ┌─────────────────┐                           │
│                 │   LOAD BALANCER │                           │
│                 │    (Optional)   │                           │
│                 └─────────────────┘                           │
│                           │                                    │
│                           ▼                                    │
│                 ┌─────────────────┐                           │
│                 │   FASTAPI APP   │                           │
│                 │                 │                           │
│                 │ ┌─────────────┐ │                           │
│                 │ │Middleware   │ │                           │
│                 │ │- CORS       │ │                           │
│                 │ │- Auth       │ │                           │
│                 │ │- Rate Limit │ │                           │
│                 │ │- Logging    │ │                           │
│                 │ └─────────────┘ │                           │
│                 │                 │                           │
│                 │ ┌─────────────┐ │                           │
│                 │ │API Routes   │ │                           │
│                 │ │- /chat      │ │                           │
│                 │ │- /search    │ │                           │
│                 │ │- /analyze   │ │                           │
│                 │ │- /health    │ │                           │
│                 │ └─────────────┘ │                           │
│                 └─────────────────┘                           │
│                           │                                    │
│                           ▼                                    │
│                 ┌─────────────────┐                           │
│                 │   AI AGENT      │                           │
│                 │   MANAGER       │                           │
│                 │                 │                           │
│                 │ ┌─────────────┐ │                           │
│                 │ │Chat Agent   │ │                           │
│                 │ └─────────────┘ │                           │
│                 │ ┌─────────────┐ │                           │
│                 │ │RAG Agent    │ │                           │
│                 │ └─────────────┘ │                           │
│                 │ ┌─────────────┐ │                           │
│                 │ │Analysis     │ │                           │
│                 │ │Agent        │ │                           │
│                 │ └─────────────┘ │                           │
│                 └─────────────────┘                           │
│                           │                                    │
│                           ▼                                    │
│        ┌─────────────────────────────────────────────────┐    │
│        │              EXTERNAL SERVICES                  │    │
│        │                                                 │    │
│        │ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │    │
│        │ │   LLM API   │  │  Vector DB  │  │   Cache     │ │    │
│        │ │ (OpenAI)    │  │ (Pinecone)  │  │  (Redis)    │ │    │
│        │ └─────────────┘  └─────────────┘  └─────────────┘ │    │
│        └─────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Request Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       REQUEST FLOW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Client Request                                                │
│       │                                                        │
│       ▼                                                        │
│ ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│ │   Request   │───▶│ Validation  │───▶│    Auth     │         │
│ │  Received   │    │   Layer     │    │   Layer     │         │
│ └─────────────┘    └─────────────┘    └─────────────┘         │
│       │                  │                  │                 │
│       ▼                  ▼                  ▼                 │
│ ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│ │Rate Limit   │───▶│   Cache     │───▶│  AI Agent   │         │
│ │   Check     │    │   Check     │    │ Processing  │         │
│ └─────────────┘    └─────────────┘    └─────────────┘         │
│       │                  │                  │                 │
│       ▼                  ▼                  ▼                 │
│ ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│ │   Error     │───▶│   Cache     │───▶│  Response   │         │
│ │  Handling   │    │   Update    │    │ Formatting  │         │
│ └─────────────┘    └─────────────┘    └─────────────┘         │
│       │                  │                  │                 │
│       └──────────────────┼──────────────────┘                 │
│                          ▼                                    │
│                   Client Response                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Core Implementation

### Project Structure

```
ai_agent_api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Configuration settings
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py      # Request models
│   │   └── responses.py     # Response models
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py      # Chat endpoint
│   │   │   ├── search.py    # Search endpoint
│   │   │   └── health.py    # Health check
│   │   └── dependencies.py  # Dependency injection
│   ├── services/
│   │   ├── __init__.py
│   │   ├── agent_manager.py # AI agent management
│   │   ├── chat_service.py  # Chat logic
│   │   └── search_service.py # Search logic
│   ├── core/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication
│   │   ├── security.py      # Security utilities
│   │   └── logging.py       # Logging configuration
│   └── middleware/
│       ├── __init__.py
│       ├── cors.py          # CORS middleware
│       ├── rate_limit.py    # Rate limiting
│       └── error_handler.py # Error handling
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_agents.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## 1. Basic FastAPI Setup

### Main Application Setup

```python
# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.api.routes import chat, search, health
from app.middleware.error_handler import CustomErrorHandler
from app.middleware.rate_limit import RateLimitMiddleware
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting AI Agent API...")
    # Startup
    yield
    # Shutdown
    logger.info("Shutting down AI Agent API...")

# Initialize FastAPI app
app = FastAPI(
    title="AI Agent API",
    description="Production-ready API for AI agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(CustomErrorHandler)
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
```

### Configuration Management

```python
# app/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # API Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # AI Service Settings
    OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_VERSION: str = "2023-05-15"
    
    # Database
    REDIS_URL: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

## 2. Request/Response Models

### Pydantic Models for Data Validation

```python
# app/models/requests.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    user_id: Optional[str] = Field(None, description="User identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Number of results")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    include_metadata: bool = Field(False, description="Include metadata in results")

class AnalysisRequest(BaseModel):
    """Analysis request model"""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to analyze")
    analysis_type: str = Field(..., description="Type of analysis")
    options: Optional[Dict[str, Any]] = Field(None, description="Analysis options")
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        allowed_types = ['sentiment', 'summarization', 'classification', 'extraction']
        if v not in allowed_types:
            raise ValueError(f'Analysis type must be one of: {allowed_types}')
        return v

class BatchRequest(BaseModel):
    """Batch processing request model"""
    requests: List[Dict[str, Any]] = Field(..., min_items=1, max_items=100)
    batch_id: Optional[str] = Field(None, description="Batch identifier")
    priority: int = Field(1, ge=1, le=10, description="Processing priority")
```

```python
# app/models/responses.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"

class BaseResponse(BaseModel):
    """Base response model"""
    status: ResponseStatus = Field(..., description="Response status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier")

class ChatResponse(BaseResponse):
    """Chat response model"""
    message: str = Field(..., description="AI response message")
    conversation_id: str = Field(..., description="Conversation ID")
    tokens_used: int = Field(..., description="Number of tokens used")
    response_time: float = Field(..., description="Response time in seconds")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Response confidence")
    sources: Optional[List[str]] = Field(None, description="Information sources")

class SearchResponse(BaseResponse):
    """Search response model"""
    results: List[Dict[str, Any]] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
    query: str = Field(..., description="Original search query")
    search_time: float = Field(..., description="Search time in seconds")

class AnalysisResponse(BaseResponse):
    """Analysis response model"""
    analysis_result: Dict[str, Any] = Field(..., description="Analysis results")
    analysis_type: str = Field(..., description="Type of analysis performed")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Analysis confidence")
    processing_time: float = Field(..., description="Processing time in seconds")

class ErrorResponse(BaseResponse):
    """Error response model"""
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.now)
    dependencies: Dict[str, str] = Field(..., description="Dependency status")
    uptime: float = Field(..., description="Uptime in seconds")
```

## 3. AI Agent Integration

### Agent Manager Service

```python
# app/services/agent_manager.py
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.stats = {
            'requests_handled': 0,
            'total_response_time': 0,
            'errors': 0,
            'last_used': None
        }
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return response"""
        pass
    
    def update_stats(self, response_time: float, error: bool = False):
        """Update agent statistics"""
        self.stats['requests_handled'] += 1
        self.stats['total_response_time'] += response_time
        if error:
            self.stats['errors'] += 1
        self.stats['last_used'] = datetime.now()
    
    def get_avg_response_time(self) -> float:
        """Calculate average response time"""
        if self.stats['requests_handled'] == 0:
            return 0
        return self.stats['total_response_time'] / self.stats['requests_handled']

class ChatAgent(BaseAgent):
    """Chat agent implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("chat_agent", config)
        self.llm_client = self._initialize_llm_client()
    
    def _initialize_llm_client(self):
        """Initialize LLM client"""
        # Implementation depends on your LLM provider
        pass
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process chat message"""
        start_time = datetime.now()
        
        try:
            message = input_data.get('message')
            conversation_id = input_data.get('conversation_id')
            
            # Get conversation context
            context = await self._get_conversation_context(conversation_id)
            
            # Generate response
            response = await self._generate_response(message, context)
            
            # Update conversation
            await self._update_conversation(conversation_id, message, response)
            
            response_time = (datetime.now() - start_time).total_seconds()
            self.update_stats(response_time)
            
            return {
                'message': response,
                'conversation_id': conversation_id,
                'tokens_used': self._count_tokens(message + response),
                'response_time': response_time
            }
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            self.update_stats(response_time, error=True)
            logger.error(f"Chat agent error: {str(e)}")
            raise
    
    async def _get_conversation_context(self, conversation_id: str) -> str:
        """Get conversation context"""
        # Implementation for retrieving conversation history
        return ""
    
    async def _generate_response(self, message: str, context: str) -> str:
        """Generate AI response"""
        # Implementation for LLM response generation
        return "AI response placeholder"
    
    async def _update_conversation(self, conversation_id: str, message: str, response: str):
        """Update conversation history"""
        # Implementation for storing conversation
        pass
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        # Simple token counting - replace with actual tokenizer
        return len(text.split())

class SearchAgent(BaseAgent):
    """Search agent implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("search_agent", config)
        self.vector_store = self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize vector store"""
        # Implementation depends on your vector store
        pass
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process search query"""
        start_time = datetime.now()
        
        try:
            query = input_data.get('query')
            limit = input_data.get('limit', 10)
            filters = input_data.get('filters', {})
            
            # Perform search
            results = await self._search_documents(query, limit, filters)
            
            response_time = (datetime.now() - start_time).total_seconds()
            self.update_stats(response_time)
            
            return {
                'results': results,
                'total_results': len(results),
                'query': query,
                'search_time': response_time
            }
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            self.update_stats(response_time, error=True)
            logger.error(f"Search agent error: {str(e)}")
            raise
    
    async def _search_documents(self, query: str, limit: int, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search documents in vector store"""
        # Implementation for vector search
        return []

class AgentManager:
    """Manages multiple AI agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.load_balancer = RoundRobinLoadBalancer()
    
    def register_agent(self, agent_type: str, agent: BaseAgent):
        """Register an agent"""
        self.agents[agent_type] = agent
        logger.info(f"Registered agent: {agent_type}")
    
    async def process_request(self, agent_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request with appropriate agent"""
        if agent_type not in self.agents:
            raise ValueError(f"Agent type '{agent_type}' not found")
        
        agent = self.agents[agent_type]
        return await agent.process(input_data)
    
    def get_agent_stats(self, agent_type: str) -> Dict[str, Any]:
        """Get agent statistics"""
        if agent_type not in self.agents:
            raise ValueError(f"Agent type '{agent_type}' not found")
        
        return self.agents[agent_type].stats
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all agents"""
        return {
            agent_type: agent.stats 
            for agent_type, agent in self.agents.items()
        }

class RoundRobinLoadBalancer:
    """Simple round-robin load balancer"""
    
    def __init__(self):
        self.counters = {}
    
    def get_next_agent(self, agent_list: List[BaseAgent]) -> BaseAgent:
        """Get next agent using round-robin"""
        if not agent_list:
            raise ValueError("No agents available")
        
        agent_key = id(agent_list)
        if agent_key not in self.counters:
            self.counters[agent_key] = 0
        
        agent = agent_list[self.counters[agent_key] % len(agent_list)]
        self.counters[agent_key] += 1
        
        return agent

# Global agent manager instance
agent_manager = AgentManager()
```

## 4. Async Operations

### Async Route Handlers

```python
# app/api/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import asyncio
import json
from typing import AsyncGenerator

from app.models.requests import ChatRequest, BatchRequest
from app.models.responses import ChatResponse, ErrorResponse
from app.services.agent_manager import agent_manager
from app.core.auth import get_current_user
from app.core.security import rate_limit

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Chat endpoint with async processing"""
    try:
        # Add user context
        input_data = {
            **request.dict(),
            'user_id': current_user.get('user_id')
        }
        
        # Process with chat agent
        result = await agent_manager.process_request('chat', input_data)
        
        # Log interaction in background
        background_tasks.add_task(
            log_interaction,
            user_id=current_user.get('user_id'),
            request_data=request.dict(),
            response_data=result
        )
        
        return ChatResponse(
            status="success",
            request_id=generate_request_id(),
            **result
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Streaming chat endpoint"""
    async def generate_response() -> AsyncGenerator[str, None]:
        try:
            # Add user context
            input_data = {
                **request.dict(),
                'user_id': current_user.get('user_id')
            }
            
            # Get streaming response from agent
            async for chunk in agent_manager.stream_response('chat', input_data):
                yield f"data: {json.dumps(chunk)}\n\n"
                
        except Exception as e:
            error_chunk = {
                'error': str(e),
                'status': 'error'
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.post("/chat/batch")
async def chat_batch(
    request: BatchRequest,
    current_user: dict = Depends(get_current_user)
):
    """Batch chat processing"""
    try:
        # Process requests concurrently
        tasks = []
        for req_data in request.requests:
            task = agent_manager.process_request('chat', {
                **req_data,
                'user_id': current_user.get('user_id')
            })
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        responses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                responses.append({
                    'status': 'error',
                    'error': str(result),
                    'request_index': i
                })
            else:
                responses.append({
                    'status': 'success',
                    'result': result,
                    'request_index': i
                })
        
        return {
            'batch_id': request.batch_id,
            'total_requests': len(request.requests),
            'responses': responses,
            'status': 'completed'
        }
        
    except Exception as e:
        logger.error(f"Batch chat endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch processing error: {str(e)}"
        )

async def log_interaction(user_id: str, request_data: dict, response_data: dict):
    """Log user interaction in background"""
    try:
        # Implementation for logging user interactions
        logger.info(f"User {user_id} interaction logged")
    except Exception as e:
        logger.error(f"Failed to log interaction: {str(e)}")

def generate_request_id() -> str:
    """Generate unique request ID"""
    import uuid
    return str(uuid.uuid4())
```

## 5. Error Handling

### Comprehensive Error Handling

```python
# app/middleware/error_handler.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)

class CustomErrorHandler(BaseHTTPMiddleware):
    """Custom error handling middleware"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            return await self.handle_http_exception(request, e)
        except Exception as e:
            return await self.handle_general_exception(request, e)
    
    async def handle_http_exception(self, request: Request, exc: HTTPException):
        """Handle HTTP exceptions"""
        logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error_code": f"HTTP_{exc.status_code}",
                "error_message": exc.detail,
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url)
            }
        )
    
    async def handle_general_exception(self, request: Request, exc: Exception):
        """Handle general exceptions"""
        logger.error(f"Unhandled exception: {str(exc)}")
        logger.error(traceback.format_exc())
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error_code": "INTERNAL_ERROR",
                "error_message": "An internal server error occurred",
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url)
            }
        )

# Custom exception classes
class AgentError(Exception):
    """Base exception for agent-related errors"""
    pass

class AgentNotFoundError(AgentError):
    """Agent not found error"""
    pass

class AgentProcessingError(AgentError):
    """Agent processing error"""
    pass

class ValidationError(Exception):
    """Data validation error"""
    pass

class RateLimitError(Exception):
    """Rate limit exceeded error"""
    pass

class AuthenticationError(Exception):
    """Authentication error"""
    pass

class AuthorizationError(Exception):
    """Authorization error"""
    pass

# Exception handlers
from fastapi import FastAPI

def setup_exception_handlers(app: FastAPI):
    """Setup custom exception handlers"""
    
    @app.exception_handler(AgentNotFoundError)
    async def agent_not_found_handler(request: Request, exc: AgentNotFoundError):
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "error_code": "AGENT_NOT_FOUND",
                "error_message": str(exc),
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.exception_handler(AgentProcessingError)
    async def agent_processing_error_handler(request: Request, exc: AgentProcessingError):
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error_code": "AGENT_PROCESSING_ERROR",
                "error_message": str(exc),
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "error_code": "VALIDATION_ERROR",
                "error_message": str(exc),
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.exception_handler(RateLimitError)
    async def rate_limit_error_handler(request: Request, exc: RateLimitError):
        return JSONResponse(
            status_code=429,
            content={
                "status": "error",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "error_message": str(exc),
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(
            status_code=401,
            content={
                "status": "error",
                "error_code": "AUTHENTICATION_ERROR",
                "error_message": str(exc),
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.exception_handler(AuthorizationError)
    async def authorization_error_handler(request: Request, exc: AuthorizationError):
        return JSONResponse(
            status_code=403,
            content={
                "status": "error",
                "error_code": "AUTHORIZATION_ERROR",
                "error_message": str(exc),
                "timestamp": datetime.now().isoformat()
            }
        )
```

## 6. Authentication & Security

### JWT Authentication

```python
# app/core/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import secrets

from app.config import settings

security = HTTPBearer()

class AuthManager:
    """Authentication manager"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def hash_password(self, password: str) -> str:
        """Hash password"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            salt, password_hash = hashed_password.split(':')
            computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return computed_hash.hex() == password_hash
        except:
            return False

# Global auth manager
auth_manager = AuthManager()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = auth_manager.verify_token(token)
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # In production, you would fetch user details from database
        user = {
            "user_id": user_id,
            "email": payload.get("email"),
            "roles": payload.get("roles", [])
        }
        
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_roles(required_roles: List[str]):
    """Require specific roles for endpoint access"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_roles = current_user.get("roles", [])
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker

# Authentication routes
from fastapi import APIRouter
from pydantic import BaseModel

auth_router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

@auth_router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """User login endpoint"""
    # In production, validate credentials against database
    user = authenticate_user(request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_manager.create_access_token(
        data={"sub": user["user_id"], "email": user["email"], "roles": user["roles"]}
    )
    
    return LoginResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user credentials"""
    # In production, this would query your user database
    # For demo purposes, we'll use a mock user
    mock_user = {
        "user_id": "user123",
        "email": "user@example.com",
        "password_hash": auth_manager.hash_password("password123"),
        "roles": ["user"]
    }
    
    if email == mock_user["email"] and auth_manager.verify_password(password, mock_user["password_hash"]):
        return {
            "user_id": mock_user["user_id"],
            "email": mock_user["email"],
            "roles": mock_user["roles"]
        }
    
    return None
```

## 7. Monitoring & Logging

### Comprehensive Logging System

```python
# app/core/logging.py
import logging
import sys
from datetime import datetime
from typing import Dict, Any
import json

class CustomFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'execution_time'):
            log_entry['execution_time'] = record.execution_time
        
        return json.dumps(log_entry)

def setup_logging():
    """Setup application logging"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CustomFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(CustomFormatter())
    root_logger.addHandler(file_handler)

class RequestLogger:
    """Request logging utility"""
    
    @staticmethod
    def log_request(request_id: str, method: str, path: str, user_id: str = None):
        """Log incoming request"""
        logger = logging.getLogger(__name__)
        logger.info(
            f"Request received: {method} {path}",
            extra={
                'request_id': request_id,
                'user_id': user_id,
                'method': method,
                'path': path
            }
        )
    
    @staticmethod
    def log_response(request_id: str, status_code: int, execution_time: float, user_id: str = None):
        """Log response"""
        logger = logging.getLogger(__name__)
        logger.info(
            f"Response sent: {status_code}",
            extra={
                'request_id': request_id,
                'user_id': user_id,
                'status_code': status_code,
                'execution_time': execution_time
            }
        )

# Metrics collection
from prometheus_client import Counter, Histogram, Gauge
import time

# Prometheus metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'API request duration', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('api_active_connections', 'Active API connections')
AGENT_PROCESSING_TIME = Histogram('agent_processing_duration_seconds', 'Agent processing time', ['agent_type'])

class MetricsMiddleware:
    """Middleware for collecting metrics"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        ACTIVE_CONNECTIONS.inc()
        
        try:
            await self.app(scope, receive, send)
        finally:
            ACTIVE_CONNECTIONS.dec()
            duration = time.time() - start_time
            
            # Record metrics
            method = scope["method"]
            path = scope["path"]
            
            REQUEST_DURATION.labels(method=method, endpoint=path).observe(duration)
```

## 8. Rate Limiting

### Advanced Rate Limiting

```python
# app/middleware/rate_limit.py
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta
import redis
import hashlib

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        self.rate_limits = {
            'default': {'requests': 100, 'window': 60},  # 100 requests per minute
            'premium': {'requests': 1000, 'window': 60}, # 1000 requests per minute
            'admin': {'requests': 10000, 'window': 60}   # 10000 requests per minute
        }
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier
        client_id = self.get_client_id(request)
        
        # Get user tier (from auth or default)
        user_tier = self.get_user_tier(request)
        
        # Check rate limit
        if not await self.check_rate_limit(client_id, user_tier):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={"Retry-After": "60"}
            )
        
        response = await call_next(request)
        return response
    
    def get_client_id(self, request: Request) -> str:
        """Get client identifier"""
        # Try to get user ID from auth
        auth_header = request.headers.get('Authorization')
        if auth_header:
            # Hash the token for privacy
            token_hash = hashlib.sha256(auth_header.encode()).hexdigest()
            return f"user:{token_hash}"
        
        # Fall back to IP address
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            ip = forwarded_for.split(',')[0].strip()
        else:
            ip = request.client.host
        
        return f"ip:{ip}"
    
    def get_user_tier(self, request: Request) -> str:
        """Get user tier for rate limiting"""
        # In production, this would be determined from user's subscription
        # For demo, we'll use a simple header-based approach
        return request.headers.get('X-User-Tier', 'default')
    
    async def check_rate_limit(self, client_id: str, user_tier: str) -> bool:
        """Check if request is within rate limit"""
        limits = self.rate_limits.get(user_tier, self.rate_limits['default'])
        
        key = f"rate_limit:{client_id}:{user_tier}"
        current_time = int(time.time())
        window_start = current_time - limits['window']
        
        try:
            # Use Redis for distributed rate limiting
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(key, limits['window'])
            
            results = pipe.execute()
            
            current_requests = results[1]
            
            return current_requests < limits['requests']
            
        except Exception as e:
            # If Redis is unavailable, allow the request
            logger.warning(f"Rate limiting error: {e}")
            return True

class APIKeyRateLimiter:
    """API key-based rate limiter"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.api_key_limits = {}  # Load from database
    
    async def check_api_key_limit(self, api_key: str) -> bool:
        """Check rate limit for API key"""
        # Get API key limits from database
        limits = self.get_api_key_limits(api_key)
        
        if not limits:
            return False  # Invalid API key
        
        key = f"api_key_limit:{api_key}"
        current_time = int(time.time())
        window_start = current_time - limits['window']
        
        try:
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.expire(key, limits['window'])
            
            results = pipe.execute()
            current_requests = results[1]
            
            return current_requests < limits['requests']
            
        except Exception as e:
            logger.warning(f"API key rate limiting error: {e}")
            return True
    
    def get_api_key_limits(self, api_key: str) -> Optional[Dict]:
        """Get rate limits for API key"""
        # In production, this would query your database
        # For demo, return default limits
        return {'requests': 1000, 'window': 3600}  # 1000 requests per hour
```

## Production Deployment

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DEBUG=false
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  redis_data:
```

### Health Check Implementation

```python
# app/api/routes/health.py
from fastapi import APIRouter, Depends
from datetime import datetime
import psutil
import asyncio
from typing import Dict, Any

from app.services.agent_manager import agent_manager
from app.models.responses import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint"""
    start_time = datetime.now()
    
    # Check system resources
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Check dependencies
    dependencies = {}
    
    # Check Redis
    dependencies['redis'] = await check_redis_health()
    
    # Check AI agents
    dependencies['agents'] = await check_agents_health()
    
    # Check external APIs
    dependencies['external_apis'] = await check_external_apis_health()
    
    # Calculate uptime
    uptime = (datetime.now() - start_time).total_seconds()
    
    # Determine overall status
    status = "healthy"
    if any(dep_status == "unhealthy" for dep_status in dependencies.values()):
        status = "unhealthy"
    elif any(dep_status == "degraded" for dep_status in dependencies.values()):
        status = "degraded"
    
    return HealthResponse(
        status=status,
        version="1.0.0",
        dependencies=dependencies,
        uptime=uptime,
        system_info={
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent,
            'available_memory': memory.available,
            'total_memory': memory.total
        }
    )

async def check_redis_health() -> str:
    """Check Redis health"""
    try:
        # Implementation depends on your Redis client
        return "healthy"
    except Exception:
        return "unhealthy"

async def check_agents_health() -> str:
    """Check AI agents health"""
    try:
        stats = agent_manager.get_all_stats()
        
        # Check if any agents have high error rates
        for agent_type, agent_stats in stats.items():
            if agent_stats['requests_handled'] > 0:
                error_rate = agent_stats['errors'] / agent_stats['requests_handled']
                if error_rate > 0.1:  # 10% error rate threshold
                    return "degraded"
        
        return "healthy"
    except Exception:
        return "unhealthy"

async def check_external_apis_health() -> str:
    """Check external APIs health"""
    try:
        # Check OpenAI API health
        # Implementation depends on your LLM provider
        return "healthy"
    except Exception:
        return "unhealthy"

@router.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    # Return metrics in Prometheus format
    return "# Metrics endpoint - implement prometheus_client exposition"
```

## Best Practices

### 1. API Design Principles

#### RESTful Design
- **Resource-based URLs**: Use nouns, not verbs
- **HTTP Methods**: Use appropriate HTTP methods (GET, POST, PUT, DELETE)
- **Status Codes**: Return meaningful HTTP status codes
- **Consistent Responses**: Use consistent response formats

#### Versioning
- **URL Versioning**: Include version in URL (e.g., `/api/v1/`)
- **Backward Compatibility**: Maintain compatibility for existing clients
- **Deprecation Strategy**: Plan for version deprecation

### 2. Security Best Practices

#### Authentication & Authorization
- **Strong Authentication**: Use JWT tokens or OAuth 2.0
- **Principle of Least Privilege**: Grant minimal necessary permissions
- **Token Expiration**: Implement reasonable token expiration times
- **Rate Limiting**: Protect against abuse and DDoS attacks

#### Input Validation
- **Strict Validation**: Validate all input data
- **Sanitization**: Sanitize input to prevent injection attacks
- **Length Limits**: Enforce reasonable length limits
- **Type Checking**: Use strong typing with Pydantic models

### 3. Performance Optimization

#### Async Operations
- **Async/Await**: Use async/await for I/O-bound operations
- **Connection Pooling**: Reuse database and HTTP connections
- **Caching**: Cache frequently accessed data
- **Batch Processing**: Process multiple requests efficiently

#### Resource Management
- **Memory Management**: Monitor and optimize memory usage
- **Connection Limits**: Set appropriate connection limits
- **Timeout Configuration**: Configure reasonable timeouts
- **Graceful Degradation**: Handle failures gracefully

### 4. Monitoring & Observability

#### Logging
- **Structured Logging**: Use JSON format for logs
- **Log Levels**: Use appropriate log levels
- **Correlation IDs**: Track requests across services
- **Error Tracking**: Implement comprehensive error tracking

#### Metrics
- **Business Metrics**: Track key business metrics
- **Technical Metrics**: Monitor system performance
- **Custom Metrics**: Add application-specific metrics
- **Alerting**: Set up alerts for critical issues

## Conclusion

Building production-ready APIs for AI agents requires careful consideration of architecture, security, performance, and monitoring. FastAPI provides an excellent foundation for building high-performance, async web services that can scale to handle thousands of concurrent requests.

Key takeaways:

1. **Design for Scale**: Build with scalability in mind from the start
2. **Security First**: Implement comprehensive security measures
3. **Monitor Everything**: Use comprehensive monitoring and logging
4. **Handle Failures Gracefully**: Implement robust error handling
5. **Document Thoroughly**: Maintain good API documentation

Remember that deployment is just the beginning. Continuous monitoring, optimization, and improvement are essential for maintaining a successful production API.

## Next Steps

1. Set up basic FastAPI application with health checks
2. Implement authentication and authorization
3. Add comprehensive error handling and logging
4. Deploy with Docker and implement monitoring
5. Add rate limiting and security measures
6. Implement CI/CD pipeline for automated deployments

---

*This lesson provides the foundation for deploying AI agents as production-ready APIs. In the next lesson, we'll explore advanced deployment strategies and DevOps practices.*
