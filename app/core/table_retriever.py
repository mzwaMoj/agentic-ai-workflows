"""
Table retriever for managing database table metadata operations.
"""

import logging
from typing import List, Optional, Dict
from app.services.vector_service import VectorService

logger = logging.getLogger(__name__)


class TableRetriever:
    """Service for retrieving relevant database table metadata."""
    
    def __init__(self, vector_service: VectorService):
        self.vector_service = vector_service
        
    async def get_relevant_tables(self, user_request: str) -> str:
        """
        Identify and retrieve metadata for tables relevant to the user's request.
        
        Args:
            user_request: User's natural language query
            
        Returns:
            Relevant table metadata as string
        """
        try:
            # First, determine which tables are needed using the table router agent
            table_names = await self._route_to_tables(user_request)
            
            # Then retrieve the full metadata for those tables
            table_metadata = await self.vector_service.search_tables(table_names)
            
            logger.info(f"Retrieved table metadata for query: {user_request[:50]}...")
            logger.debug(f"Relevant tables: {table_names}")
            
            return table_metadata
            
        except Exception as e:
            logger.error(f"Table retrieval failed: {e}")
            raise
            
    async def _route_to_tables(self, user_request: str) -> str:
        """
        Use the table router agent to identify relevant tables.
        
        Args:
            user_request: User's natural language query
            
        Returns:
            String containing relevant table names
        """
        try:
            # Import the existing table router agent
            from agents.agents import agent_table_router
            import json
            
            # Call the table router agent
            response = agent_table_router(user_request)
            
            # Extract table names from tool call response
            if hasattr(response, 'choices') and response.choices:
                message = response.choices[0].message
                
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    tool_call = message.tool_calls[0]
                    
                    if tool_call.function.name == "agent_table_rag":
                        args = json.loads(tool_call.function.arguments)
                        relevant_tables = args.get("relevant_tables", "")
                        
                        logger.debug(f"Table router identified tables: {relevant_tables}")
                        return str(relevant_tables)
                        
            # Fallback: return the user request for general search
            logger.warning("Table router did not return expected format, using fallback")
            return user_request
            
        except Exception as e:
            logger.error(f"Table routing failed: {e}")
            # Fallback to using the user request directly
            return user_request
            
    async def list_available_tables(self) -> List[str]:
        """
        Get a list of all available tables in the metadata collection.
        
        Returns:
            List of table names
        """
        try:
            # Get collection info from vector service
            collection_info = await self.vector_service.get_collection_info()
            
            if collection_info.get("status") == "ready":
                # For now, return known table types
                # This could be enhanced to dynamically discover tables
                known_tables = [
                    "customer_information",
                    "transaction_history", 
                    "crs_account_report",
                    "crs_messagespec",
                    "crs_countrycode"
                ]
                
                logger.info(f"Available tables: {known_tables}")
                return known_tables
            else:
                logger.warning("Vector collection not ready")
                return []
                
        except Exception as e:
            logger.error(f"Failed to list available tables: {e}")
            return []
            
    async def get_table_schema(self, table_name: str) -> Optional[str]:
        """
        Get detailed schema information for a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Table schema information or None if not found
        """
        try:
            # Search for specific table metadata
            schema_info = await self.vector_service.search_tables(table_name)
            
            if schema_info and schema_info.strip():
                logger.info(f"Retrieved schema for table: {table_name}")
                return schema_info
            else:
                logger.warning(f"No schema found for table: {table_name}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get schema for table {table_name}: {e}")
            return None
            
    async def validate_table_access(self, table_names: List[str]) -> Dict[str, bool]:
        """
        Validate access to specified tables.
        
        Args:
            table_names: List of table names to validate
            
        Returns:
            Dictionary mapping table names to access status
        """
        access_status = {}
        
        try:
            available_tables = await self.list_available_tables()
            
            for table_name in table_names:
                # Check if table exists in available tables
                access_status[table_name] = table_name.lower() in [t.lower() for t in available_tables]
                
            logger.info(f"Table access validation completed: {access_status}")
            return access_status
            
        except Exception as e:
            logger.error(f"Table access validation failed: {e}")
            # Return False for all tables in case of error
            return {table_name: False for table_name in table_names}
