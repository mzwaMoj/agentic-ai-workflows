# from openai import AzureOpenAI
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
import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.query_engine import RetrieverQueryEngine
import logging
import sys
API_KEY = os.environ.get("AZURE_OPENAI_KEY") 
API_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
API_VERSION = os.environ.get("AZURE_OPENAI_VERSION")
MODEL = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")

client = AzureOpenAI(
  default_headers={"Ocp-Apim-Subscription-Key": API_KEY},
  api_key=API_KEY,
  azure_endpoint=API_ENDPOINT,
  azure_deployment= AZURE_DEPLOYMENT,
  api_version=API_VERSION, 
  model = AZURE_DEPLOYMENT,
  http_client=http_client
)

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
# Embeddings Model
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

# Define file-specific metadata for initialization (uncommented to make it work)
doc_transactions_path = r"C:\Users\A238737\OneDrive - Standard Bank\Documents\GroupFunctions\rag-systems\ai-analyst-demo\text_sql_analysis\table_metadata\metadata_transaction_history.txt"
# doc_customer_info_path = r"C:\Users\A238737\OneDrive - Standard Bank\Documents\GroupFunctions\rag-systems\ai-analyst-demo\text_sql_analysis\table_metadata\metadata_customer_information.txt"
# doc_crs_accountreport_path = r"C:\Users\A238737\OneDrive - Standard Bank\Documents\GroupFunctions\rag-systems\ai-analyst-demo\text_sql_analysis\table_metadata\metadata_crs.txt"
# doc_crs_countrycode_path = r"C:\Users\A238737\OneDrive - Standard Bank\Documents\GroupFunctions\rag-systems\ai-analyst-demo\text_sql_analysis\table_metadata\metadata_crs.txt"
# doc_crs_messagespec_path = r"C:\Users\A238737\OneDrive - Standard Bank\Documents\GroupFunctions\rag-systems\ai-analyst-demo\text_sql_analysis\table_metadata\metadata_crs.txt"

file_paths = [doc_transactions_path, 
            # doc_customer_info_path, 
            # doc_crs_accountreport_path, 
            # doc_crs_countrycode_path, 
            # doc_crs_messagespec_path
            ]

def get_metadata_for_files(file_paths):
    # Create a map of file path to custom metadata
    file_metadata_map = {
        
        doc_transactions_path: {
            "category": "transaction history table",
            "year": "2025-07-20",
            "department": "Finance", 
            "author": "Mzwandile Mhlongo",
            "confidentiality": "high",
            "description": "Comprehensive transaction history table containing all customer financial transactions including deposits, withdrawals, transfers, payments, and purchases"
        },
        # doc_customer_info_path: {
        #     "category": "customer information table",
        #     "year": "2025-07-20",
        #     "department": "Finance", 
        #     "author": "Mzwandile Mhlongo",
        #     "confidentiality": "high",
        #     "description": "Comprehensive customer information data table containing personal information, financial details, loan information, and product holdings for bank customers"
        # },
        # doc_crs_accountreport_path: {
        #     "category": "Common Reporting Standard (CRS) Account Reporting",
        #     "year": "2025-07-20",
        #     "department": "Finance",
        #     "author": "Mzwandile Mhlongo",
        #     "confidentiality": "low",
        #     "description": "Detailed financial account reporting data in accordance with **Common Reporting Standard (CRS)** requirements. This table captures comprehensive information about account holders and their financial accounts, crucial for international tax transparency"
        # },
        # doc_crs_countrycode_path: {
        #     "category": "Common Reporting Standard (CRS) Country Codes",
        #     "year": "2025-07-20",
        #     "department": "Finance",
        #     "author": "Mzwandile Mhlongo",
        #     "confidentiality": "low",
        #     "description": "Comprehensive country code reference for **Common Reporting Standard (CRS)** reporting. This table provides essential mappings between various country code formats, ensuring accurate and consistent country identification across CRS data. It is based on the **ISO 3166-1 alpha-2 standard"
        # },
        # doc_crs_messagespec_path: {
        #     "category": "Common Reporting Standard (CRS) Message Specification",
        #     "year": "2025-07-20",
        #     "department": "Finance",
        #     "author": "Mzwandile Mhlongo",
        #     "confidentiality": "low",
        #     "description": "This table stores the crucial **header and reporting entity information** for **Common Reporting Standard (CRS) messages"
        # },
    }
    
    # The function that SimpleDirectoryReader will call
    def file_metadata_func(file_path):
        # Get predefined metadata if available, otherwise return basic metadata
        if file_path in file_metadata_map:
            return file_metadata_map[file_path]
        else:
            return {
                "source": file_path,
                "file_type": os.path.splitext(file_path)[1],
                "confidentiality": "unknown"
            }
    
    return file_metadata_func

# Create reader with specific files and their metadata
documents = SimpleDirectoryReader(
    input_files=file_paths,
    file_metadata=get_metadata_for_files(file_paths)
).load_data()

# Create index and query engine as before (this initializes Settings properly)
index = VectorStoreIndex.from_documents(documents)
print("✓ Settings initialized successfully via document indexing")

# Verify Settings are properly configured
print("✓ LLM configured:", Settings.llm is not None)
print("✓ Embedding model configured:", Settings.embed_model is not None)

# Test embedding model is working
try:
    test_embedding = Settings.embed_model.get_text_embedding("test")
    print(f"✓ Embedding model working, dimensions: {len(test_embedding)}")
except Exception as e:
    print(f"✗ Embedding model test failed: {e}")

print("\n" + "="*50)
print("INITIALIZATION COMPLETE - Now querying ChromaDB...")
print("="*50 + "\n")

# Query From Local Index
import chromadb
import sys
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext  # Added Settings import
                                
# initialize client
index_path = r"C:\Users\A238737\OneDrive - Standard Bank\Documents\GroupFunctions\rag-systems\ai-analyst-demo\text_sql_analysis\index\chroma_db"
db = chromadb.PersistentClient(path=index_path)

# get collection
chroma_collection = db.get_or_create_collection("sql_tables_metadata")

# assign chroma as the vector_store to the context
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# load your index from stored vectors
index_local = VectorStoreIndex.from_vector_store(
                                            vector_store = vector_store, 
                                            storage_context=storage_context
                                        )

# create a query engine
local_query_engine = index_local.as_query_engine(similarity_top_k=10)

def generate_response(query):
    answer = local_query_engine.query(query)
    print("\n**Query:**\n", query)
    print("\n**Answer:**\n", answer)
    print("\n**Source:**\n", answer.get_formatted_sources())
    
    # Optionally print metadata from sources to verify it's working
    print("\n**Source Metadata:**")
    for source_node in answer.source_nodes:
        print(f"- {source_node.node.metadata}")

if __name__ == "__main__":

    output = generate_response("generate the full table details without intepreting or editing anything: customer information full table details")
    print(output)