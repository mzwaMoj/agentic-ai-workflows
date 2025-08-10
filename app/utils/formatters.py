"""
Formatting utilities for response formatting and data presentation.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Formatter for API responses and data presentation."""
    
    @staticmethod
    def format_sql_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format SQL results for consistent API response.
        
        Args:
            results: Raw SQL results from database
            
        Returns:
            Formatted results list
        """
        try:
            formatted_results = []
            
            for result in results:
                if not isinstance(result, dict):
                    continue
                
                formatted_result = {
                    "status": result.get("status", "unknown"),
                    "query": result.get("query", ""),
                    "data": ResponseFormatter._format_data(result.get("data")),
                    "row_count": 0,
                    "execution_time": result.get("execution_time"),
                    "error": result.get("error")
                }
                
                # Calculate row count
                if formatted_result["data"] and isinstance(formatted_result["data"], list):
                    formatted_result["row_count"] = len(formatted_result["data"])
                
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"SQL results formatting failed: {e}")
            return results
    
    @staticmethod
    def _format_data(data: Any) -> Any:
        """
        Format data values for JSON serialization.
        
        Args:
            data: Data to format
            
        Returns:
            JSON-serializable data
        """
        try:
            if data is None:
                return None
            
            if isinstance(data, str):
                # Try to parse JSON strings
                try:
                    return json.loads(data)
                except (json.JSONDecodeError, TypeError):
                    return data
            
            elif isinstance(data, (datetime, date)):
                return data.isoformat()
            
            elif isinstance(data, Decimal):
                return float(data)
            
            elif isinstance(data, list):
                return [ResponseFormatter._format_data(item) for item in data]
            
            elif isinstance(data, dict):
                return {key: ResponseFormatter._format_data(value) for key, value in data.items()}
            
            else:
                return data
                
        except Exception as e:
            logger.error(f"Data formatting failed: {e}")
            return str(data) if data is not None else None
    
    @staticmethod
    def format_chat_history(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format chat history for consistent presentation.
        
        Args:
            messages: List of chat messages
            
        Returns:
            Formatted chat history
        """
        try:
            formatted_messages = []
            
            for message in messages:
                if not isinstance(message, dict):
                    continue
                
                formatted_message = {
                    "role": message.get("role", "unknown"),
                    "content": ResponseFormatter._format_message_content(message.get("content")),
                    "timestamp": message.get("timestamp", datetime.now().isoformat())
                }
                
                # Add metadata if present
                if "metadata" in message:
                    formatted_message["metadata"] = message["metadata"]
                
                formatted_messages.append(formatted_message)
            
            return formatted_messages
            
        except Exception as e:
            logger.error(f"Chat history formatting failed: {e}")
            return messages
    
    @staticmethod
    def _format_message_content(content: Any) -> Union[str, Dict[str, Any]]:
        """
        Format message content for display.
        
        Args:
            content: Message content
            
        Returns:
            Formatted content
        """
        try:
            if isinstance(content, dict):
                # Handle structured content (e.g., with charts)
                formatted_content = {}
                
                if "text" in content:
                    formatted_content["text"] = str(content["text"])
                
                if "chart_html" in content:
                    formatted_content["chart_html"] = content["chart_html"]
                
                if "sql_results" in content:
                    formatted_content["sql_results"] = ResponseFormatter.format_sql_results(
                        content["sql_results"]
                    )
                
                return formatted_content if formatted_content else str(content)
            
            else:
                return str(content) if content is not None else ""
                
        except Exception as e:
            logger.error(f"Message content formatting failed: {e}")
            return str(content) if content is not None else ""
    
    @staticmethod
    def format_error_response(error: Exception, include_details: bool = False) -> Dict[str, Any]:
        """
        Format error for API response.
        
        Args:
            error: Exception object
            include_details: Whether to include detailed error information
            
        Returns:
            Formatted error response
        """
        try:
            error_response = {
                "success": False,
                "error": str(error),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add error code if available
            if hasattr(error, 'error_code'):
                error_response["error_code"] = error.error_code
            
            # Add details if requested and available
            if include_details:
                if hasattr(error, 'details'):
                    error_response["details"] = error.details
                
                error_response["error_type"] = type(error).__name__
            
            return error_response
            
        except Exception as e:
            logger.error(f"Error response formatting failed: {e}")
            return {
                "success": False,
                "error": "An error occurred",
                "timestamp": datetime.now().isoformat()
            }


class DataFormatter:
    """Formatter for data presentation and export."""
    
    @staticmethod
    def format_table_data(data: List[Dict[str, Any]], format_type: str = "json") -> Union[str, List[Dict[str, Any]]]:
        """
        Format table data for different output formats.
        
        Args:
            data: Table data
            format_type: Output format (json, csv, html)
            
        Returns:
            Formatted data in requested format
        """
        try:
            if format_type.lower() == "json":
                return ResponseFormatter._format_data(data)
            
            elif format_type.lower() == "csv":
                return DataFormatter._to_csv(data)
            
            elif format_type.lower() == "html":
                return DataFormatter._to_html_table(data)
            
            else:
                logger.warning(f"Unsupported format type: {format_type}")
                return data
                
        except Exception as e:
            logger.error(f"Table data formatting failed: {e}")
            return data
    
    @staticmethod
    def _to_csv(data: List[Dict[str, Any]]) -> str:
        """Convert data to CSV format."""
        try:
            if not data:
                return ""
            
            # Get headers from first row
            headers = list(data[0].keys())
              # Create CSV content
            csv_lines = [",".join(headers)]
            
            for row in data:
                csv_row = []
                for header in headers:
                    value = row.get(header, "")
                    # Escape commas and quotes
                    if isinstance(value, str) and ("," in value or '"' in value):
                        value = f'"{value.replace(chr(34), chr(34)+chr(34))}"'
                    csv_row.append(str(value))
                csv_lines.append(",".join(csv_row))
            
            return "\n".join(csv_lines)
            
        except Exception as e:
            logger.error(f"CSV formatting failed: {e}")
            return ""
    
    @staticmethod
    def _to_html_table(data: List[Dict[str, Any]]) -> str:
        """Convert data to HTML table format."""
        try:
            if not data:
                return "<table><tr><td>No data available</td></tr></table>"
            
            # Get headers
            headers = list(data[0].keys())
            
            # Build HTML table
            html_parts = ["<table border='1' style='border-collapse: collapse;'>"]
            
            # Header row
            html_parts.append("<thead><tr>")
            for header in headers:
                html_parts.append(f"<th style='padding: 8px; background-color: #f2f2f2;'>{header}</th>")
            html_parts.append("</tr></thead>")
            
            # Data rows
            html_parts.append("<tbody>")
            for row in data:
                html_parts.append("<tr>")
                for header in headers:
                    value = row.get(header, "")
                    html_parts.append(f"<td style='padding: 8px;'>{value}</td>")
                html_parts.append("</tr>")
            html_parts.append("</tbody>")
            
            html_parts.append("</table>")
            
            return "".join(html_parts)
            
        except Exception as e:
            logger.error(f"HTML table formatting failed: {e}")
            return f"<p>Error formatting table: {str(e)}</p>"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """
        Truncate text to specified length.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add when truncating
            
        Returns:
            Truncated text
        """
        try:
            if not isinstance(text, str):
                text = str(text)
            
            if len(text) <= max_length:
                return text
            
            return text[:max_length - len(suffix)] + suffix
            
        except Exception as e:
            logger.error(f"Text truncation failed: {e}")
            return str(text)[:max_length] if text else ""
    
    @staticmethod
    def format_number(value: Union[int, float, Decimal], decimal_places: int = 2) -> str:
        """
        Format numeric values for display.
        
        Args:
            value: Numeric value
            decimal_places: Number of decimal places
            
        Returns:
            Formatted number string
        """
        try:
            if value is None:
                return "N/A"
            
            if isinstance(value, (int, float, Decimal)):
                if isinstance(value, int):
                    return f"{value:,}"
                else:
                    return f"{value:,.{decimal_places}f}"
            else:
                return str(value)
                
        except Exception as e:
            logger.error(f"Number formatting failed: {e}")
            return str(value)
