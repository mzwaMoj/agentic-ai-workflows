
from pathlib import Path
import sys
src_dir = str(Path(__file__).parent.parent)
if src_dir not in sys.path:
    sys.path.append(src_dir)

import json
import logging
import re
from IPython.display import display
import json
import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext

import mlflow
mlflow.openai.autolog()
from utils.mlflow_logger import (
        start_chat_run, 
        log_router_response, 
        log_sql_code, 
        log_sql_results,
        log_table_retriever_response,
        log_generated_chart_results,
        log_required_tables,
        log_polish_prompt,
        log_sql_analysis_error,
        log_final_response, 
        end_chat_run
)
# Now import the modules from rag-compliance
try:
    # Import prompts
    from prompts.prompt_agent_router import prompt_agent_router
    from prompts.prompt_agent_sql_analysis import prompt_agent_sql_analysis
    from prompts.prompt_agent_plot import prompt_agent_plot
    from prompts.prompt_agent_plot import prompt_agent_plot

    from tools.tools import tools_definitions
    from utils.generate_charts import execute_plot_code
    from agents.agents import (routing_agent,  
                               agent_sql_analysis, 
                               agent_generate_charts,
                               agent_table_router,
                               agent_final_response
    )
    print("Successfully imported modules from rag-compliance directory")
except ImportError as e:
    print(f"Error importing modules: {e}")

try:
    from app.db import connect_to_sql_server
    from app.db.sql_query_executor import execute_sql_with_pyodbc
    print("Successfully imported")
except ImportError as e:
    print(f"Error importing: {e}")
    print("Ensure the file/s is in the parent directory of your current script.")
    sys.exit(1)

logger = logging.getLogger(__name__)

from openai import AzureOpenAI
import os
from dotenv import load_dotenv, find_dotenv
import warnings
warnings.filterwarnings("ignore")
load_dotenv(find_dotenv())


import ssl
import urllib3
import httpx

# Disable SSL certificate verification globally (for development only!)
ssl._create_default_https_context = ssl._create_unverified_context

# # For requests and urllib3, suppress warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Create httpx client with SSL verification disabled
http_client = httpx.Client(verify=False)

import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI

API_KEY = os.environ.get("AZURE_OPENAI_KEY") 
API_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
API_VERSION = os.environ.get("AZURE_OPENAI_VERSION")
MODEL = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")


# set up an LLM
llm = AzureOpenAI(
  default_headers={"Ocp-Apim-Subscription-Key": API_KEY},
  api_key=API_KEY,
  azure_endpoint=API_ENDPOINT,
  azure_deployment= AZURE_DEPLOYMENT,
  api_version=API_VERSION, 
  model = AZURE_DEPLOYMENT,
  http_client=http_client
)

embeddings_endpoint = os.environ.get("AZURE_OPENAI_EMBEDDING_ENDPOINT")
embeddings_api_subscription_key = os.environ.get("AZURE_OPENAI_EMBEDDING_KEY")
embeddings_model_name = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
embeddings_deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
embeddings_api_version = os.environ.get("AZURE_OPENAI_EMBEDDING_API_VERSION")

# Set up embedding model
embedding_model = AzureOpenAIEmbedding(
    deployment_name=embeddings_deployment,
    api_key=embeddings_api_subscription_key,
    azure_endpoint=embeddings_endpoint,
    api_version=embeddings_api_version,
    http_client=http_client
)

Settings.llm = llm
Settings.embed_model = embedding_model



# initialize client
index_path = r"C:\Users\A238737\OneDrive - Standard Bank\Documents\GroupFunctions\rag-systems\ai-analyst-demo\text_sql_analysis\index\chroma_db"
db = chromadb.PersistentClient(path=index_path)

# get collection
chroma_collection = db.get_or_create_collection("sql_tables_metadata")

# assign chroma as the vector_store to the context
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# load your index from stored vectors
index = VectorStoreIndex.from_vector_store(
    vector_store, storage_context=storage_context
)

# create a query engine
query_engine = index.as_query_engine(similarity_top_k=10)

def agent_table_rag(query):
    return query_engine.query("retrieve the full tables metadata without intepreting or editing anything for the following given tables: " + query)

def agent_table_retriever(user_request):
    """
    This function identifies the most relevant database tables based on the user's request.
    It uses the provided user_request to determine which tables are needed to answer the query.
    
    Args:
        user_request (str): The user's natural language query.
        
    Returns:
        list: A list of table names that are relevant to the user request.
    """
    response = agent_table_router(user_request)
    
    tool_call = response.choices[0].message.tool_calls[0]
    if tool_call.function.name == "agent_table_rag":
        args = json.loads(tool_call.function.arguments)
        table_results = agent_table_rag( str(args.get("relevant_tables")))
    else:
        raise ValueError("Unexpected tool call name: {}".format(tool_call.function.name))
    
    return table_results.response



def ai_chatbot(user_input, chat_history):
    if not chat_history or chat_history[-1]["role"] != "user" or chat_history[-1]["content"] != user_input:
        chat_history.append({"role": "user", "content": user_input})

    start_chat_run(user_input)

    try:
        response = routing_agent(user_input, chat_history)
        message = response.choices[0].message
        log_router_response(message)

        chart_html = None  # Will hold the chart HTML if generated

        if hasattr(message, 'tool_calls') and message.tool_calls:
            print(f"\nProcessing {len(message.tool_calls)} tool call(s)")
            sql_results = []
            chart_results = []
            unknown_functions = []

            for i, tool_call in enumerate(message.tool_calls):
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                print(f"\nTool Call {i+1}:")
                print(f"Function Name: {function_name}")
                print(f"Function Arguments: {function_args}")

                if function_name == "agent_sql_analysis":
                    # Modified: capture chart_html if generated
                    sql_results, chart_html = handle_sql_analysis(user_input, function_args)
                    print("sql_results:\n", sql_results)
                else:
                    unknown_functions.append(function_name)
                    print(f"Warning: Unknown function '{function_name}' encountered")

            # ...existing polish prompt and response logic...
            polish_prompt = build_polish_prompt(sql_results, chart_results, user_input)
            log_polish_prompt(polish_prompt)
            if polish_prompt:
                polish_chat_history = [{"role": "user", "content": polish_prompt}]
                polish_response = agent_final_response(polish_prompt, polish_chat_history)
                if polish_response:
                    final_message = polish_response
                    log_final_response(final_message)
                    # If a chart was generated, store both text and chart in chat_history
                    if chart_html is not None:
                        chat_history.append({
                            "role": "assistant",
                            "content": {
                                "text": final_message,
                                "chart_html": chart_html
                            }
                        })
                    else:
                        chat_history.append({"role": "assistant", "content": final_message})
                else:
                    fallback_message = create_fallback_message(sql_results, chart_results)
                    chat_history.append({"role": "assistant", "content": fallback_message})
                    log_final_response(fallback_message)
            else:
                assistant_msg = "I couldn't process your request. Please try again."
                chat_history.append({"role": "assistant", "content": assistant_msg})
                return chat_history
        else:
            content = message.content or "I don't have a response for that."
            log_final_response(content)
            chat_history.append({"role": "assistant", "content": content})

    finally:
        end_chat_run()

    return chat_history

def handle_sql_analysis(user_input, function_args):
    chart_html = None
    try:
        required_tables = agent_table_retriever(user_input)
        log_table_retriever_response(required_tables)
        sql_code = agent_sql_analysis(user_input, required_tables)
        log_sql_code(sql_code)
        sql_results = execute_sql_with_pyodbc(sql_code, auth_type='windows')
        log_sql_results(sql_results)

        processed_results = []
        for res in sql_results:
            if isinstance(res, dict) and res.get("status") == "success":
                try:
                    if isinstance(res["result"], str):
                        json_data = json.loads(res["result"])
                    else:
                        json_data = "[Chart visual generated]" if "HTML" in str(type(res["result"])) else str(res["result"])
                    processed_results.append({
                        "type": "sql_success",
                        "query_info": f"Query returned {res['row_count']} rows with columns: {', '.join(res['columns'])}",
                        "data": json_data,
                        "user_request": function_args.get("user_requests", user_input)
                    })
                except (json.JSONDecodeError, TypeError):
                    processed_results.append({
                        "type": "sql_success",
                        "query_info": f"Query returned {res['row_count']} rows",
                        "data": str(res["result"]),
                        "user_request": function_args.get("user_requests", user_input)
                    })
            else:
                processed_results.append({
                    "type": "sql_error",
                    "query_info": f"Query failed with status: {res.get('status', 'unknown')}",
                    "data": res.get("result", "No data available"),
                    "user_request": function_args.get("user_requests", user_input)
                })
        # --- Generate chart visual if user request is for a chart ---
        chart_keywords = ["chart", "graph", "plot", "visual", "pie", "bar", "line"]
        if any(kw in user_input.lower() for kw in chart_keywords):
            chart_code = agent_generate_charts("User Query: " + user_input + f"\nHere is the data: \n {sql_results}")
            chart_html = execute_plot_code(chart_code)
            # If chart_html is empty or error, replace with a message
            if hasattr(chart_html, 'data') and not chart_html.data:
                chart_html = None
            elif hasattr(chart_html, 'data') and "Error" in chart_html.data:
                chart_html = chart_html  # Will display error message in chat
            log_generated_chart_results("[Chart visual generated]")

        return processed_results, chart_html
    except Exception as e:
        print(f"Error in SQL analysis: {e}")
        log_sql_analysis_error(f"Error in SQL analysis: {e}")
        return ([{
            "type": "sql_error", 
            "query_info": f"SQL analysis failed: {str(e)}", 
            "data": None,
            "user_request": function_args.get("user_requests", user_input)
        }], None)
    
    
def build_polish_prompt(sql_results, chart_results, user_input):
    if not sql_results and not chart_results:
        return None
    
    prompt_parts = [f"User Query: '{user_input}'\n"]
    
    successful_sql = [r for r in sql_results if r["type"] == "sql_success"]
    failed_sql = [r for r in sql_results if r["type"] == "sql_error"]
    
    if successful_sql:
        prompt_parts.append("SQL Query Results:")
        for result in successful_sql:
            prompt_parts.append(f"- {result['query_info']}")
            prompt_parts.append(f"  Data: {result['data']}")
    
    if failed_sql:
        prompt_parts.append("SQL Query Errors:")
        for result in failed_sql:
            prompt_parts.append(f"- {result['query_info']}")
    
    successful_charts = [r for r in chart_results if r["type"] == "chart_success"]
    failed_charts = [r for r in chart_results if r["type"] == "chart_error"]
    
    if successful_charts:
        prompt_parts.append("Chart Generation Results:")
        for result in successful_charts:
            prompt_parts.append(f"- Successfully generated chart for: {result['user_request']}")
    
    if failed_charts:
        prompt_parts.append("Chart Generation Errors:")
        for result in failed_charts:
            prompt_parts.append(f"- Failed to generate chart: {result['error']}")
    
    prompt_parts.append("\nPlease provide a clear, friendly summary of these results.")
    
    return "\n".join(prompt_parts)


def create_fallback_message(sql_results, chart_results):
    message_parts = ["I've analyzed your request but encountered an issue formatting the results."]
    
    if sql_results:
        successful_count = len([r for r in sql_results if r["type"] == "sql_success"])
        message_parts.append(f"Successfully executed {successful_count} SQL queries.")
    
    if chart_results:
        successful_charts = len([r for r in chart_results if r["type"] == "chart_success"])
        message_parts.append(f"Successfully generated {successful_charts} charts.")
    
    return " ".join(message_parts)


# Simple chatbot ui in  the notebok:
from IPython.display import clear_output, display, Markdown
import sys

chat_history = []

def inline_input(prompt=""):
    """Custom input function that displays inline in Jupyter notebook"""
    print(prompt, end='')
    sys.stdout.flush()
    return input()

def display_chat(chat_history):
    """Nicely formats and displays the full chat history, including charts if present."""
    clear_output(wait=True)
    for msg in chat_history:
        role = msg["role"]
        content = msg["content"]
        # If the assistant's message contains a chart visual, display it as HTML
        if role == "user":
            display(Markdown(f"👤 **You:** {content}"))
        elif role == "assistant":
            # Check for chart visual (stored as a tuple or dict with 'chart_html')
            if isinstance(content, dict) and "chart_html" in content:
                display(Markdown(f"🤖 **Assistant:** {content.get('text', '')}"))
                display(content["chart_html"])
            else:
                display(Markdown(f"🤖 **Assistant:** {content}"))

# Main loop
while True:
    display_chat(chat_history)
    user_input = inline_input("👤 You: ")
    
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting chat.")
        break

    # Process input and update chat history
    chat_history = ai_chatbot(user_input, chat_history)
    
    # Display updated chat after processing response
    display_chat(chat_history)