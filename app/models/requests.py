"""
Request models for API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any


class Text2SQLRequest(BaseModel):
    """Request model for text-to-SQL generation."""
    
    query: str = Field(
        ..., 
        description="Natural language query to convert to SQL", 
        min_length=1, 
        max_length=1000,
        example="Which client has the highest account balance?"
    )
    include_charts: bool = Field(
        default=True, 
        description="Whether to generate charts if applicable",
        example=True
    )
    max_results: int = Field(
        default=100, 
        ge=1, 
        le=1000, 
        description="Maximum number of result rows",
        example=100
    )
    chat_history: Optional[List[Dict[str, str]]] = Field(
        default=None, 
        description="Optional chat history for context",
        example=[
            {"role": "user", "content": "Show me customer data"},
            {"role": "assistant", "content": "Here are the customers..."}
        ]
    )
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty or whitespace only")
        return v.strip()

    class Config:
        schema_extra = {
            "examples": [
                {
                    "summary": "Customer Balance Query",
                    "description": "Find the client with the highest account balance",
                    "value": {
                        "query": "Which client has the highest account balance?",
                        "include_charts": False,
                        "max_results": 10,
                        "chat_history": []
                    }
                },
                {
                    "summary": "Transaction Volume Query",
                    "description": "Find quarterly transaction volumes",
                    "value": {
                        "query": "Which quarter has the highest transaction volume?",
                        "include_charts": True,
                        "max_results": 50,
                        "chat_history": []
                    }
                },
                {
                    "summary": "Account Status Query", 
                    "description": "Count closed accounts",
                    "value": {
                        "query": "How many closed accounts are there?",
                        "include_charts": False,
                        "max_results": 100,
                        "chat_history": []
                    }
                },
                {
                    "summary": "Customer Demographics",
                    "description": "Analyze customer demographics with chart generation",
                    "value": {
                        "query": "Show me customer demographics by age group",
                        "include_charts": True,
                        "max_results": 200,
                        "chat_history": []
                    }
                }
            ]
        }


class SQLExecuteRequest(BaseModel):
    """Request model for direct SQL execution."""
    
    sql_query: str = Field(
        ..., 
        description="SQL query to execute", 
        min_length=1,
        example="SELECT TOP 10 full_name, balance FROM customer_information ORDER BY balance DESC"
    )
    validate_only: bool = Field(
        default=False, 
        description="Only validate syntax, don't execute",
        example=False
    )
    max_results: int = Field(
        default=100, 
        ge=1, 
        le=1000, 
        description="Maximum number of result rows",
        example=100
    )
    
    @validator('sql_query')
    def validate_sql(cls, v):
        if not v.strip():
            raise ValueError("SQL query cannot be empty")
        return v.strip()

    class Config:
        schema_extra = {
            "examples": [
                {
                    "summary": "Top Customers by Balance",
                    "description": "Execute SQL to find customers with highest balances",
                    "value": {
                        "sql_query": "SELECT TOP 10 full_name, balance FROM customer_information ORDER BY balance DESC",
                        "validate_only": False,
                        "max_results": 10
                    }
                },
                {
                    "summary": "Validate SQL Only",
                    "description": "Just validate SQL syntax without executing",
                    "value": {
                        "sql_query": "SELECT COUNT(*) FROM customer_information WHERE status = 'closed'",
                        "validate_only": True,
                        "max_results": 1
                    }
                },
                {
                    "summary": "Transaction Summary",
                    "description": "Get transaction summary by quarter",
                    "value": {
                        "sql_query": "SELECT DATEPART(quarter, transaction_date) as quarter, COUNT(*) as transaction_count FROM transaction_history GROUP BY DATEPART(quarter, transaction_date) ORDER BY quarter",
                        "validate_only": False,
                        "max_results": 4
                    }
                }
            ]
        }


class ChatRequest(BaseModel):
    """Request model for chat-based interactions."""
    
    message: str = Field(
        ..., 
        description="User message", 
        min_length=1, 
        max_length=2000,
        example="Can you help me analyze our customer data?"
    )
    chat_history: Optional[List[Dict[str, Any]]] = Field(
        default=None, 
        description="Chat conversation history",
        example=[
            {"role": "user", "content": "Show me customer balance data"},
            {"role": "assistant", "content": "Here's the customer balance information..."}
        ]
    )
    include_charts: bool = Field(
        default=True, 
        description="Whether to generate charts if applicable",
        example=True
    )
    session_id: Optional[str] = Field(
        default=None, 
        description="Optional session identifier",
        example="session_123456"
    )
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()

    class Config:
        schema_extra = {
            "examples": [
                {
                    "summary": "New Conversation",
                    "description": "Start a new chat conversation",
                    "value": {
                        "message": "Can you help me analyze our customer data?",
                        "chat_history": [],
                        "include_charts": True,
                        "session_id": None
                    }
                },
                {
                    "summary": "Follow-up Question",
                    "description": "Continue an existing conversation",
                    "value": {
                        "message": "Can you show me that data in a chart?",
                        "chat_history": [
                            {"role": "user", "content": "Which customers have the highest balances?"},
                            {"role": "assistant", "content": "Here are the top customers by balance: Charles Cline ($49,859.96)..."}
                        ],
                        "include_charts": True,
                        "session_id": "session_123"
                    }
                },
                {
                    "summary": "Data Analysis Request",
                    "description": "Request complex data analysis",
                    "value": {
                        "message": "What trends do you see in our transaction data over the past year?",
                        "chat_history": [],
                        "include_charts": True,
                        "session_id": "analysis_session_001"
                    }
                }
            ]
        }


class QueryValidationRequest(BaseModel):
    """Request model for query validation."""
    
    query: str = Field(..., description="Query to validate", min_length=1)
    query_type: str = Field(default="auto", description="Type of query (sql, natural_language, auto)")
    
    @validator('query_type')
    def validate_query_type(cls, v):
        valid_types = ["sql", "natural_language", "auto"]
        if v not in valid_types:
            raise ValueError(f"Query type must be one of: {valid_types}")
        return v


class HealthCheckRequest(BaseModel):
    """Request model for health check (typically empty)."""
    
    detailed: bool = Field(default=False, description="Whether to return detailed health information")
    check_services: Optional[List[str]] = Field(default=None, description="Specific services to check")


class TableInfoRequest(BaseModel):
    """Request model for table information."""
    
    table_name: Optional[str] = Field(default=None, description="Specific table name to get info for")
    include_schema: bool = Field(default=True, description="Whether to include schema information")


class ChartGenerationRequest(BaseModel):
    """Request model for standalone chart generation."""
    
    data: Any = Field(..., description="Data to visualize")
    chart_type: str = Field(default="auto", description="Type of chart to generate")
    title: Optional[str] = Field(default=None, description="Chart title")
    user_request: Optional[str] = Field(default=None, description="Natural language description of desired chart")
    
    @validator('chart_type')
    def validate_chart_type(cls, v):
        valid_types = ["auto", "bar", "line", "pie", "scatter", "histogram", "table"]
        if v not in valid_types:
            raise ValueError(f"Chart type must be one of: {valid_types}")
        return v
