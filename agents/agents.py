"""
Consolidated agents module that combines functionality from separate agent scripts.
This module provides three agent functions:
- routing_agent: Routes user requests to appropriate functions/tools
- agent_sql_queries: Processes SQL query-related requests
- agent_product_offerings: Processes product offering-related requests
"""

from pathlib import Path
import sys
import os
import json
import warnings
import mlflow
from mlflow.entities import SpanType

# Add the src directory to the Python path
src_dir = str(Path(__file__).parent.parent)
sys.path.append(src_dir)
print("Adding current directory to sys.path: \n", str(Path(__file__).parent))
# Update import statement to use the new OpenAI API format
from openai import OpenAI
from app.prompts import (
    prompt_agent_router,
    prompt_agent_sql_analysis,
    prompt_agent_final_response,
    prompt_agent_plot,
    prompt_agent_table_router,
    prompt_agent_products
)
from app.tools import tools_definitions
warnings.filterwarnings("ignore")

# Try to load environment variables, but don't crash if module is missing
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
except ImportError:
    print("Warning: python-dotenv not found. Please set OPENAI_API_KEY manually.")

# Get the Keys - now using standard OpenAI
API_KEY = os.environ.get("OPENAI_API_KEY") 
MODEL = os.environ.get("OPENAI_MODEL", "gpt-5-mini")  # Default to gpt-4o if not set

# Create OpenAI client
client = OpenAI(api_key=API_KEY)


def get_agent_table_rag_tool(tool_input):
    """Get the specific tool definition (updated for new OpenAI schema)"""
    tools = tools_definitions()
    for tool in tools:
        # New schema: tool['name'] instead of tool['function']['name']
        if tool.get('name') == tool_input:
            return tool
    return None

@mlflow.trace(span_type=SpanType.AGENT)
def routing_agent(user_request, chat_history):
    """Routes the user request to the appropriate function/tool, using chat history for context."""
    prompt = prompt_agent_router()

    # Build input messages for the new format
    input_messages = [{"role": "system", "content": prompt}]
    input_messages.extend(chat_history)

    # Ensure latest user message is not duplicated
    if not chat_history or chat_history[-1]["role"] != "user" or chat_history[-1]["content"] != user_request:
        input_messages.append({"role": "user", "content": user_request})

    response = client.responses.create(
        model=MODEL,
        tools=tools_definitions(),
        input=input_messages
    )
    return response

@mlflow.trace(span_type=SpanType.AGENT)
def agent_final_response(user_request, chat_history):
    """Generates final response to the user request, using chat history for context."""
    prompt = prompt_agent_final_response()

    # Build input messages
    input_messages = [{"role": "system", "content": prompt}]
    input_messages.extend(chat_history)

    # Ensure latest user message is not duplicated
    if not chat_history or chat_history[-1]["role"] != "user" or chat_history[-1]["content"] != user_request:
        input_messages.append({"role": "user", "content": user_request})

    response = client.responses.create(
        model=MODEL,
        input=input_messages,
    )
    return response.output_text

@mlflow.trace(span_type=SpanType.TOOL)
def agent_sql_analysis(user_query, required_tables):
    """
    Processes SQL query-related requests.
    
    Args:
        user_query: String or JSON-serializable input from the user
        required_tables: List of tables required for the query
        
    Returns:
        str: The generated response text
    """
    prompt = prompt_agent_sql_analysis().format(required_tables=required_tables)
    
    # Accepts any data type: string, dict, list, etc.
    # If not string, convert to JSON string for the LLM
    if not isinstance(user_query, str):
        user_input_serialized = json.dumps(user_query)
    else:
        user_input_serialized = user_query

    response = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input_serialized}
        ],
    )
    return response.output_text

@mlflow.trace(span_type=SpanType.AGENT)
def agent_generate_charts(user_query):
    """Generates chart/visualization code based on user query."""
    prompt = prompt_agent_plot()
    
    response = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_query}
        ]
    )
    return response.output_text

@mlflow.trace(span_type=SpanType.AGENT)
def agent_products(user_query):
    """Generates chart/visualization code based on user query."""
    prompt = prompt_agent_products()
    
    response = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_query}
        ]
    )
    return response.output_text

@mlflow.trace(span_type=SpanType.AGENT)
def agent_table_router(user_query):
    """
    Get the relevant tables using tool calling.
    
    Args:
        user_query: String - the user's question/request
        
    Returns:
        response: OpenAI response object with tool calls
    """
    tool_table_rag = get_agent_table_rag_tool('agent_table_rag')
    
    response = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": prompt_agent_table_router()},
            {"role": "user", "content": user_query}
        ],
        tools=[tool_table_rag],  # get only the table RAG tool
    )
    return response

# simple usage
if __name__ == "__main__":
    user_query = "What is the total transaction volume for each month?"
    required_tables = ["transaction_history"]
    
    # Test routing agent
    response = routing_agent(user_query, [])
    print("Routing Agent Response:")
    print(f"  Output text: {response.output_text}")
    print(f"  Has tool calls: {len([item for item in response.output if hasattr(item, 'type') and item.type == 'function_call']) > 0}")
    
    # Test SQL analysis agent
    sql_response = agent_sql_analysis(user_query, required_tables)
    print("\nSQL Analysis Response:", sql_response)
    
    # Test final response agent
    final_response = agent_final_response(user_query, [])
    print("\nFinal Response:", final_response)
    
    # Test chart generation
    chart_code = agent_generate_charts(user_query)
    print("\nChart Generation Code:", chart_code)
    
    # Test table router
    table_response = agent_table_router(user_query)
    print("\nTable Router Response:")
    print(f"  Output text: {table_response.output_text}")
