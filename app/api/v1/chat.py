"""
Chat endpoints for conversational Text2SQL interactions.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
import uuid

from app.models import (
    ChatRequest,
    ChatResponse,
    ChatState,
    ChatSession,
    MessageRole,
    ErrorResponse
)
from app.core import Text2SQLEngine
from app.services import get_services

logger = logging.getLogger(__name__)
router = APIRouter()


# In-memory session storage (in production, use Redis or database)
chat_sessions: Dict[str, ChatState] = {}


async def get_text2sql_engine(services: Dict[str, Any] = Depends(get_services)) -> Text2SQLEngine:
    """Dependency to get Text2SQL engine instance."""
    return Text2SQLEngine(services)


def get_or_create_session(session_id: Optional[str] = None) -> ChatState:
    """Get existing chat session or create a new one."""
    if session_id and session_id in chat_sessions:
        return chat_sessions[session_id]
    else:
        # Create new session
        new_session_id = session_id or str(uuid.uuid4())
        chat_session = ChatSession(session_id=new_session_id)
        chat_state = ChatState(session=chat_session)
        chat_sessions[new_session_id] = chat_state
        return chat_state


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    engine: Text2SQLEngine = Depends(get_text2sql_engine)
):
    """
    Send a message in a conversational Text2SQL session.
    
    This endpoint maintains conversation context and provides 
    natural language interactions with the database.
    """
    try:
        # Get or create chat session
        chat_state = get_or_create_session(request.session_id)
        
        # Add user message to session
        chat_state.add_user_message(request.message)
        
        # Get formatted chat history for the engine
        chat_history = chat_state.get_formatted_history()
        
        # Process the message through the Text2SQL engine
        result = await engine.process_query(
            user_input=request.message,
            chat_history=chat_history[:-1]  # Exclude the current message as it's added by engine
        )
        
        if result["success"]:
            response_content = result["response"]
            
            # Add assistant response to session
            assistant_content = {"text": response_content}
            if result.get("chart_html"):
                assistant_content["chart_html"] = result["chart_html"]
                
            chat_state.add_assistant_message(assistant_content)
            
            # Update context with query results
            if result.get("sql_results"):
                chat_state.context.update_context(
                    last_results=result["sql_results"],
                    last_sql_query=result.get("sql_results", [{}])[0].get("query_info")
                )
            
            # Determine response type
            response_type = "text"
            if result.get("sql_results"):
                response_type = "sql"
            if result.get("chart_html"):
                response_type = "chart"
            
            return ChatResponse(
                success=True,
                message=response_content,
                chat_history=chat_state.get_formatted_history(),
                sql_results=result.get("sql_results"),
                chart_html=result.get("chart_html"),
                session_id=chat_state.session.session_id,
                response_type=response_type
            )
        else:
            # Handle error response
            error_message = result.get("error", "I encountered an error processing your message.")
            chat_state.add_assistant_message(error_message)
            
            return ChatResponse(
                success=False,
                message=error_message,
                chat_history=chat_state.get_formatted_history(),
                session_id=chat_state.session.session_id,
                error=result.get("error")
            )
            
    except Exception as e:
        logger.error(f"Chat message processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing error: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=ChatResponse)
async def get_session(session_id: str):
    """
    Get chat session history.
    
    Retrieve the complete conversation history for a session.
    """
    try:
        if session_id not in chat_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found"
            )
        
        chat_state = chat_sessions[session_id]
        
        return ChatResponse(
            success=True,
            message="Session retrieved successfully",
            chat_history=chat_state.get_formatted_history(),
            session_id=session_id,
            response_type="session_info"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session retrieval error: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """
    Clear a chat session.
    
    Remove all messages from the specified session.
    """
    try:
        if session_id not in chat_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found"
            )
        
        chat_state = chat_sessions[session_id]
        chat_state.session.clear_history()
        
        return {
            "success": True,
            "message": f"Session '{session_id}' cleared successfully",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session clearing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session clearing error: {str(e)}"
        )


@router.get("/sessions")
async def list_sessions():
    """
    List all active chat sessions.
    
    Get a summary of all currently active chat sessions.
    """
    try:
        session_summaries = []
        
        for session_id, chat_state in chat_sessions.items():
            summary = {
                "session_id": session_id,
                "message_count": len(chat_state.session.messages),
                "created_at": chat_state.session.created_at,
                "updated_at": chat_state.session.updated_at,
                "current_topic": chat_state.context.current_topic
            }
            session_summaries.append(summary)
        
        return {
            "success": True,
            "sessions": session_summaries,
            "total_sessions": len(session_summaries)
        }
        
    except Exception as e:
        logger.error(f"Session listing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session listing error: {str(e)}"
        )


@router.post("/sessions/{session_id}/context")
async def update_session_context(
    session_id: str,
    context_updates: Dict[str, Any]
):
    """
    Update session context information.
    
    Manually update conversation context for better continuity.
    """
    try:
        if session_id not in chat_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found"
            )
        
        chat_state = chat_sessions[session_id]
        chat_state.context.update_context(**context_updates)
        
        return {
            "success": True,
            "message": "Session context updated successfully",
            "session_id": session_id,
            "updated_fields": list(context_updates.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Context update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Context update error: {str(e)}"
        )
