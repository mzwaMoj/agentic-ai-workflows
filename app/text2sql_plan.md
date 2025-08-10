
# Detailed Text2SQL Application Plan

Based on the analysis of your codebase, project plan, and the existing chatbot.py functionality, here's a comprehensive plan to create a modular, FastAPI-based text2sql application following the project guidelines:

## 1. **Current State Analysis**

**Existing Strengths:**
- ✅ Working chatbot functionality with agent routing
- ✅ SQL generation and execution capabilities
- ✅ Chart generation with Plotly
- ✅ Vector database (ChromaDB) for table metadata
- ✅ MLflow logging integration
- ✅ Comprehensive database connection management
- ✅ Multi-intent query processing
- ✅ Modular prompt management

**Areas to Modularize:**
- ❌ All functionality is in chatbot.py (notebook-style)
- ❌ No FastAPI structure
- ❌ No proper service separation
- ❌ No API endpoints
- ❌ Missing configuration management
- ❌ No structured response models

## 2. **Architecture Design**

### **Core Application Structure**
```
app/
├── main.py                 # FastAPI application entry
├── config/
│   ├── __init__.py
│   ├── settings.py         # Centralized configuration
│   └── database.py         # Database configuration
├── core/
│   ├── __init__.py
│   ├── text2sql_engine.py  # Main business logic
│   ├── table_retriever.py  # Table metadata management
│   └── chart_generator.py  # Chart generation logic
├── services/
│   ├── __init__.py
│   ├── openai_service.py   # Azure OpenAI integration
│   ├── database_service.py # SQL execution service
│   ├── vector_service.py   # ChromaDB vector operations
│   └── logging_service.py  # MLflow logging service
├── api/
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── text2sql.py     # Text2SQL endpoints
│   │   ├── chat.py         # Chat endpoints
│   │   └── health.py       # Health check endpoints
├── models/
│   ├── __init__.py
│   ├── requests.py         # Request schemas
│   ├── responses.py        # Response schemas
│   └── chat.py            # Chat-specific models
├── agents/
│   ├── __init__.py
│   ├── router_agent.py     # Query routing logic
│   ├── sql_agent.py        # SQL generation logic
│   ├── chart_agent.py      # Chart generation logic
│   └── final_agent.py      # Final response formatting
└── utils/
    ├── __init__.py
    ├── validators.py       # Input validation
    ├── formatters.py       # Output formatting
    └── exceptions.py       # Custom exceptions
```

## 3. **Implementation Plan**

### **Phase 1: Configuration & Infrastructure (Priority 1)**

**1.1 Enhanced Configuration Management**
```python
# app/config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    app_name: str = "Text2SQL API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_key: str
    azure_openai_deployment: str
    azure_openai_version: str = "2024-02-15-preview"
    
    # Database
    db_server: str
    db_database: str = "master"
    db_auth_type: str = "windows"
    db_username: Optional[str] = None
    db_password: Optional[str] = None
    
    # Vector Database
    vector_db_path: str = "./index/chroma_db"
    
    # API Configuration
    cors_origins: list = ["*"]
    api_prefix: str = "/api/v1"
    
    class Config:
        env_file = ".env"
```

**1.2 Database Service Setup**
```python
# app/services/database_service.py
from app.config.settings import Settings
from app.db.sql_connector import connect_to_sql_server
from app.db.sql_query_executor import execute_multiple_sql_code
import logging

class DatabaseService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.connection = None
        self.cursor = None
        
    async def connect(self):
        # Implementation from existing sql_connector
        
    async def execute_sql(self, sql_query: str):
        # Implementation from existing sql_query_executor
        
    async def close(self):
        # Cleanup connections
```

### **Phase 2: Core Business Logic (Priority 1)**

**2.1 Text2SQL Engine**
```python
# app/core/text2sql_engine.py
from typing import List, Dict, Any, Optional
from app.agents.router_agent import RouterAgent
from app.agents.sql_agent import SQLAgent
from app.agents.chart_agent import ChartAgent
from app.core.table_retriever import TableRetriever

class Text2SQLEngine:
    def __init__(self, services: Dict[str, Any]):
        self.router_agent = RouterAgent(services['openai'])
        self.sql_agent = SQLAgent(services['openai'])
        self.chart_agent = ChartAgent(services['openai'])
        self.table_retriever = TableRetriever(services['vector'])
        self.db_service = services['database']
        self.logger = services['logging']
        
    async def process_query(self, user_input: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """Main processing pipeline"""
        try:
            # 1. Route the query
            route_response = await self.router_agent.route_query(user_input, chat_history)
            
            # 2. Handle SQL analysis
            if route_response.requires_sql:
                sql_results, chart_html = await self._handle_sql_analysis(user_input)
                
                # 3. Generate final response
                final_response = await self._generate_final_response(
                    user_input, sql_results, chart_html
                )
                
                return {
                    "success": True,
                    "response": final_response,
                    "sql_results": sql_results,
                    "chart_html": chart_html,
                    "chat_history": chat_history + [{"role": "assistant", "content": final_response}]
                }
            else:
                # Handle general queries
                return await self._handle_general_query(user_input, chat_history)
                
        except Exception as e:
            self.logger.log_error(f"Text2SQL Engine Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error processing your request. Please try again."
            }
    
    async def _handle_sql_analysis(self, user_input: str) -> tuple:
        # Implementation from existing handle_sql_analysis function
        
    async def _generate_final_response(self, user_input: str, sql_results: List, chart_html: str) -> str:
        # Implementation from existing polish prompt logic
```

**2.2 Agent Modularization**
```python
# app/agents/router_agent.py
class RouterAgent:
    def __init__(self, openai_service):
        self.openai_service = openai_service
        
    async def route_query(self, user_input: str, chat_history: List[Dict] = None):
        # Implementation from existing routing_agent function
        
# app/agents/sql_agent.py  
class SQLAgent:
    def __init__(self, openai_service):
        self.openai_service = openai_service
        
    async def generate_sql(self, user_query: str, required_tables: str) -> str:
        # Implementation from existing agent_sql_analysis function

# app/agents/chart_agent.py
class ChartAgent:
    def __init__(self, openai_service):
        self.openai_service = openai_service
        
    async def generate_chart(self, user_query: str, data: str) -> str:
        # Implementation from existing agent_generate_charts function
```

### **Phase 3: API Layer (Priority 1)**

**3.1 FastAPI Application Setup**
```python
# app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import Settings
from app.api.v1 import text2sql, chat, health
from app.services import get_services

def create_app() -> FastAPI:
    settings = Settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router, prefix=f"{settings.api_prefix}/health", tags=["Health"])
    app.include_router(text2sql.router, prefix=f"{settings.api_prefix}/text2sql", tags=["Text2SQL"])
    app.include_router(chat.router, prefix=f"{settings.api_prefix}/chat", tags=["Chat"])
    
    return app

app = create_app()
```

**3.2 API Endpoints**
```python
# app/api/v1/text2sql.py
from fastapi import APIRouter, Depends, HTTPException
from app.models.requests import Text2SQLRequest, SQLExecuteRequest
from app.models.responses import Text2SQLResponse, SQLExecuteResponse
from app.core.text2sql_engine import Text2SQLEngine

router = APIRouter()

@router.post("/generate", response_model=Text2SQLResponse)
async def generate_sql(
    request: Text2SQLRequest,
    engine: Text2SQLEngine = Depends(get_text2sql_engine)
):
    """Generate SQL from natural language query."""
    try:
        result = await engine.process_query(request.query, request.chat_history)
        return Text2SQLResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute", response_model=SQLExecuteResponse)
async def execute_sql(
    request: SQLExecuteRequest,
    engine: Text2SQLEngine = Depends(get_text2sql_engine)
):
    """Execute validated SQL query."""
    # Implementation for direct SQL execution
    
@router.post("/explain")
async def explain_sql(sql_query: str):
    """Explain SQL query in natural language."""
    # Implementation for SQL explanation

# app/api/v1/chat.py
router = APIRouter()

@router.post("/completions")
async def chat_completions(
    request: ChatRequest,
    engine: Text2SQLEngine = Depends(get_text2sql_engine)
):
    """Chat interface for conversational SQL generation."""
    # Implementation for chat-style interactions
```

**3.3 Request/Response Models**
```python
# app/models/requests.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Text2SQLRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    chat_history: Optional[List[Dict[str, str]]] = Field(default=[], description="Chat history")
    include_charts: bool = Field(default=True, description="Generate charts if applicable")
    max_results: int = Field(default=100, le=1000, description="Maximum result rows")

class SQLExecuteRequest(BaseModel):
    sql_query: str = Field(..., description="SQL query to execute")
    validate_only: bool = Field(default=False, description="Only validate, don't execute")

# app/models/responses.py
class Text2SQLResponse(BaseModel):
    success: bool
    response: str
    sql_query: Optional[str] = None
    sql_results: Optional[List[Dict[str, Any]]] = None
    chart_html: Optional[str] = None
    chat_history: List[Dict[str, str]]
    execution_time: float
    
class SQLExecuteResponse(BaseModel):
    success: bool
    results: Optional[List[Dict[str, Any]]] = None
    row_count: int = 0
    columns: List[str] = []
    execution_time: float
    error: Optional[str] = None
```

### **Phase 4: Service Layer (Priority 2)**

**4.1 Service Dependencies**
```python
# app/services/__init__.py
from app.services.openai_service import OpenAIService
from app.services.database_service import DatabaseService
from app.services.vector_service import VectorService
from app.services.logging_service import LoggingService

async def get_services():
    """Dependency injection for services"""
    settings = Settings()
    
    return {
        'openai': OpenAIService(settings),
        'database': DatabaseService(settings),
        'vector': VectorService(settings),
        'logging': LoggingService(settings)
    }

async def get_text2sql_engine(services = Depends(get_services)):
    return Text2SQLEngine(services)
```

### **Phase 5: Integration & Testing (Priority 2)**

**5.1 Health Checks**
```python
# app/api/v1/health.py
@router.get("/")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@router.get("/detailed")
async def detailed_health_check(services = Depends(get_services)):
    """Comprehensive health check for all services"""
    health_status = {
        "database": await services['database'].health_check(),
        "openai": await services['openai'].health_check(),
        "vector_db": await services['vector'].health_check(),
    }
    return health_status
```

**5.2 Error Handling**
```python
# app/utils/exceptions.py
class Text2SQLException(Exception):
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class SQLValidationError(Text2SQLException):
    pass

class DatabaseConnectionError(Text2SQLException):
    pass
```

## 4. **Migration Strategy from chatbot.py**

### **Step 1: Extract Core Functions**
- Move `agent_table_retriever` → `app/core/table_retriever.py`
- Move `handle_sql_analysis` → `app/core/text2sql_engine.py`
- Move agent functions → `app/agents/`
- Move prompt functions → prompts (keep existing structure)

### **Step 2: Preserve Existing Logic**
- Keep the exact same LLM prompts and agent logic
- Maintain the ChromaDB vector search functionality
- Preserve the MLflow logging structure
- Keep the chart generation capabilities

### **Step 3: Add API Layer**
- Wrap existing functionality in FastAPI endpoints
- Add request/response validation
- Implement proper error handling
- Add authentication if needed later

## 5. **Deployment Configuration**

### **5.1 Docker Support**
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY .env .env

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **5.2 Requirements Management**
```txt
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
# ... existing dependencies from current project
```

## 6. **React Integration Ready**

### **6.1 API Endpoints for Frontend**
```javascript
// React integration examples
const apiClient = {
  generateSQL: async (query) => {
    return fetch('/api/v1/text2sql/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, include_charts: true })
    });
  },
  
  chatCompletion: async (messages) => {
    return fetch('/api/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages })
    });
  }
};
```

## 7. **Implementation Priority**

1. **Week 1:** Configuration, core services, and basic API structure
2. **Week 2:** Migrate chatbot.py logic to modular services
3. **Week 3:** API endpoints, request/response models, error handling
4. **Week 4:** Testing, documentation, and React integration preparation

## 8. **Key Benefits of This Approach**

- ✅ **Preserves existing functionality** - No loss of current capabilities
- ✅ **API-ready** - Can be integrated with React immediately
- ✅ **Modular design** - Easy to maintain and extend
- ✅ **Production-ready** - Proper error handling, logging, health checks
- ✅ **Scalable** - Can be deployed in containers, scaled horizontally
- ✅ **Testable** - Clear separation of concerns enables unit testing

This plan maintains the complexity and sophistication of your current text2sql functionality while making it production-ready and React-integrable. Would you like me to proceed with implementing this plan, starting with Phase 1?