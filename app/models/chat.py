"""
Chat-specific models for conversation handling.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Enumeration for message roles in chat."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Individual chat message model."""
    
    role: MessageRole = Field(..., description="Role of the message sender")
    content: Union[str, Dict[str, Any]] = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional message metadata")
    
    @validator('content')
    def validate_content(cls, v):
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Message content cannot be empty")
        elif isinstance(v, dict):
            if not v:
                raise ValueError("Message content dictionary cannot be empty")
        return v


class ChatSession(BaseModel):
    """Chat session model for managing conversation state."""
    
    session_id: str = Field(..., description="Unique session identifier")
    messages: List[ChatMessage] = Field(default_factory=list, description="Chat messages")
    created_at: datetime = Field(default_factory=datetime.now, description="Session creation time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Session metadata")
    
    def add_message(self, role: MessageRole, content: Union[str, Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None):
        """Add a new message to the session."""
        message = ChatMessage(
            role=role,
            content=content,
            metadata=metadata
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        
    def get_recent_messages(self, count: int = 10) -> List[ChatMessage]:
        """Get the most recent messages."""
        return self.messages[-count:] if len(self.messages) > count else self.messages
        
    def clear_history(self):
        """Clear all messages from the session."""
        self.messages = []
        self.updated_at = datetime.now()


class ConversationContext(BaseModel):
    """Context information for maintaining conversation state."""
    
    current_topic: Optional[str] = Field(default=None, description="Current conversation topic")
    last_sql_query: Optional[str] = Field(default=None, description="Last generated SQL query")
    last_results: Optional[List[Dict[str, Any]]] = Field(default=None, description="Last query results")
    active_tables: List[str] = Field(default_factory=list, description="Tables currently being discussed")
    chart_preferences: Optional[Dict[str, Any]] = Field(default=None, description="User's chart preferences")
    query_history: List[str] = Field(default_factory=list, description="History of user queries")
    
    def update_context(self, **kwargs):
        """Update context with new information."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class ChatState(BaseModel):
    """Overall chat state including session and context."""
    
    session: ChatSession = Field(..., description="Chat session information")
    context: ConversationContext = Field(default_factory=ConversationContext, description="Conversation context")
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="User preferences")
    
    def get_formatted_history(self) -> List[Dict[str, str]]:
        """Get chat history in format expected by OpenAI API."""
        formatted = []
        for message in self.session.messages:
            formatted.append({
                "role": message.role.value,
                "content": str(message.content) if isinstance(message.content, dict) else message.content
            })
        return formatted
        
    def add_user_message(self, content: str):
        """Add a user message to the session."""
        self.session.add_message(MessageRole.USER, content)
        self.context.query_history.append(content)
        
    def add_assistant_message(self, content: Union[str, Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None):
        """Add an assistant message to the session."""
        self.session.add_message(MessageRole.ASSISTANT, content, metadata)


class StreamingChatResponse(BaseModel):
    """Response model for streaming chat responses."""
    
    delta: str = Field(..., description="Incremental response content")
    is_complete: bool = Field(default=False, description="Whether the response is complete")
    session_id: str = Field(..., description="Session identifier")
    message_id: Optional[str] = Field(default=None, description="Message identifier")


class ChatAnalytics(BaseModel):
    """Analytics model for chat sessions."""
    
    session_id: str = Field(..., description="Session identifier")
    total_messages: int = Field(default=0, description="Total number of messages")
    sql_queries_generated: int = Field(default=0, description="Number of SQL queries generated")
    charts_created: int = Field(default=0, description="Number of charts created")
    errors_encountered: int = Field(default=0, description="Number of errors encountered")
    average_response_time: Optional[float] = Field(default=None, description="Average response time")
    session_duration: Optional[float] = Field(default=None, description="Session duration in seconds")
    most_used_tables: List[str] = Field(default_factory=list, description="Most frequently used tables")
    
    def calculate_session_duration(self, session: ChatSession) -> float:
        """Calculate session duration based on message timestamps."""
        if len(session.messages) < 2:
            return 0.0
            
        start_time = session.messages[0].timestamp
        end_time = session.messages[-1].timestamp
        duration = (end_time - start_time).total_seconds()
        
        self.session_duration = duration
        return duration
