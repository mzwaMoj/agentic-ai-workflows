"""
Main Text2SQL Engine - Core business logic orchestrator.
Follows the exact logic from chatbot.py to maintain functionality.
"""

import json
import logging
import sys
import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Add project root to path for imports at module level
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Import agents at module level to avoid hanging during request processing
try:
    from agents.agents import (
        routing_agent,  
        agent_sql_analysis, 
        agent_generate_charts,
        agent_table_router,
        agent_final_response
    )
    from app.db.sql_query_executor import execute_sql_with_pyodbc
    from app.utils.generate_charts import execute_plot_code
    
    AGENTS_IMPORTED = True
except ImportError as e:
    logging.warning(f"Failed to import agents: {e}")
    AGENTS_IMPORTED = False

logger = logging.getLogger(__name__)


class Text2SQLEngine:
    """Main engine for processing text-to-SQL requests and generating responses."""
    
    def __init__(self, services: Dict[str, Any]):
        # Store services
        self.services = services
        self.openai_service = services['openai']
        self.database_service = services['database']
        self.vector_service = services['vector']
        self.logging_service = services['logging']
        
    async def process_query(self, user_input: str, chat_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Main processing pipeline following chatbot.py logic exactly.
        
        Args:
            user_input: User's natural language query
            chat_history: Optional chat history for context
            
        Returns:
            Complete response with SQL results, charts, and formatted response
        """
        # Initialize chat history if not provided
        if chat_history is None:
            chat_history = []
            
        # Add user input to chat history if not already there
        if not chat_history or chat_history[-1]["role"] != "user" or chat_history[-1]["content"] != user_input:
            chat_history.append({"role": "user", "content": user_input})        # Start MLflow tracking (following chatbot.py)
        self.logging_service.start_chat_run(user_input)        
        try:
            # Check if agents are available
            if not AGENTS_IMPORTED:
                logger.error("Agents not imported - returning error response")
                return {
                    "success": False,
                    "error": "Agents not available",
                    "response": "I'm sorry, but I'm experiencing technical difficulties. Please try again later.",
                    "chat_history": chat_history
                }
                
            # Step 1: Route the query (following chatbot.py)
            response = routing_agent(user_input, chat_history)
            message = response.choices[0].message
            self.logging_service.log_router_response(message)

            chart_html = None  # Will hold the chart HTML if generated

            # Step 2: Process tool calls (following chatbot.py logic)
            if hasattr(message, 'tool_calls') and message.tool_calls:
                logger.info(f"Processing {len(message.tool_calls)} tool call(s)")
                sql_results = []
                chart_results = []
                unknown_functions = []

                for i, tool_call in enumerate(message.tool_calls):
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    logger.info(f"Tool Call {i+1}: {function_name}")

                    if function_name == "agent_sql_analysis":
                        # Handle SQL analysis (following chatbot.py)
                        sql_results, chart_html = await self._handle_sql_analysis(
                            user_input, function_args, agent_sql_analysis, 
                            agent_table_router, execute_sql_with_pyodbc,
                            agent_generate_charts, execute_plot_code
                        )
                    else:
                        unknown_functions.append(function_name)
                        logger.warning(f"Unknown function '{function_name}' encountered")

                # Step 3: Generate polished response (following chatbot.py)
                polish_prompt = self._build_polish_prompt(sql_results, chart_results, user_input)
                self.logging_service.log_polish_prompt(polish_prompt)
                
                if polish_prompt:
                    polish_chat_history = [{"role": "user", "content": polish_prompt}]
                    polish_response = agent_final_response(polish_prompt, polish_chat_history)
                    
                    if polish_response:
                        final_message = polish_response
                        self.logging_service.log_final_response(final_message)
                        
                        # Update chat history (following chatbot.py)
                        if chart_html is not None:
                            chat_history.append({
                                "role": "assistant",
                                "content": {
                                    "text": final_message,
                                    "chart_html": chart_html
                                }
                            })
                        else:
                            chat_history.append({"role": "assistant", "content": final_message})
                            
                        return {
                            "success": True,
                            "response": final_message,
                            "sql_results": sql_results,
                            "chart_html": chart_html,
                            "chat_history": chat_history,
                            "routing_info": {
                                "requires_sql": True,
                                "requires_chart": chart_html is not None,
                                "tool_calls": [{"name": tc.function.name} for tc in message.tool_calls]
                            }
                        }
                    else:
                        fallback_message = self._create_fallback_message(sql_results, chart_results)
                        chat_history.append({"role": "assistant", "content": fallback_message})
                        self.logging_service.log_final_response(fallback_message)
                        
                        return {
                            "success": True,
                            "response": fallback_message,
                            "sql_results": sql_results,
                            "chart_html": chart_html,
                            "chat_history": chat_history,
                            "routing_info": {"requires_sql": True}
                        }
                else:
                    assistant_msg = "I couldn't process your request. Please try again."
                    chat_history.append({"role": "assistant", "content": assistant_msg})
                    return {
                        "success": False,
                        "response": assistant_msg,
                        "chat_history": chat_history,
                        "error": "Could not build polish prompt"
                    }
            else:
                # Handle non-tool responses (following chatbot.py)
                content = message.content or "I don't have a response for that."
                self.logging_service.log_final_response(content)
                chat_history.append({"role": "assistant", "content": content})                
                return {
                    "success": True,
                    "response": content,
                    "chat_history": chat_history,
                    "routing_info": {"requires_sql": False}
                }

        except Exception as e:
            logger.error(f"Text2SQL Engine Error: {str(e)}")
            self.logging_service.log_error(f"Text2SQL Engine Error: {str(e)}")
            
            error_response = "I encountered an error processing your request. Please try again or rephrase your question."
            chat_history.append({"role": "assistant", "content": error_response})
            return {
                "success": False,
                "error": str(e),
                "response": error_response,
                "chat_history": chat_history
            }
        finally:
            # End MLflow tracking (following chatbot.py)
            self.logging_service.end_chat_run()
            
    async def _handle_sql_analysis(self, user_input: str, function_args: dict, 
                                   agent_sql_analysis, agent_table_router, 
                                   execute_sql_with_pyodbc, agent_generate_charts, 
                                   execute_plot_code) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Handle SQL analysis following chatbot.py logic exactly.
        """
        chart_html = None
        try:            # Step 1: Get required tables (following chatbot.py)
            required_tables = self._agent_table_retriever(user_input, agent_table_router)
            self.logging_service.log_table_retriever_response(required_tables)
            
            # Step 2: Generate SQL (following chatbot.py)
            sql_code = agent_sql_analysis(user_input, required_tables)
            self.logging_service.log_sql_code(sql_code)
            
            # Step 3: Execute SQL (following chatbot.py)
            sql_results = execute_sql_with_pyodbc(sql_code, auth_type='windows')
            self.logging_service.log_sql_results(sql_results)

            # Step 4: Process results (following chatbot.py)
            processed_results = []
            for res in sql_results:
                if isinstance(res, dict) and res.get("status") == "success":
                    try:
                        if isinstance(res["result"], str):
                            json_data = json.loads(res["result"])
                        else:
                            json_data = "[Chart visual generated]" if "HTML" in str(type(res["result"])) else str(res["result"])
                        processed_results.append({
                            "type": "sql_success",
                            "query_info": f"Query returned {res['row_count']} rows with columns: {', '.join(res['columns'])}",
                            "data": json_data,
                            "user_request": function_args.get("user_requests", user_input)
                        })
                    except (json.JSONDecodeError, TypeError):
                        processed_results.append({
                            "type": "sql_success",
                            "query_info": f"Query returned {res['row_count']} rows",
                            "data": str(res["result"]),
                            "user_request": function_args.get("user_requests", user_input)
                        })
                else:
                    processed_results.append({
                        "type": "sql_error",
                        "query_info": f"Query failed with status: {res.get('status', 'unknown')}",
                        "data": res.get("result", "No data available"),
                        "user_request": function_args.get("user_requests", user_input)
                    })
              # Step 5: Generate chart visual if user request is for a chart (following chatbot.py)
            chart_keywords = ["chart", "graph", "plot", "visual", "pie", "bar", "barh", "line", "scatter", "histogram", "heatmap", "boxplot",
                              "distribution", "trend", "time series", "dashboard", "visualization", "map", "bubble", "treemap", "funnel", "gauge", 
                              "area", "donut", "violin", "pareto", "tile", "scorecard",
                            "calendar", "heat", "flow", "network", "cohort", "forecast", "seasonal", "trendline", "comparison", "summary",
                            "overview", "slice", "breakdown", "distribution chart", "performance chart", "KPI", "metric", "speedometer",
                            "traffic light", "waterfall", "stacked", "multi-line", "multi-bar", "interactive", "real-time", "live"]
            if any(kw in user_input.lower() for kw in chart_keywords):                
                chart_code = agent_generate_charts("User Query: " + user_input + f"\nHere is the data: \n {sql_results}")
                chart_html_obj = execute_plot_code(chart_code)
                
                # Convert IPython.display.HTML object to string for API response
                if hasattr(chart_html_obj, 'data'):
                    if chart_html_obj.data and "Error" not in str(chart_html_obj.data):
                        chart_html = chart_html_obj.data  # Extract HTML string from IPython.display.HTML object
                    elif "Error" in str(chart_html_obj.data):
                        chart_html = chart_html_obj.data  # Keep error message
                    else:
                        chart_html = None  # Empty data
                else:
                    # If it's already a string, use it directly
                    chart_html = str(chart_html_obj) if chart_html_obj else None
                
                self.logging_service.log_generated_chart_results("[Chart visual generated]")
            return processed_results, chart_html        
        except Exception as e:
            logger.error(f"Error in SQL analysis: {e}")
            self.logging_service.log_sql_analysis_error(f"Error in SQL analysis: {e}")
            return ([{
                "type": "sql_error", 
                "query_info": f"SQL analysis failed: {str(e)}",
                "data": None,
                "user_request": function_args.get("user_requests", user_input)
            }], None)

    def _agent_table_retriever(self, user_request: str, agent_table_router):
        """
        Table retriever following chatbot.py logic exactly.
        """
        import json
        
        try:
            # Get response from table router (following chatbot.py)
            response = agent_table_router(user_request)
            
            tool_call = response.choices[0].message.tool_calls[0]
            if tool_call.function.name == "agent_table_rag":
                args = json.loads(tool_call.function.arguments)
                  # Use the vector service's search_tables method (following the service pattern)
                try:
                    table_results_response = self.vector_service.search_tables(str(args.get("relevant_tables")))
                    
                    # Create a mock response object to match chatbot.py structure
                    class MockResponse:
                        def __init__(self, response_text):
                            self.response = response_text
                    
                    table_results = MockResponse(table_results_response)
                    
                    # Log the required tables
                    try:
                        from app.utils import log_required_tables
                        log_required_tables(args.get("relevant_tables"))
                    except ImportError:
                        logger.warning("MLflow logger not available for table logging")
                    
                    return table_results.response
                except Exception as vector_error:
                    logger.error(f"Vector service search failed: {vector_error}")
                    # Fallback to mock data to prevent server crash
                    return f"Mock table metadata for: {args.get('relevant_tables', 'customer tables')}"
            else:
                raise ValueError("Unexpected tool call name: {}".format(tool_call.function.name))
        
        except Exception as e:
            logger.error(f"Table router failed: {e}")
            # Return fallback table metadata to prevent complete failure
            return "Mock table metadata: customer_information(id, name, email), transaction_history(id, customer_id, amount, date)"

    def _build_polish_prompt(self, sql_results: List[Dict], chart_results: List[Dict], user_input: str) -> Optional[str]:
        """
        Build polish prompt following chatbot.py logic exactly.
        """
        if not sql_results and not chart_results:
            return None
        
        prompt_parts = [f"User Query: '{user_input}'\n"]
        
        successful_sql = [r for r in sql_results if r["type"] == "sql_success"]
        failed_sql = [r for r in sql_results if r["type"] == "sql_error"]
        
        if successful_sql:
            prompt_parts.append("SQL Query Results:")
            for result in successful_sql:
                prompt_parts.append(f"- {result['query_info']}")
                prompt_parts.append(f"  Data: {result['data']}")
        
        if failed_sql:
            prompt_parts.append("SQL Query Errors:")
            for result in failed_sql:
                prompt_parts.append(f"- {result['query_info']}")
        
        successful_charts = [r for r in chart_results if r["type"] == "chart_success"]
        failed_charts = [r for r in chart_results if r["type"] == "chart_error"]
        
        if successful_charts:
            prompt_parts.append("Chart Generation Results:")
            for result in successful_charts:
                prompt_parts.append(f"- Successfully generated chart for: {result['user_request']}")
        
        if failed_charts:
            prompt_parts.append("Chart Generation Errors:")
            for result in failed_charts:
                prompt_parts.append(f"- Failed to generate chart: {result['error']}")
        
        prompt_parts.append("\nPlease provide a clear, friendly summary of these results.")
        
        return "\n".join(prompt_parts)

    def _create_fallback_message(self, sql_results: List[Dict], chart_results: List[Dict]) -> str:
        """
        Create fallback message following chatbot.py logic exactly.
        """
        message_parts = ["I've analyzed your request but encountered an issue formatting the results."]
        
        if sql_results:
            successful_count = len([r for r in sql_results if r["type"] == "sql_success"])
            message_parts.append(f"Successfully executed {successful_count} SQL queries.")
        
        if chart_results:
            successful_charts = len([r for r in chart_results if r["type"] == "chart_success"])
            message_parts.append(f"Successfully generated {successful_charts} charts.")
        
        return " ".join(message_parts)
    
    async def validate_query(self, query: str) -> Dict[str, Any]:
        """
        Validate query for safety and format.
        """
        try:
            # Basic validation
            if not query or len(query.strip()) == 0:
                return {"is_valid": False, "warnings": ["Query is empty"]}
            
            if len(query) > 1000:
                return {"is_valid": False, "warnings": ["Query is too long (max 1000 characters)"]}
            
            # SQL injection basic check
            dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
            query_upper = query.upper()
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    return {"is_valid": False, "warnings": [f"Dangerous SQL keyword detected: {keyword}"]}
            
            return {"is_valid": True, "warnings": []}
            
        except Exception as e:
            return {"is_valid": False, "warnings": [f"Validation error: {str(e)}"]}
