"""
Configuration settings for the Text2SQL application.
Centralized configuration management with environment variable support.
"""

import os
from typing import Optional, List
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


class Settings:
    """Application settings with environment variable support."""
    
    def __init__(self):
        # Application
        self.app_name: str = os.environ.get("APP_NAME")
        self.app_version: str = os.environ.get("APP_VERSION")
        self.debug: bool = os.environ.get("DEBUG", "false").lower() == "true"
        
        # OpenAI Configuration (replaces Azure OpenAI)
        self.openai_api_key: str = os.environ.get("OPENAI_API_KEY")
        self.openai_model: str = os.environ.get("OPENAI_MODEL", "gpt-4o")
        
        # OpenAI Embedding Configuration (using standard OpenAI embeddings)
        self.openai_embedding_model: str = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        
        # Database Configuration
        # Default to SQL authentication for macOS (Windows uses 'windows' auth)
        self.db_server: str = os.environ.get("DB_SERVER", "localhost,1433")
        self.db_database: str = os.environ.get("DB_DATABASE", "master")
        self.db_auth_type: str = os.environ.get("DB_AUTH_TYPE", "sql")  # Default to 'sql' for macOS
        self.db_username: Optional[str] = os.environ.get("DB_USERNAME", "SA")
        self.db_password: Optional[str] = os.environ.get("DB_PASSWORD")        # ChromaDB Configuration
        self.chroma_persist_directory: str = os.environ.get("CHROMA_PERSIST_DIRECTORY", "./index/chroma_db")
        self.chroma_collection_name: str = os.environ.get("CHROMA_COLLECTION_NAME", "sql_tables_metadata")
        
        # Vector Database Configuration
        self.vector_db_path: str = os.environ.get("VECTOR_DB_PATH", "./index/chroma_db")
        
        # MLflow Configuration
        self.mlflow_tracking_uri: str = os.environ.get("MLFLOW_TRACKING_URI", "./mlruns")
        self.mlflow_experiment_name: str = os.environ.get("MLFLOW_EXPERIMENT_NAME")
        
        # API Configuration
        self.api_title: str = os.environ.get("API_TITLE")
        self.api_description: str = os.environ.get("API_DESCRIPTION")
        self.api_version: str = os.environ.get("API_VERSION")
        self.api_prefix: str = os.environ.get("API_PREFIX", "/api/v1")
        
        # Server Configuration
        self.host: str = os.environ.get("HOST", "0.0.0.0")
        self.port: int = int(os.environ.get("PORT", "8000"))
        self.workers: int = int(os.environ.get("WORKERS", "1"))
        
        # CORS Configuration
        self.cors_origins: List[str] = os.environ.get("CORS_ORIGINS", "*").split(",")
        self.cors_methods: List[str] = os.environ.get("CORS_METHODS", "GET,POST,PUT,DELETE").split(",")
        self.cors_headers: List[str] = os.environ.get("CORS_HEADERS", "*").split(",")
        
        # Logging Configuration
        self.log_level: str = os.environ.get("LOG_LEVEL", "INFO")
        self.log_format: str = os.environ.get("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        # Feature Flags
        self.enable_chat: bool = os.environ.get("ENABLE_CHAT", "true").lower() == "true"
        self.enable_charts: bool = os.environ.get("ENABLE_CHARTS", "true").lower() == "true"
        self.enable_mlflow: bool = os.environ.get("ENABLE_MLFLOW", "true").lower() == "true"
        
        # Security
        self.api_key: Optional[str] = os.environ.get("API_KEY")
        self.secret_key: str = os.environ.get("SECRET_KEY")
        
        # Load from .env file if it exists
        self._load_env_file()
    
    def _load_env_file(self):
        """Load environment variables from .env file if it exists."""
        env_file = Path(".env")
        if env_file.exists():
            try:
                
                from dotenv import load_dotenv, find_dotenv
                # load_dotenv(find_dotenv())
                load_dotenv(env_file)
                
                # Note: We don't reload __init__ to avoid infinite recursion
            except ImportError:
                pass  # python-dotenv not available
    @property
    def database_url(self) -> str:
        """Get database connection URL."""
        if self.db_auth_type and self.db_auth_type.lower() == "windows":
            return f"mssql+pyodbc://{self.db_server}/{self.db_database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
        else:
            # SQL authentication (default for macOS/Docker)
            return f"mssql+pyodbc://{self.db_username}:{self.db_password}@{self.db_server}/{self.db_database}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes&Encrypt=no"
        
    @property
    def vector_db_absolute_path(self) -> str:
        """Get absolute path for vector database."""
        if os.path.isabs(self.vector_db_path):
            return self.vector_db_path
        
        # Get the project root directory (text_sql_analysis folder)
        current_file = Path(__file__)  # This is app/config/settings.py
        project_root = current_file.parent.parent.parent  # Go up to text_sql_analysis
        return str(project_root / self.vector_db_path)
        
    def validate_required_settings(self) -> bool:
        """Validate that required settings are provided."""
        required_fields = [
            "openai_api_key",
            "openai_model"
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(self, field):
                missing_fields.append(field)
                
        if missing_fields:
            print(f"Warning: Missing configuration for: {', '.join(missing_fields)}")
            print("Application will start but may not function properly without these settings.")
            
        return len(missing_fields) == 0


# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
