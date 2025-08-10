"""
Validation utilities for input validation and data checking.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Union
from app.utils.exceptions import InvalidQueryError, DataValidationError

logger = logging.getLogger(__name__)


class QueryValidator:
    """Validator for natural language and SQL queries."""
    
    # Dangerous SQL keywords that should be restricted
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'INSERT', 'UPDATE',
        'GRANT', 'REVOKE', 'EXEC', 'EXECUTE', 'SHUTDOWN', 'RESTORE'
    ]
    
    # Valid SQL statement prefixes
    VALID_SQL_PREFIXES = [
        'SELECT', 'WITH', 'SHOW', 'DESCRIBE', 'EXPLAIN', 'ANALYZE'
    ]
    
    @staticmethod
    def validate_natural_language_query(query: str) -> Dict[str, Any]:
        """
        Validate natural language query.
        
        Args:
            query: Natural language query string
            
        Returns:
            Validation result dictionary
        """
        validation = {
            "is_valid": True,
            "warnings": [],
            "suggestions": []
        }
        
        try:
            # Basic checks
            if not query or not query.strip():
                validation["is_valid"] = False
                validation["warnings"].append("Query cannot be empty")
                return validation
            
            # Length check
            if len(query) > 1000:
                validation["warnings"].append("Query is very long, consider breaking it down")
            
            if len(query) < 5:
                validation["warnings"].append("Query seems too short, please be more specific")
            
            # Check for common SQL injection patterns
            suspicious_patterns = [
                r";\s*(drop|delete|truncate|alter)",
                r"union\s+select",
                r"exec\s*\(",
                r"<script",
                r"javascript:",
                r"--\s*$"
            ]
            
            query_lower = query.lower()
            for pattern in suspicious_patterns:
                if re.search(pattern, query_lower):
                    validation["warnings"].append("Query contains potentially suspicious content")
                    break
            
            # Check for dangerous keywords in natural language context
            for keyword in QueryValidator.DANGEROUS_KEYWORDS:
                if keyword.lower() in query_lower:
                    validation["warnings"].append(f"Query mentions potentially dangerous operation: {keyword}")
            
            # Suggestions for better queries
            if "?" not in query and query.strip()[-1] not in ".!":
                validation["suggestions"].append("Consider ending your question with a question mark")
            
            if len(query.split()) < 3:
                validation["suggestions"].append("Try to be more descriptive in your query")
                
            logger.debug(f"Natural language query validation: {validation}")
            return validation
            
        except Exception as e:
            logger.error(f"Natural language query validation failed: {e}")
            return {
                "is_valid": False,
                "warnings": [f"Validation error: {str(e)}"],
                "suggestions": []
            }
    
    @staticmethod
    def validate_sql_query(sql_query: str) -> Dict[str, Any]:
        """
        Validate SQL query syntax and safety.
        
        Args:
            sql_query: SQL query string
            
        Returns:
            Validation result dictionary
        """
        validation = {
            "is_valid": True,
            "warnings": [],
            "suggestions": []
        }
        
        try:
            if not sql_query or not sql_query.strip():
                validation["is_valid"] = False
                validation["warnings"].append("SQL query cannot be empty")
                return validation
            
            sql_upper = sql_query.upper().strip()
            
            # Check if query starts with valid SQL keywords
            is_valid_start = any(sql_upper.startswith(prefix) for prefix in QueryValidator.VALID_SQL_PREFIXES)
            if not is_valid_start:
                validation["is_valid"] = False
                validation["warnings"].append("SQL query must start with a valid SELECT-like statement")
            
            # Check for dangerous operations
            for keyword in QueryValidator.DANGEROUS_KEYWORDS:
                if keyword in sql_upper:
                    validation["is_valid"] = False
                    validation["warnings"].append(f"Dangerous SQL operation not allowed: {keyword}")
            
            # Basic syntax checks
            if sql_query.count('(') != sql_query.count(')'):
                validation["warnings"].append("Mismatched parentheses in SQL query")
            
            if sql_query.count("'") % 2 != 0:
                validation["warnings"].append("Unmatched single quotes in SQL query")
            
            if sql_query.count('"') % 2 != 0:
                validation["warnings"].append("Unmatched double quotes in SQL query")
            
            # Performance suggestions
            if "SELECT *" in sql_upper:
                validation["suggestions"].append("Consider selecting specific columns instead of using SELECT *")
            
            if "WHERE" not in sql_upper and "LIMIT" not in sql_upper:
                validation["suggestions"].append("Consider adding WHERE clause or LIMIT to avoid large result sets")
            
            logger.debug(f"SQL query validation: {validation}")
            return validation
            
        except Exception as e:
            logger.error(f"SQL query validation failed: {e}")
            return {
                "is_valid": False,
                "warnings": [f"Validation error: {str(e)}"],
                "suggestions": []
            }
    
    @staticmethod
    def sanitize_input(input_text: str) -> str:
        """
        Sanitize user input by removing potentially harmful content.
        
        Args:
            input_text: Raw input text
            
        Returns:
            Sanitized input text
        """
        try:
            if not input_text:
                return ""
            
            # Remove null bytes
            sanitized = input_text.replace('\x00', '')
            
            # Remove excessive whitespace
            sanitized = re.sub(r'\s+', ' ', sanitized)
            
            # Trim
            sanitized = sanitized.strip()
            
            return sanitized
            
        except Exception as e:
            logger.error(f"Input sanitization failed: {e}")
            return input_text


class DataValidator:
    """Validator for data structures and API payloads."""
    
    @staticmethod
    def validate_chat_history(chat_history: List[Dict[str, Any]]) -> bool:
        """
        Validate chat history structure.
        
        Args:
            chat_history: List of chat messages
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if not isinstance(chat_history, list):
                return False
            
            for message in chat_history:
                if not isinstance(message, dict):
                    return False
                
                if "role" not in message or "content" not in message:
                    return False
                
                if message["role"] not in ["user", "assistant", "system"]:
                    return False
                
                if not isinstance(message["content"], (str, dict)):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Chat history validation failed: {e}")
            return False
    
    @staticmethod
    def validate_sql_results(results: Any) -> bool:
        """
        Validate SQL results structure.
        
        Args:
            results: SQL results to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if not isinstance(results, list):
                return False
            
            for result in results:
                if not isinstance(result, dict):
                    return False
                
                # Check for required fields
                if "status" not in result:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"SQL results validation failed: {e}")
            return False
    
    @staticmethod
    def validate_table_metadata(metadata: str) -> bool:
        """
        Validate table metadata format.
        
        Args:
            metadata: Table metadata string
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if not isinstance(metadata, str):
                return False
            
            # Basic check for table-like content
            metadata_lower = metadata.lower()
            table_indicators = ["table", "column", "field", "type", "schema"]
            
            return any(indicator in metadata_lower for indicator in table_indicators)
            
        except Exception as e:
            logger.error(f"Table metadata validation failed: {e}")
            return False


def validate_request_data(data: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate that required fields are present in request data.
    
    Args:
        data: Request data dictionary
        required_fields: List of required field names
        
    Raises:
        DataValidationError: If validation fails
    """
    try:
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif data[field] is None:
                missing_fields.append(field)
            elif isinstance(data[field], str) and not data[field].strip():
                missing_fields.append(field)
        
        if missing_fields:
            raise DataValidationError(f"Missing required fields: {', '.join(missing_fields)}")
            
    except DataValidationError:
        raise
    except Exception as e:
        logger.error(f"Request data validation failed: {e}")
        raise DataValidationError(f"Validation error: {str(e)}")


def validate_pagination_params(page: int, page_size: int, max_page_size: int = 1000) -> None:
    """
    Validate pagination parameters.
    
    Args:
        page: Page number (1-based)
        page_size: Number of items per page
        max_page_size: Maximum allowed page size
        
    Raises:
        DataValidationError: If validation fails
    """
    try:
        if page < 1:
            raise DataValidationError("Page number must be 1 or greater")
        
        if page_size < 1:
            raise DataValidationError("Page size must be 1 or greater")
        
        if page_size > max_page_size:
            raise DataValidationError(f"Page size cannot exceed {max_page_size}")
            
    except DataValidationError:
        raise
    except Exception as e:
        logger.error(f"Pagination validation failed: {e}")
        raise DataValidationError(f"Pagination validation error: {str(e)}")
