"""
Chart generator for managing chart creation and execution.
"""

import logging
from typing import Optional, Dict, Any
from app.agents.chart_agent import ChartAgent

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Service for generating and managing chart visualizations."""
    
    def __init__(self, chart_agent: ChartAgent):
        self.chart_agent = chart_agent
        
    async def generate_chart(self, user_query: str, data: Any) -> Optional[str]:
        """
        Generate a chart based on user request and data.
        
        Args:
            user_query: User's request for visualization
            data: Data to be visualized
            
        Returns:
            HTML string of the generated chart, or None if failed
        """
        try:
            # Check if chart is actually requested
            if not self.chart_agent.validate_chart_request(user_query):
                logger.info("No chart requested in user query")
                return None
                
            # Generate chart code
            chart_code = await self.chart_agent.generate_chart_code(user_query, str(data))
            
            if not chart_code:
                logger.warning("No chart code generated")
                return None
                
            # Execute chart code to generate HTML
            chart_html = await self.chart_agent.execute_chart_code(chart_code)
            
            if chart_html and "Error" not in chart_html:
                logger.info("Chart generated successfully")
                return chart_html
            else:
                logger.warning("Chart generation failed or returned error")
                return None
                
        except Exception as e:
            logger.error(f"Chart generation failed: {e}")
            return None
            
    async def suggest_visualization(self, data_description: str) -> str:
        """
        Suggest appropriate visualization type for given data.
        
        Args:
            data_description: Description of the data structure
            
        Returns:
            Suggestion for visualization type
        """
        try:
            suggestion = await self.chart_agent.suggest_chart_type(data_description)
            logger.info("Visualization suggestion generated")
            return suggestion
            
        except Exception as e:
            logger.error(f"Failed to generate visualization suggestion: {e}")
            return "Consider using a bar chart or table view for your data."
            
    def analyze_data_for_visualization(self, data: Any) -> Dict[str, Any]:
        """
        Analyze data structure to determine best visualization approach.
        
        Args:
            data: Data to analyze
            
        Returns:
            Analysis results with recommendations
        """
        try:
            analysis = {
                "data_type": "unknown",
                "row_count": 0,
                "column_count": 0,
                "has_numeric_data": False,
                "has_categorical_data": False,
                "recommended_charts": []
            }
            
            if isinstance(data, list):
                analysis["row_count"] = len(data)
                
                if len(data) > 0 and isinstance(data[0], dict):
                    # Data is list of dictionaries
                    analysis["data_type"] = "tabular"
                    analysis["column_count"] = len(data[0].keys())
                    
                    # Analyze column types
                    sample_row = data[0]
                    for key, value in sample_row.items():
                        if isinstance(value, (int, float)):
                            analysis["has_numeric_data"] = True
                        elif isinstance(value, str):
                            analysis["has_categorical_data"] = True
                            
                    # Recommend chart types based on data structure
                    if analysis["has_numeric_data"] and analysis["has_categorical_data"]:
                        analysis["recommended_charts"] = ["bar", "column", "pie"]
                    elif analysis["has_numeric_data"]:
                        analysis["recommended_charts"] = ["line", "histogram", "scatter"]
                    else:
                        analysis["recommended_charts"] = ["bar", "pie"]
                        
            elif isinstance(data, dict):
                analysis["data_type"] = "key_value"
                analysis["column_count"] = len(data.keys())
                analysis["recommended_charts"] = ["bar", "pie"]
                
            logger.debug(f"Data analysis completed: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"Data analysis for visualization failed: {e}")
            return {
                "data_type": "unknown",
                "error": str(e),
                "recommended_charts": ["table"]
            }
            
    def format_data_for_chart(self, data: Any, chart_type: str = "auto") -> Dict[str, Any]:
        """
        Format data appropriately for chart generation.
        
        Args:
            data: Raw data to format
            chart_type: Type of chart to format for
            
        Returns:
            Formatted data structure
        """
        try:
            formatted = {
                "original_data": data,
                "chart_data": None,
                "labels": [],
                "values": []
            }
            
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict):
                    # Extract labels and values for common chart types
                    keys = list(data[0].keys())
                    
                    if len(keys) >= 2:
                        # Use first column as labels, second as values
                        label_key = keys[0]
                        value_key = keys[1]
                        
                        formatted["labels"] = [str(row.get(label_key, "")) for row in data]
                        formatted["values"] = [row.get(value_key, 0) for row in data]
                        
                formatted["chart_data"] = data
                
            logger.debug(f"Data formatted for chart type: {chart_type}")
            return formatted
            
        except Exception as e:
            logger.error(f"Data formatting for chart failed: {e}")
            return {
                "original_data": data,
                "chart_data": data,
                "error": str(e)
            }
