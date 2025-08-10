"""
Custom exceptions for the Text2SQL application.
"""

from typing import Optional, Dict, Any


class Text2SQLException(Exception):
    """Base exception for Text2SQL application."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class SQLGenerationError(Text2SQLException):
    """Exception raised when SQL generation fails."""
    
    def __init__(self, message: str = "SQL generation failed", **kwargs):
        super().__init__(message, error_code="SQL_GENERATION_ERROR", **kwargs)


class SQLExecutionError(Text2SQLException):
    """Exception raised when SQL execution fails."""
    
    def __init__(self, message: str = "SQL execution failed", **kwargs):
        super().__init__(message, error_code="SQL_EXECUTION_ERROR", **kwargs)


class SQLValidationError(Text2SQLException):
    """Exception raised when SQL validation fails."""
    
    def __init__(self, message: str = "SQL validation failed", **kwargs):
        super().__init__(message, error_code="SQL_VALIDATION_ERROR", **kwargs)


class DatabaseConnectionError(Text2SQLException):
    """Exception raised when database connection fails."""
    
    def __init__(self, message: str = "Database connection failed", **kwargs):
        super().__init__(message, error_code="DATABASE_CONNECTION_ERROR", **kwargs)


class VectorDatabaseError(Text2SQLException):
    """Exception raised when vector database operations fail."""
    
    def __init__(self, message: str = "Vector database operation failed", **kwargs):
        super().__init__(message, error_code="VECTOR_DATABASE_ERROR", **kwargs)


class ChartGenerationError(Text2SQLException):
    """Exception raised when chart generation fails."""
    
    def __init__(self, message: str = "Chart generation failed", **kwargs):
        super().__init__(message, error_code="CHART_GENERATION_ERROR", **kwargs)


class TableNotFoundError(Text2SQLException):
    """Exception raised when requested table is not found."""
    
    def __init__(self, table_name: str, **kwargs):
        message = f"Table '{table_name}' not found"
        super().__init__(message, error_code="TABLE_NOT_FOUND", **kwargs)


class InvalidQueryError(Text2SQLException):
    """Exception raised when query is invalid."""
    
    def __init__(self, message: str = "Invalid query", **kwargs):
        super().__init__(message, error_code="INVALID_QUERY", **kwargs)


class AuthenticationError(Text2SQLException):
    """Exception raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, error_code="AUTHENTICATION_ERROR", **kwargs)


class ConfigurationError(Text2SQLException):
    """Exception raised when configuration is invalid."""
    
    def __init__(self, message: str = "Configuration error", **kwargs):
        super().__init__(message, error_code="CONFIGURATION_ERROR", **kwargs)


class ServiceUnavailableError(Text2SQLException):
    """Exception raised when a required service is unavailable."""
    
    def __init__(self, service_name: str, **kwargs):
        message = f"Service '{service_name}' is unavailable"
        super().__init__(message, error_code="SERVICE_UNAVAILABLE", **kwargs)


class RateLimitError(Text2SQLException):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, error_code="RATE_LIMIT_ERROR", **kwargs)


class TimeoutError(Text2SQLException):
    """Exception raised when operation times out."""
    
    def __init__(self, operation: str = "Operation", **kwargs):
        message = f"{operation} timed out"
        super().__init__(message, error_code="TIMEOUT_ERROR", **kwargs)


class DataValidationError(Text2SQLException):
    """Exception raised when data validation fails."""
    
    def __init__(self, message: str = "Data validation failed", **kwargs):
        super().__init__(message, error_code="DATA_VALIDATION_ERROR", **kwargs)


class PermissionError(Text2SQLException):
    """Exception raised when user lacks required permissions."""
    
    def __init__(self, message: str = "Permission denied", **kwargs):
        super().__init__(message, error_code="PERMISSION_ERROR", **kwargs)
