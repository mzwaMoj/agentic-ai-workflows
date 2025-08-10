"""
Azure OpenAI service for managing OpenAI API interactions.
"""

import os
import logging
import ssl
import urllib3
import warnings
import httpx
from typing import Optional, List, Dict, Any
from openai import AzureOpenAI
from llama_index.llms.azure_openai import AzureOpenAI as LlamaAzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import Settings as LlamaSettings
from app.config.settings import Settings

# Disable SSL warnings for development (following chatbot.py)
warnings.filterwarnings("ignore")
ssl._create_default_https_context = ssl._create_unverified_context
# For requests and urllib3, suppress warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Create httpx client with SSL verification disabled
http_client = httpx.Client(verify=False)


logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for managing Azure OpenAI interactions."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client: Optional[AzureOpenAI] = None
        self._llm: Optional[LlamaAzureOpenAI] = None
        self._embedding_model: Optional[AzureOpenAIEmbedding] = None
        self._initialize_clients()
        
    def _initialize_clients(self):
        """Initialize Azure OpenAI clients and configure LlamaIndex settings."""
        try:
            # Initialize standard OpenAI client
            self._client = AzureOpenAI(
                api_key=self.settings.azure_openai_key,
                api_version=self.settings.azure_openai_version,
                azure_endpoint=self.settings.azure_openai_endpoint,
                http_client=http_client
            )
            
            # Initialize LlamaIndex LLM (following chatbot.py)
            self._llm = LlamaAzureOpenAI(
                default_headers={"Ocp-Apim-Subscription-Key": self.settings.azure_openai_key},
                api_key=self.settings.azure_openai_key,
                azure_endpoint=self.settings.azure_openai_endpoint,
                azure_deployment=self.settings.azure_openai_deployment_name,
                api_version=self.settings.azure_openai_version,
                model=self.settings.azure_openai_deployment_name,
                http_client=http_client
            )
            
            # Initialize embedding model (following chatbot.py)
            self._embedding_model = AzureOpenAIEmbedding(
                deployment_name=self.settings.azure_openai_embedding_deployment_name,
                api_key=self.settings.azure_openai_embedding_key,
                azure_endpoint=self.settings.azure_openai_embedding_endpoint,
                api_version=self.settings.azure_openai_embedding_api_version,
                http_client=http_client
            )
            
            # Configure LlamaIndex global settings (following chatbot.py)
            LlamaSettings.llm = self._llm
            LlamaSettings.embed_model = self._embedding_model
            
            logger.info("Azure OpenAI clients and LlamaIndex settings initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI clients: {e}")
            raise
    @property
    def client(self) -> AzureOpenAI:
        """Get the OpenAI client instance."""
        if self._client is None:
            self._initialize_clients()
        return self._client
    
    @property
    def llm(self) -> LlamaAzureOpenAI:
        """Get the LlamaIndex LLM instance."""
        if self._llm is None:
            self._initialize_clients()
        return self._llm
    
    @property
    def embedding_model(self) -> AzureOpenAIEmbedding:
        """Get the embedding model instance."""
        if self._embedding_model is None:
            self._initialize_clients()
        return self._embedding_model
        
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.4,
        max_tokens: Optional[int] = None
    ) -> Any:
        """
        Create a chat completion with Azure OpenAI.
        
        Args:
            messages: List of message dictionaries
            tools: Optional list of tools/functions
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            OpenAI chat completion response
        """
        try:
            params = {
                "model": self.settings.azure_openai_deployment_name,
                "messages": messages,
                "temperature": temperature
            }
            
            if tools:
                params["tools"] = tools
                params["tool_choice"] = "auto"
                
            if max_tokens:
                params["max_tokens"] = max_tokens
                
            response = self.client.chat.completions.create(**params)
            
            logger.debug(f"Chat completion successful. Model: {self.settings.azure_openai_deployment_name}")
            return response
            
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise
            
    async def validate_connection(self) -> bool:
        """Validate OpenAI service connection."""
        try:
            # Test with a simple completion
            test_messages = [{"role": "user", "content": "Hello"}]
            response = await self.chat_completion(test_messages, max_tokens=10)
            
            if response and response.choices:
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
                "endpoint": self.settings.azure_openai_endpoint,
                "deployment": self.settings.azure_openai_deployment_name,
                "version": self.settings.azure_openai_version
            }
        except Exception as e:
            return {
                "service": "openai",
                "status": "unhealthy",
                "error": str(e),
                "endpoint": self.settings.azure_openai_endpoint,
                "deployment": self.settings.azure_openai_deployment_name
            }
