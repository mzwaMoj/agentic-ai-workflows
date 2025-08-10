from pathlib import Path
import sys
src_dir = str(Path(__file__).parent.parent)
if src_dir not in sys.path:
    sys.path.append(src_dir)

import json
import logging
import re
import json

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

# # For requests and urllib3, suppress warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Create httpx client with SSL verification disabled
http_client = httpx.Client(verify=False)

import chromadb
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
# Note: get_or_create_collection will create the collection if it doesn't exist.
# For checking existence without creation, use db.get_collection() with a try-except.
chroma_collection = db.get_or_create_collection("sql_tables_metadata")
print(f"Chroma collection '{chroma_collection.name}' loaded successfully.")
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

def check_and_display_collection_info(client_db, collection_name_to_check):
    """
    Checks if a ChromaDB collection exists and displays its content if it does.
    Also lists all available collections.
    """
    print("\n--- ChromaDB Collection Information ---")

    # 1. List all collections
    print("Listing all collections:")
    all_collections = client_db.list_collections()
    if all_collections:
        for col in all_collections:
            print(f"- {col.name}")
    else:
        print("No collections found in the database.")

    # 2. Check if the specified collection exists
    print(f"\nChecking if collection '{collection_name_to_check}' exists...")
    try:
        target_collection = client_db.get_collection(collection_name_to_check)
        print(f"Collection '{collection_name_to_check}' exists!")

        # 3. Get and display some content from the index
        print(f"\nDisplaying first 5 items from '{collection_name_to_check}':")
        # Use peek() to get a small sample of the collection's contents
        # It returns a dictionary with 'ids', 'embeddings', 'metadatas', 'documents'
        # We are primarily interested in 'documents' and 'metadatas' for content.
        collection_content = target_collection.peek(limit=5)

        if collection_content and collection_content.get('documents'):
            for i, doc in enumerate(collection_content['documents']):
                print(f"--- Item {i+1} ---")
                print(f"ID: {collection_content['ids'][i]}")
                print(f"Document: {doc}")
                if collection_content.get('metadatas') and collection_content['metadatas'][i]:
                    print(f"Metadata: {json.dumps(collection_content['metadatas'][i], indent=2)}")
                print("-" * 20)
        else:
            print(f"Collection '{collection_name_to_check}' is empty or has no documents.")

    except chromadb.exceptions.CollectionNotFoundError:
        print(f"Collection '{collection_name_to_check}' does NOT exist.")
    except Exception as e:
        print(f"An error occurred while accessing collection '{collection_name_to_check}': {e}")
    print("-------------------------------------")


if __name__ == "__main__":
    # Call the new function to check and display collection info
    check_and_display_collection_info(db, "sql_tables_metadata")
    # check_and_display_collection_info(db, "non_existent_collection") # Example for a non-existent collection

    user_request = "customer information"
    try:
        print("\nRetrieving relevant tables for the request:", user_request)
        # table_results = agent_table_rag(user_request)
        table_results = query_engine.query("retrieve the full tables metadata without intepreting or editing anything for the following given tables: " + user_request)
        print("Type of result:", type(table_results))
        print("Raw result:", repr(table_results))
        if not table_results:
            print("No results returned from query.")
        else:
            # If it's not a string, print its attributes
            if not isinstance(table_results, str):
                print("Result attributes:", dir(table_results))
                # Try to print a 'response' or 'text' attribute if present
                if hasattr(table_results, 'response'):
                    print("Response attribute:", table_results.response)
                if hasattr(table_results, 'text'):
                    print("Text attribute:", table_results.text)
            print("Relevant tables retrieved successfully!")
            print(table_results)
    except Exception as e:
        print(f"Error retrieving tables: {e}")

