"""
SQL agent for generating SQL queries from natural language.
"""

import logging
from typing import Optional
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class SQLAgent:
    """Agent responsible for generating SQL queries from natural language."""
    
    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service
        
    async def generate_sql(self, user_query: str, required_tables: str) -> str:
        """
        Generate SQL query from user's natural language request.
        
        Args:
            user_query: User's natural language query
            required_tables: Metadata about relevant database tables
              Returns:
            Generated SQL query as string
        """
        try:
            # Import prompt from app module
            from app.prompts import prompt_agent_sql_analysis
            
            # Prepare the prompt with user query and table metadata
            full_prompt = prompt_agent_sql_analysis().format(required_tables=required_tables)
            
            messages = [{"role": "user", "content": full_prompt}]
            
            # Call OpenAI for SQL generation
            response = await self.openai_service.chat_completion(
                messages=messages,
                temperature=0.0
            )
            
            sql_query = response.choices[0].message.content
            
            logger.info(f"SQL agent generated query for: {user_query[:50]}...")
            logger.debug(f"Generated SQL: {sql_query[:100]}...")
            
            return sql_query
            
        except Exception as e:
            logger.error(f"SQL agent failed to generate query: {e}")
            raise
            
    async def validate_sql_syntax(self, sql_query: str) -> bool:
        """
        Basic validation of SQL query syntax.
        
        Args:
            sql_query: SQL query to validate
            
        Returns:
            True if syntax appears valid, False otherwise
        """
        try:
            if not sql_query or not sql_query.strip():
                return False
                
            # Basic SQL keyword validation
            sql_upper = sql_query.upper().strip()
            
            # Must start with SELECT, WITH, or be a comment
            valid_starts = ['SELECT', 'WITH', '--', '/*']
            if not any(sql_upper.startswith(start) for start in valid_starts):
                return False
                
            # Basic structure check
            if 'SELECT' in sql_upper and 'FROM' in sql_upper:
                return True
            elif sql_upper.startswith('WITH') and 'SELECT' in sql_upper:
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"SQL validation failed: {e}")
            return False
            
    async def explain_sql(self, sql_query: str) -> str:
        """
        Generate natural language explanation of SQL query.
        
        Args:
            sql_query: SQL query to explain
            
        Returns:
            Natural language explanation of the query
        """
        try:
            explanation_prompt = f"""
            Please provide a clear, natural language explanation of the following SQL query.
            Explain what the query does, which tables it uses, what conditions are applied,
            and what results it will return.
            
            SQL Query:
            {sql_query}
            """
            
            messages = [{"role": "user", "content": explanation_prompt}]
            
            response = await self.openai_service.chat_completion(
                messages=messages,
                temperature=0.1
            )
            
            explanation = response.choices[0].message.content
            
            logger.info("SQL explanation generated successfully")
            return explanation
            
        except Exception as e:
            logger.error(f"Failed to generate SQL explanation: {e}")
            return f"Unable to explain query: {str(e)}"
