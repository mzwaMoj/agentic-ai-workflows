"""
Final response agent for polishing and formatting final responses.
"""

import logging
from typing import List, Dict, Any, Optional
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class FinalAgent:
    """Agent responsible for generating polished final responses."""
    
    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service
        
    async def generate_final_response(
        self, 
        user_query: str, 
        sql_results: List[Dict[str, Any]], 
        chart_html: Optional[str] = None
    ) -> str:
        """
        Generate a polished final response based on query results.
        
        Args:
            user_query: Original user query
            sql_results: Results from SQL execution
            chart_html: Optional chart HTML
            
        Returns:
            Polished natural language response
        """
        try:            # Import prompt from app module
            from app.prompts import prompt_agent_final_response
            
            # Build comprehensive prompt
            polish_prompt = self._build_polish_prompt(user_query, sql_results, chart_html)
            
            messages = [{"role": "user", "content": polish_prompt}]
            
            # Call OpenAI for final response generation
            response = await self.openai_service.chat_completion(
                messages=messages,
                temperature=0.1
            )
            
            final_response = response.choices[0].message.content
            
            logger.info(f"Final response generated for query: {user_query[:50]}...")
            return final_response
            
        except Exception as e:
            logger.error(f"Final agent failed to generate response: {e}")
            return self._create_fallback_response(user_query, sql_results, chart_html)
            
    def _build_polish_prompt(
        self, 
        user_query: str, 
        sql_results: List[Dict[str, Any]], 
        chart_html: Optional[str] = None
    ) -> str:
        """
        Build a comprehensive prompt for final response generation.
        
        Args:
            user_query: Original user query
            sql_results: Results from SQL execution
            chart_html: Optional chart HTML
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = [f"User Query: '{user_query}'\n"]
        
        # Process SQL results
        successful_sql = [r for r in sql_results if r.get("type") == "sql_success"]
        failed_sql = [r for r in sql_results if r.get("type") == "sql_error"]
        
        if successful_sql:
            prompt_parts.append("SQL Query Results:")
            for result in successful_sql:
                prompt_parts.append(f"- {result.get('query_info', 'Query executed')}")
                data = result.get('data')
                if data:
                    # Limit data display for prompt
                    if isinstance(data, list) and len(data) > 5:
                        prompt_parts.append(f"  Data (first 5 rows): {data[:5]}")
                        prompt_parts.append(f"  Total rows: {len(data)}")
                    else:
                        prompt_parts.append(f"  Data: {data}")
        
        if failed_sql:
            prompt_parts.append("SQL Query Errors:")
            for result in failed_sql:
                prompt_parts.append(f"- {result.get('query_info', 'Query failed')}")
        
        # Handle chart information
        if chart_html:
            if "Error" in chart_html or "failed" in chart_html.lower():
                prompt_parts.append("Chart Generation: Failed to generate visualization")
            else:
                prompt_parts.append("Chart Generation: Successfully generated visualization")
        
        prompt_parts.append("\nPlease provide a clear, friendly, and comprehensive summary of these results.")
        prompt_parts.append("Focus on answering the user's question directly and highlight key insights from the data.")
        
        return "\n".join(prompt_parts)
        
    def _create_fallback_response(
        self, 
        user_query: str, 
        sql_results: List[Dict[str, Any]], 
        chart_html: Optional[str] = None
    ) -> str:
        """
        Create a fallback response when final agent fails.
        
        Args:
            user_query: Original user query
            sql_results: Results from SQL execution
            chart_html: Optional chart HTML
            
        Returns:
            Basic fallback response
        """
        message_parts = ["I've processed your request but encountered an issue formatting the complete response."]
        
        if sql_results:
            successful_count = len([r for r in sql_results if r.get("type") == "sql_success"])
            failed_count = len([r for r in sql_results if r.get("type") == "sql_error"])
            
            if successful_count > 0:
                message_parts.append(f"Successfully executed {successful_count} SQL queries.")
                
                # Try to show some data
                for result in sql_results:
                    if result.get("type") == "sql_success" and result.get("data"):
                        data = result.get("data")
                        if isinstance(data, list) and len(data) > 0:
                            message_parts.append(f"Found {len(data)} records in the results.")
                        break
                        
            if failed_count > 0:
                message_parts.append(f"Encountered {failed_count} query errors.")
        
        if chart_html and "Error" not in chart_html:
            message_parts.append("Generated visualization successfully.")
        
        return " ".join(message_parts)
        
    async def summarize_data(self, data: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of data results.
        
        Args:
            data: Data to summarize
            
        Returns:
            Natural language summary of the data
        """
        try:
            if not data:
                return "No data found."
                
            summary_prompt = f"""
            Please provide a brief, informative summary of the following data.
            Highlight key patterns, totals, and interesting insights.
            
            Data: {data[:10] if len(data) > 10 else data}
            {f"(Showing first 10 of {len(data)} total records)" if len(data) > 10 else ""}
            """
            
            messages = [{"role": "user", "content": summary_prompt}]
            
            response = await self.openai_service.chat_completion(
                messages=messages,
                temperature=0.1
            )
            
            summary = response.choices[0].message.content
            
            logger.info("Data summary generated successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate data summary: {e}")
            return f"Found {len(data)} records in the results."
