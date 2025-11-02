"""
OpenAI service for managing OpenAI API interactions.
Updated to use standard OpenAI API instead of Azure OpenAI.
"""

import os
import logging
import warnings
from typing import Optional, List, Dict, Any
from openai import OpenAI
from llama_index.llms.openai import OpenAI as LlamaIndexOpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings as LlamaSettings
from app.config.settings import Settings

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for managing OpenAI interactions."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client: Optional[OpenAI] = None
        self._llm: Optional[LlamaIndexOpenAI] = None
        self._embedding_model: Optional[OpenAIEmbedding] = None
        self._initialize_clients()
        
    def _initialize_clients(self):
        """Initialize OpenAI clients and configure LlamaIndex settings."""
        try:
            # Initialize standard OpenAI client
            self._client = OpenAI(
                api_key=self.settings.openai_api_key
            )
            
            # Initialize LlamaIndex LLM with standard OpenAI
            self._llm = LlamaIndexOpenAI(
                api_key=self.settings.openai_api_key,
                model=self.settings.openai_model,
            )
            
            # Initialize embedding model with standard OpenAI
            # Explicitly set api_base to ensure correct endpoint
            self._embedding_model = OpenAIEmbedding(
                model=self.settings.openai_embedding_model,
                api_key=self.settings.openai_api_key,
                api_base="https://api.openai.com/v1",
            )
            
            # Configure LlamaIndex global settings
            LlamaSettings.llm = self._llm
            LlamaSettings.embed_model = self._embedding_model
            
            logger.info("OpenAI clients and LlamaIndex settings initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI clients: {e}")
            raise
    
    @property
    def client(self) -> OpenAI:
        """Get the OpenAI client instance."""
        if self._client is None:
            self._initialize_clients()
        return self._client
    
    @property
    def llm(self) -> LlamaIndexOpenAI:
        """Get the LlamaIndex LLM instance."""
        if self._llm is None:
            self._initialize_clients()
        return self._llm
    
    @property
    def embedding_model(self) -> OpenAIEmbedding:
        """Get the embedding model instance."""
        if self._embedding_model is None:
            self._initialize_clients()
        return self._embedding_model
        
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Generate chat completion using new OpenAI API format.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            tools: Optional list of tool definitions
            
        Returns:
            OpenAI response object with output_text and output properties
        """
        try:
            params = {
                "model": self.settings.openai_model,
                "input": messages,
            }
            
            if tools:
                params["tools"] = tools
                
            # Note: temperature and max_tokens may need to be passed differently
            # in the new API - check OpenAI documentation for exact parameters
                
            response = self.client.responses.create(**params)
            
            logger.debug(f"Chat completion successful. Model: {self.settings.openai_model}")
            return response
            
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise
            
    async def validate_connection(self) -> bool:
        """Validate OpenAI service connection."""
        try:
            # Test with a simple completion
            test_messages = [{"role": "user", "content": "Hello"}]
            response = await self.chat_completion(test_messages)
            
            if response and hasattr(response, 'output_text'):
                logger.info("OpenAI service connection validated successfully")
                return True
            else:
                logger.error("OpenAI service connection validation failed: No response")
                return False
                
        except Exception as e:
            logger.error(f"OpenAI service connection validation failed: {e}")
            return False
            
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for OpenAI service."""
        try:
            is_healthy = await self.validate_connection()
            return {
                "service": "openai",
                "status": "healthy" if is_healthy else "unhealthy",
                "model": self.settings.openai_model,
                "api_configured": bool(self.settings.openai_api_key)
            }
        except Exception as e:
            return {
                "service": "openai",
                "status": "unhealthy",
                "error": str(e),
                "model": self.settings.openai_model
            }
