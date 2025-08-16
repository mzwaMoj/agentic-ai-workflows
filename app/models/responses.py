"""
Response models for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


class Text2SQLResponse(BaseModel):
    """Response model for text-to-SQL generation."""
    
    success: bool = Field(..., description="Whether the request was successful", example=True)
    response: str = Field(..., description="Natural language response to the user", example="The client with the highest account balance is Charles Cline, with a balance of $49,859.96.")
    sql_query: Optional[str] = Field(default=None, description="Generated SQL query", example="SELECT TOP 1 full_name, balance FROM customer_information ORDER BY balance DESC")
    sql_results: Optional[List[Dict[str, Any]]] = Field(default=None, description="SQL execution results", example=[{"full_name": "Charles Cline", "balance": 49859.96}])
    chart_html: Optional[str] = Field(default=None, description="Generated chart HTML", example="<div id='chart'>...</div>")
    execution_time: Optional[float] = Field(default=None, description="Query execution time in seconds", example=1.234)
    chat_history: Optional[List[Dict[str, Any]]] = Field(default=None, description="Updated chat history", example=[{"role": "user", "content": "Which client has the highest balance?"}, {"role": "assistant", "content": "Charles Cline has the highest balance..."}])
    error: Optional[str] = Field(default=None, description="Error message if failed", example=None)
    routing_info: Optional[Dict[str, Any]] = Field(default=None, description="Query routing information", example={"requires_sql": True, "requires_chart": False})

    class Config:
        schema_extra = {
            "examples": [
                {
                    "summary": "Successful Query Response",
                    "description": "Example of a successful text-to-SQL response",
                    "value": {
                        "success": True,
                        "response": "The client with the highest account balance is Charles Cline, with a balance of $49,859.96.",
                        "sql_query": "SELECT TOP 1 full_name, balance FROM customer_information ORDER BY balance DESC",
                        "sql_results": [{"full_name": "Charles Cline", "balance": 49859.96}],
                        "chart_html": None,
                        "execution_time": 1.234,
                        "chat_history": [
                            {"role": "user", "content": "Which client has the highest account balance?"},
                            {"role": "assistant", "content": "The client with the highest account balance is Charles Cline, with a balance of $49,859.96."}
                        ],
                        "error": None,
                        "routing_info": {"requires_sql": True, "requires_chart": False}
                    }
                },
                {
                    "summary": "Response with Chart",
                    "description": "Example response that includes a generated chart",
                    "value": {
                        "success": True,
                        "response": "Here's the quarterly transaction volume analysis. Q4 2024 had the highest volume with 244 transactions.",
                        "sql_query": "SELECT DATEPART(quarter, transaction_date) as quarter, COUNT(*) as transaction_count FROM transaction_history GROUP BY DATEPART(quarter, transaction_date)",
                        "sql_results": [{"quarter": 1, "transaction_count": 156}, {"quarter": 2, "transaction_count": 178}, {"quarter": 3, "transaction_count": 198}, {"quarter": 4, "transaction_count": 244}],
                        "chart_html": "<div id='chart'><script>/* Chart code */</script></div>",
                        "execution_time": 2.1,
                        "chat_history": [],
                        "error": None,
                        "routing_info": {"requires_sql": True, "requires_chart": True}
                    }
                }
            ]
        }


class SQLExecuteResponse(BaseModel):
    """Response model for SQL execution."""
    
    success: bool = Field(..., description="Whether the execution was successful")
    results: Optional[List[Dict[str, Any]]] = Field(default=None, description="Query results")
    row_count: Optional[int] = Field(default=None, description="Number of rows returned")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    sql_query: str = Field(..., description="The SQL query that was executed")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    validation_only: bool = Field(default=False, description="Whether this was validation only")


class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Assistant's response message")
    chat_history: List[Dict[str, Any]] = Field(..., description="Updated chat history")
    sql_results: Optional[List[Dict[str, Any]]] = Field(default=None, description="SQL results if applicable")
    chart_html: Optional[str] = Field(default=None, description="Chart HTML if generated")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    response_type: str = Field(default="text", description="Type of response (text, sql, chart, etc.)")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class HealthCheckResponse(BaseModel):
    """Response model for health checks."""
    
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    services: Optional[Dict[str, Any]] = Field(default=None, description="Individual service health status")
    version: str = Field(default="1.0.0", description="Application version")
    uptime: Optional[str] = Field(default=None, description="Application uptime")


class QueryValidationResponse(BaseModel):
    """Response model for query validation."""
    
    is_valid: bool = Field(..., description="Whether the query is valid")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    query_type: Optional[str] = Field(default=None, description="Detected query type")
    error: Optional[str] = Field(default=None, description="Validation error if failed")


class TableInfoResponse(BaseModel):
    """Response model for table information."""
    
    success: bool = Field(..., description="Whether the request was successful")
    tables: List[Dict[str, Any]] = Field(default_factory=list, description="Table information")
    total_tables: int = Field(default=0, description="Total number of tables")
    collection_status: Optional[str] = Field(default=None, description="Vector collection status")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class ChartGenerationResponse(BaseModel):
    """Response model for chart generation."""
    
    success: bool = Field(..., description="Whether chart generation was successful")
    chart_html: Optional[str] = Field(default=None, description="Generated chart HTML")
    chart_type: Optional[str] = Field(default=None, description="Type of chart generated")
    data_analysis: Optional[Dict[str, Any]] = Field(default=None, description="Data analysis results")
    suggestions: Optional[str] = Field(default=None, description="Visualization suggestions")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    success: bool = Field(default=False, description="Always false for error responses")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(default=None, description="Error code for categorization")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


class StatusResponse(BaseModel):
    """General status response model."""
    
    status: str = Field(..., description="Status message")
    message: Optional[str] = Field(default=None, description="Additional status information")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Additional data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


# Union type for flexible response handling
APIResponse = Union[
    Text2SQLResponse,
    SQLExecuteResponse, 
    ChatResponse,
    HealthCheckResponse,
    QueryValidationResponse,
    TableInfoResponse,
    ChartGenerationResponse,
    ErrorResponse,
    StatusResponse
]
