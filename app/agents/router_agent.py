"""
Router agent for determining query intent and routing to appropriate handlers.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class RouterAgent:
    """Agent responsible for routing user queries to appropriate handlers."""
    
    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service
        
    async def route_query(self, user_input: str, chat_history: Optional[List[Dict]] = None) -> Any:
        """
        Route user query to determine the appropriate handling.
        
        Args:
            user_input: User's natural language query
            chat_history: Optional chat history for context
              Returns:
            OpenAI response with routing decision
        """
        try:
            # Import prompts and tools from app modules
            from app.prompts import prompt_agent_router
            from app.tools import tools_definitions
            
            # Prepare messages
            messages = []
            
            # Add chat history if provided
            if chat_history:
                messages.extend(chat_history)
                
            # Add the current user query with routing prompt
            messages.append({
                "role": "user", 
                "content": f"{prompt_agent_router}\n\nUser Query: {user_input}"
            })
            
            # Call OpenAI with tools
            response = await self.openai_service.chat_completion(
                messages=messages,
                tools=tools_definitions,
                temperature=0.0
            )
            
            logger.info(f"Router agent processed query: {user_input[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Router agent failed: {e}")
            raise
    def extract_routing_decision(self, response: Any) -> Dict[str, Any]:
        """
        Extract routing decision from OpenAI response.
        
        Args:
            response: OpenAI chat completion response
            
        Returns:
            Dictionary with routing information
        """
        try:
            message = response.choices[0].message
            
            routing_info = {
                "requires_sql": False,
                "requires_chart": False,
                "tool_calls": [],
                "content": message.content
            }
            
            if hasattr(message, 'tool_calls') and message.tool_calls:
                # Convert tool_calls to JSON-serializable format
                serializable_tool_calls = []
                for tool_call in message.tool_calls:
                    serializable_tool_calls.append({
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    })
                
                routing_info["tool_calls"] = serializable_tool_calls
                
                # Check if SQL analysis is required
                for tool_call in message.tool_calls:
                    if tool_call.function.name == "agent_sql_analysis":
                        routing_info["requires_sql"] = True
                        
                        # Check if chart is requested in the arguments
                        try:
                            args = json.loads(tool_call.function.arguments)
                            user_request = args.get("user_requests", "").lower()
                            chart_keywords = ["chart", "graph", "plot", "visual", "pie", "bar", "line"]
                            if any(kw in user_request for kw in chart_keywords):
                                routing_info["requires_chart"] = True
                        except (json.JSONDecodeError, KeyError):
                            pass
                            
            return routing_info
            
        except Exception as e:
            logger.error(f"Failed to extract routing decision: {e}")
            return {
                "requires_sql": False,
                "requires_chart": False,
                "tool_calls": [],
                "content": "Unable to process routing decision",
                "error": str(e)
            }
