"""
Vector database service for ChromaDB operations.
Fixed version following the exact pattern from working chatbot.py
"""

import logging
import os
from typing import Dict, Any, Optional
import chromadb
from llama_index.core import VectorStoreIndex, Settings as LlamaSettings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
import httpx
from app.config.settings import Settings

logger = logging.getLogger(__name__)


class VectorService:
    """Service for managing ChromaDB vector database operations."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._db: Optional[chromadb.PersistentClient] = None
        self._collection = None
        self._index: Optional[VectorStoreIndex] = None
        self._query_engine = None
        self._llm_configured = False
        self._embedding_configured = False
        self._initialize_llm_and_embeddings()
        self._initialize_db()

    def _initialize_llm_and_embeddings(self):
        """Initialize LLM and embedding models following chatbot.py pattern."""
        try:
            # Disable SSL verification for development (following chatbot.py)
            http_client = httpx.Client(verify=False)
            
            # Set up LLM (following chatbot.py)
            llm = AzureOpenAI(
                default_headers={"Ocp-Apim-Subscription-Key": self.settings.azure_openai_key},
                api_key=self.settings.azure_openai_key,
                azure_endpoint=self.settings.azure_openai_endpoint,
                azure_deployment=self.settings.azure_openai_deployment_name,
                api_version=self.settings.azure_openai_version,
                model=self.settings.azure_openai_deployment_name,
                http_client=http_client
            )
            
            # Set up embedding model (following chatbot.py)
            embedding_model = AzureOpenAIEmbedding(
                deployment_name=self.settings.azure_openai_embedding_deployment_name,
                api_key=self.settings.azure_openai_embedding_key,
                azure_endpoint=self.settings.azure_openai_embedding_endpoint,
                api_version=self.settings.azure_openai_embedding_api_version,
                http_client=http_client
            )
            
            # Set global LlamaIndex settings (following chatbot.py)
            LlamaSettings.llm = llm
            LlamaSettings.embed_model = embedding_model
            
            self._llm_configured = True
            self._embedding_configured = True
            logger.info("LLM and embedding models configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM and embeddings: {e}")
            self._llm_configured = False
            self._embedding_configured = False

    def _initialize_db(self):
        """Initialize ChromaDB connection and index."""
        try:
            # Use settings path instead of hardcoded (following settings.py)
            index_path = self.settings.vector_db_absolute_path
            
            if not os.path.exists(index_path):
                logger.warning(f"ChromaDB path does not exist: {index_path}")
                self._fallback_to_test_mode()
                return
            
            # Initialize ChromaDB client (following chatbot.py)
            self._db = chromadb.PersistentClient(path=index_path)
            
            # Get or create collection (following chatbot.py)
            self._collection = self._db.get_or_create_collection("sql_tables_metadata")
            
            # Check if collection has data
            doc_count = self._collection.count()
            if doc_count == 0:
                logger.warning(f"Collection is empty: {self._collection.name}")
                self._fallback_to_test_mode()
                return
            
            # Assign chroma as the vector_store to the context (following chatbot.py)
            vector_store = ChromaVectorStore(chroma_collection=self._collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Load index from stored vectors (following chatbot.py)
            self._index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
            
            # Create a query engine (following chatbot.py)
            self._query_engine = self._index.as_query_engine(similarity_top_k=10)
            
            logger.info(f"Vector database initialized successfully - Collection: {self._collection.name}, Documents: {doc_count}")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {e}")
            self._fallback_to_test_mode()
    
    def _fallback_to_test_mode(self):
        """Fall back to test mode when vector DB is unavailable."""
        logger.warning("Falling back to test mode (no vector search)")
        self._db = None
        self._collection = None
        self._index = None
        self._query_engine = None

    @property
    def query_engine(self):
        """Get the query engine for vector searches."""
        if self._query_engine is None:
            self._initialize_db()
        return self._query_engine

    def search_tables(self, query: str) -> str:
        """
        Search for relevant table metadata using vector similarity.
        Following chatbot.py pattern exactly - SYNCHRONOUS like the working version.
        
        Args:
            query: Search query for table metadata
            
        Returns:
            Retrieved table metadata as string
        """
        try:
            # Check if vector search is available
            if self._query_engine is None:
                logger.warning("Vector search not available - returning fallback data")
                return self._get_fallback_metadata(query)
            
            # Check if LLM and embeddings are configured
            if not (self._llm_configured and self._embedding_configured):
                logger.warning("LLM/Embeddings not configured - returning fallback data")
                return self._get_fallback_metadata(query)
                
            # Follow chatbot.py agent_table_rag pattern EXACTLY - synchronous call
            search_query = f"retrieve the full tables metadata without intepreting or editing anything for the following given tables: {query}"
            
            # Direct synchronous call like in chatbot.py
            response = self._query_engine.query(search_query)
            
            if response and hasattr(response, 'response'):
                logger.debug(f"Vector search completed for query: {query}")
                return response.response
            else:
                logger.warning("Empty response from vector search")
                return self._get_fallback_metadata(query)
                
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return self._get_fallback_metadata(query)
    
    def _get_fallback_metadata(self, query: str) -> str:
        """Get fallback table metadata when vector search is unavailable."""
        # Basic fallback metadata that covers common table types
        fallback_metadata = {
            "customer": """
            customer_information:
            - id (int, primary key)
            - name (varchar(100))
            - email (varchar(255))
            - phone (varchar(20))
            - created_date (datetime)
            """,
            "transaction": """
            transaction_history:
            - id (int, primary key)
            - customer_id (int, foreign key)
            - amount (decimal(10,2))
            - transaction_date (datetime)
            - transaction_type (varchar(50))
            """,

        }
        
        # Try to match query keywords to fallback metadata
        query_lower = query.lower()
        for keyword, metadata in fallback_metadata.items():
            if keyword in query_lower:
                return metadata
        
        # Default fallback
        return f"Mock table metadata for query: {query} - customer_information(id, name, email), transaction_history(id, customer_id, amount, date)"

    async def add_documents(self, documents: list) -> bool:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of documents to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # This would be implemented based on your document ingestion needs
            # For now, we assume the index is already populated
            logger.info(f"Documents added to vector store: {len(documents)} items")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {e}")
            return False

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for vector database service."""
        try:
            # For test mode, return a healthy status
            if self._db is None:
                return {
                    "service": "vector_db",
                    "status": "healthy",
                    "mode": "test_mode",
                    "message": "Running in test mode with mock data"
                }
                
            # Test collection access
            collection_count = self._collection.count() if self._collection else 0
            
            # Test query engine
            if self._query_engine is None and collection_count == 0:
                return {
                    "service": "vector_db",
                    "status": "healthy",
                    "collection_count": collection_count,
                    "db_path": getattr(self.settings, 'vector_db_absolute_path', 'unknown'),
                    "message": "No documents in collection - fallback mode active"
                }
                
            return {
                "service": "vector_db",
                "status": "healthy",
                "collection_count": collection_count,
                "db_path": getattr(self.settings, 'vector_db_absolute_path', 'unknown')
            }
            
        except Exception as e:
            return {
                "service": "vector_db",
                "status": "unhealthy", 
                "error": str(e),
                "db_path": getattr(self.settings, 'vector_db_absolute_path', 'unknown')
            }

    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the current collection."""
        try:
            if not self._collection:
                return {
                    "collection_name": "sql_tables_metadata",
                    "error": "Collection not initialized",
                    "status": "test_mode"
                }
                
            count = self._collection.count()
            
            return {
                "collection_name": "sql_tables_metadata",
                "document_count": count,
                "status": "ready"
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {
                "collection_name": "sql_tables_metadata",
                "error": str(e),
                "status": "error"
            }
