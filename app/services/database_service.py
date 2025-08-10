# """
# Database service for SQL Server connections and query execution.
# """

import logging
from typing import List, Dict, Any, Optional
from app.config.settings import Settings

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for managing SQL Server database operations."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.connection = None        
        self.cursor = None
        
    async def connect(self):
        """Establish database connection."""
        try:
            # Import here to avoid circular imports and ensure modules are available
            from app.db import connect_to_sql_server
            
            self.connection, self.cursor = connect_to_sql_server(
                server=self.settings.db_server,
                database=self.settings.db_database,
                auth_type=self.settings.db_auth_type,
                # username=self.settings.db_username,
                # password=self.settings.db_password
            )
            
            if self.connection:
                logger.info("Database connection established successfully")
            else:
                raise Exception("Failed to establish database connection")
                
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
            
    async def execute_sql(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Execute SQL query and return results.
        
        Args:
            sql_query: SQL query string to execute
            
        Returns:
            List of query results        """
        try:
            # Ensure we have an active connection
            if not self.connection:
                await self.connect()
            
            # Import here to avoid circular imports
            from app.db.sql_query_executor import execute_multiple_sql_code
            
            # Format query for the executor (it expects code blocks)
            formatted_query = f"```sql\n{sql_query}\n```"
            
            # Use the existing connection
            results = execute_multiple_sql_code(formatted_query, self.connection)
            
            logger.info(f"SQL query executed successfully. Results: {len(results)} records")
            return results
            
        except Exception as e:
            logger.error(f"SQL query execution failed: {e}")
            raise
            
    async def execute_multiple_sql(self, sql_queries: List[str]) -> List[Dict[str, Any]]:
        """
        Execute multiple SQL queries.
        
        Args:
            sql_queries: List of SQL query strings
            
        Returns:
            List of results for each query        """
        try:
            # Ensure we have an active connection
            if not self.connection:
                await self.connect()
                
            # Import here to avoid circular imports
            from app.db.sql_query_executor import execute_multiple_sql_code
            
            # Format queries properly
            formatted_queries = []
            for query in sql_queries:
                if not query.strip().startswith("```"):
                    formatted_queries.append(f"```sql\n{query}\n```")
                else:
                    formatted_queries.append(query)
            
            combined_queries = "\n\n".join(formatted_queries)
            results = execute_multiple_sql_code(combined_queries, self.connection)
            
            logger.info(f"Multiple SQL queries executed. {len(sql_queries)} queries processed")
            return results
            
        except Exception as e:
            logger.error(f"Multiple SQL query execution failed: {e}")
            raise
            
    async def validate_sql(self, sql_query: str) -> bool:
        """
        Validate SQL query syntax without executing.
        
        Args:
            sql_query: SQL query to validate
            
        Returns:
            True if valid, False otherwise        """
        try:
            # Import validation function
            from app.db.sql_query_executor import validate_sql_query
            
            is_valid, message = validate_sql_query(sql_query)
            
            if not is_valid:
                logger.warning(f"SQL validation failed: {message}")
                
            return is_valid
            
        except Exception as e:
            logger.error(f"SQL validation failed: {e}")
            return False
            
    async def close(self):
        # """Close database connections."""        
        try:
            if self.cursor:
                self.cursor.close()
                self.cursor = None
                
            if self.connection:
                self.connection.close()
                self.connection = None
                
            logger.info("Database connections closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")
            
    async def health_check(self) -> Dict[str, Any]:
        # """Perform health check for database service."""
        try:
            # Try to establish a connection
            await self.connect()
            
            # Try a simple query
            test_results = await self.execute_sql("SELECT 1 as test")
            
            # Don't close the connection here - keep it for future use
            # await self.close()
            
            is_healthy = len(test_results) > 0 and test_results[0].get("status") == "success"
            
            return {
                "service": "database",
                "status": "healthy" if is_healthy else "unhealthy",
                "server": self.settings.db_server,
                "database": self.settings.db_database,
                "auth_type": self.settings.db_auth_type
            }
            
        except Exception as e:
            return {
                "service": "database", 
                "status": "unhealthy",
                "error": str(e),
                "server": self.settings.db_server,
                "database": self.settings.db_database
            }
