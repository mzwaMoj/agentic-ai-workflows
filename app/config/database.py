"""
Database configuration and connection management.
"""

from typing import Optional
import logging
from app.config.settings import Settings

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration and connection management."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._connection = None
        self._cursor = None
        
    @property
    def connection_string(self) -> str:
        """Build connection string based on authentication type."""
        if self.settings.db_auth_type.lower() == "windows":
            return (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.settings.db_server};"
                f"DATABASE={self.settings.db_database};"
                f"Trusted_Connection=yes;"
            )
        else:
            return (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.settings.db_server};"
                f"DATABASE={self.settings.db_database};"
                f"UID={self.settings.db_username};"
                f"PWD={self.settings.db_password};"
            )
    
    def validate_config(self) -> bool:
        """Validate database configuration."""
        if not self.settings.db_server:
            raise ValueError("Database server is required")
            
        if self.settings.db_auth_type.lower() == "sql":
            if not self.settings.db_username or not self.settings.db_password:
                raise ValueError("Username and password required for SQL authentication")
                
        return True
        
    async def test_connection(self) -> bool:
        """Test database connection."""
        try:
            # Import here to avoid circular imports
            from app.services.database_service import DatabaseService
            
            db_service = DatabaseService(self.settings)
            await db_service.connect()
            await db_service.close()
            
            logger.info("Database connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
