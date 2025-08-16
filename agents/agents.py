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
from openai import AzureOpenAI
from app.prompts import (
    prompt_agent_router,
    prompt_agent_sql_analysis,
    prompt_agent_final_response,
    prompt_agent_plot,
    prompt_agent_table_router
)
from app.tools import tools_definitions
warnings.filterwarnings("ignore")
import ssl
import urllib3
import httpx

# Disable SSL certificate verification globally (for development only!)
ssl._create_default_https_context = ssl._create_unverified_context
# For requests and urllib3, suppress warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Try to load environment variables, but don't crash if module is missing
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
except ImportError:
    print("Warning: python-dotenv not found. Please set OPENAI_API_KEY manually.")
# Get the Keys
API_KEY = os.environ.get("AZURE_OPENAI_KEY") 
API_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
API_VERSION = os.environ.get("AZURE_OPENAI_VERSION")
MODEL = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")

# On windows
# Create httpx client with SSL verification disabled
http_client = httpx.Client(verify=False)

# Create client with custom http_client
client = AzureOpenAI(
    api_key=API_KEY,
    azure_endpoint=API_ENDPOINT,
    api_version=API_VERSION,
    http_client=http_client
)


def get_agent_table_rag_tool(tool_input):
    """ Get the specific tool definition"""
    tools = tools_definitions()
    for tool in tools:
        if tool.get('function', {}).get('name') == tool_input:
            return tool
    return None

@mlflow.trace(span_type=SpanType.AGENT)
def routing_agent(user_request, chat_history):
    """Routes the user request to the appropriate function/tool, using chat history for context."""
    prompt = prompt_agent_router()

    messages = [{"role": "system", "content": prompt}]
    messages.extend(chat_history)

    # Ensure latest user message is not duplicated
    if not chat_history or chat_history[-1]["role"] != "user" or chat_history[-1]["content"] != user_request:
        messages.append({"role": "user", "content": user_request})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools_definitions(),
        tool_choice="auto"
    )
    return response

@mlflow.trace(span_type=SpanType.AGENT)
def agent_final_response(user_request, chat_history):
    """Routes the user request to the appropriate function/tool, using chat history for context."""
    prompt = prompt_agent_final_response()

    messages = [{"role": "system", "content": prompt}]
    messages.extend(chat_history)

    # Ensure latest user message is not duplicated
    if not chat_history or chat_history[-1]["role"] != "user" or chat_history[-1]["content"] != user_request:
        messages.append({"role": "user", "content": user_request})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    return response.choices[0].message.content

@mlflow.trace(span_type=SpanType.TOOL)
def agent_sql_analysis(user_query, required_tables):
    """
    Processes SQL query-related requests.
    
    Args:
        user_input: String or JSON-serializable input from the user
        
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

    completions = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input_serialized}
        ],
    )
    return completions.choices[0].message.content

@mlflow.trace(span_type=SpanType.AGENT)
def agent_generate_charts(user_query):
    prompt =  prompt_agent_plot()
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_query}
        ])
    code = response.choices[0].message.content
    return code

@mlflow.trace(span_type=SpanType.AGENT)
def agent_table_router(user_query):
    """
    Get the relevant tables.
    
    Args:
        user_input: String
        
    Returns:
        args: "relevant_tables":["transaction_history"]
    """
    tool_table_rag = get_agent_table_rag_tool('agent_table_rag')
    completions = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": prompt_agent_table_router()},
            {"role": "user", "content": user_query}
        ],
        tools= [tool_table_rag], # get only the 
        tool_choice="required",
    )
    return completions

# simple usage
if __name__ == "__main__":
    user_query = "What is the total transaction volume for each month?"
    required_tables = ["transaction_history"]
    
    # Test routing agent
    response = routing_agent(user_query, [])
    print("Routing Agent Response:", response.choices[0].message)
    
    # Test SQL analysis agent
    sql_response = agent_sql_analysis(user_query, required_tables)
    print("SQL Analysis Response:", sql_response)
    
    # Test final response agent
    final_response = agent_final_response(user_query, [])
    print("Final Response:", final_response)
    
    # Test chart generation
    chart_code = agent_generate_charts(user_query)
    print("Chart Generation Code:", chart_code)