"""
Models package initialization.
"""

from .requests import (
    Text2SQLRequest,
    SQLExecuteRequest,
    ChatRequest,
    QueryValidationRequest,
    HealthCheckRequest,
    TableInfoRequest,
    ChartGenerationRequest
)

from .responses import (
    Text2SQLResponse,
    SQLExecuteResponse,
    ChatResponse,
    HealthCheckResponse,
    QueryValidationResponse,
    TableInfoResponse,
    ChartGenerationResponse,
    ErrorResponse,
    StatusResponse,
    APIResponse
)

from .chat import (
    MessageRole,
    ChatMessage,
    ChatSession,
    ConversationContext,
    ChatState,
    StreamingChatResponse,
    ChatAnalytics
)

__all__ = [
    # Request models
    "Text2SQLRequest",
    "SQLExecuteRequest", 
    "ChatRequest",
    "QueryValidationRequest",
    "HealthCheckRequest",
    "TableInfoRequest",
    "ChartGenerationRequest",
    
    # Response models
    "Text2SQLResponse",
    "SQLExecuteResponse",
    "ChatResponse",
    "HealthCheckResponse",
    "QueryValidationResponse",
    "TableInfoResponse",
    "ChartGenerationResponse",
    "ErrorResponse",
    "StatusResponse",
    "APIResponse",
    
    # Chat models
    "MessageRole",
    "ChatMessage",
    "ChatSession",
    "ConversationContext",
    "ChatState",
    "StreamingChatResponse",
    "ChatAnalytics"
]
