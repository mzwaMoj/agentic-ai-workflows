"""
Chart agent for generating visualizations from data.
"""

import logging
from typing import Optional
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class ChartAgent:
    """Agent responsible for generating chart/visualization code."""
    
    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service
        
    async def generate_chart_code(self, user_query: str, data: str) -> str:
        """
        Generate Python code for creating charts/visualizations.
        
        Args:
            user_query: User's request for visualization
            data: Data to be visualized (SQL results)
              Returns:
            Python code for generating the chart
        """
        try:
            # Import prompt from app module
            from app.prompts import prompt_agent_plot
            
            # Prepare the prompt with user query and data
            full_prompt = f"{prompt_agent_plot}\n\nUser Query: {user_query}\n\nData to visualize:\n{data}"
            
            messages = [{"role": "user", "content": full_prompt}]
            
            # Call OpenAI for chart code generation
            response = await self.openai_service.chat_completion(
                messages=messages,
                temperature=0.1
            )
            
            chart_code = response.choices[0].message.content
            
            logger.info(f"Chart agent generated code for: {user_query[:50]}...")
            logger.debug(f"Generated chart code: {chart_code[:100]}...")
            
            return chart_code
            
        except Exception as e:
            logger.error(f"Chart agent failed to generate code: {e}")
            raise
            
    async def execute_chart_code(self, chart_code: str) -> str:
        """
        Execute the chart generation code and return HTML.
        
        Args:
            chart_code: Python code for generating chart
            
        Returns:
            HTML representation of the chart
        """
        try:
            # Import chart execution utility
            from utils.generate_charts import execute_plot_code
            
            chart_html = execute_plot_code(chart_code)
            
            # Handle different return types
            if hasattr(chart_html, 'data'):
                if chart_html.data and "Error" not in chart_html.data:
                    logger.info("Chart executed successfully")
                    return chart_html.data
                else:
                    logger.warning("Chart execution returned error or empty data")
                    return "<p>Chart generation failed or returned empty data</p>"
            else:
                logger.info("Chart executed successfully")
                return str(chart_html) if chart_html else "<p>No chart generated</p>"
                
        except Exception as e:
            logger.error(f"Chart execution failed: {e}")
            return f"<p>Chart generation failed: {str(e)}</p>"
            
    def validate_chart_request(self, user_query: str) -> bool:
        """
        Check if the user query is requesting a chart/visualization.
        
        Args:
            user_query: User's natural language query
            
        Returns:
            True if chart is requested, False otherwise
        """
        chart_keywords = ["chart", "graph", "plot", "visual", "pie", "bar", "line", "histogram", "scatter"]
        query_lower = user_query.lower()
        
        return any(keyword in query_lower for keyword in chart_keywords)
        
    async def suggest_chart_type(self, data_description: str) -> str:
        """
        Suggest appropriate chart type based on data description.
        
        Args:
            data_description: Description of the data structure
            
        Returns:
            Suggested chart type and reasoning
        """
        try:
            suggestion_prompt = f"""
            Based on the following data description, suggest the most appropriate chart type
            and provide reasoning for your choice.
            
            Data description: {data_description}
            
            Consider: bar charts for categories, line charts for trends over time, 
            pie charts for proportions, scatter plots for relationships, etc.
            """
            
            messages = [{"role": "user", "content": suggestion_prompt}]
            
            response = await self.openai_service.chat_completion(
                messages=messages,
                temperature=0.1
            )
            
            suggestion = response.choices[0].message.content
            
            logger.info("Chart type suggestion generated")
            return suggestion
            
        except Exception as e:
            logger.error(f"Failed to generate chart suggestion: {e}")
            return "Unable to suggest chart type. A bar chart is usually a safe default."
