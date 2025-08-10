"""
Prompts module - centralized access to all agent prompts.
"""

from .prompt_agent_router import prompt_agent_router
from .prompt_agent_sql_analysis import prompt_agent_sql_analysis
from .prompt_agent_final_response import prompt_agent_final_response
from .prompt_agent_plot import prompt_agent_plot
from .prompt_agent_table_router import prompt_agent_table_router

__all__ = [
    'prompt_agent_router',
    'prompt_agent_sql_analysis', 
    'prompt_agent_final_response',
    'prompt_agent_plot',
    'prompt_agent_table_router'
]