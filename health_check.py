"""
Quick health check for individual components of the Text2SQL API.
Tests each service separately to identify specific issues.
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def test_environment_setup():
    """Test environment configuration."""
    logger.info("Testing environment setup...")
    
    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        logger.warning(".env file not found. Using environment variables or defaults.")
        return False
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("✅ Environment variables loaded successfully")
        return True
    except ImportError:
        logger.error("❌ python-dotenv not installed")
        return False
    except Exception as e:
        logger.error(f"❌ Error loading environment: {e}")
        return False


def test_azure_openai_config():
    """Test Azure OpenAI configuration."""
    logger.info("Testing Azure OpenAI configuration...")
    
    try:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        key = os.getenv("AZURE_OPENAI_KEY")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        if not endpoint or "your_" in endpoint:
            logger.error("❌ AZURE_OPENAI_ENDPOINT not configured")
            return False
            
        if not key or "your_" in key:
            logger.error("❌ AZURE_OPENAI_KEY not configured")
            return False
            
        if not deployment or "your_" in deployment:
            logger.error("❌ AZURE_OPENAI_DEPLOYMENT_NAME not configured")
            return False
        
        logger.info("✅ Azure OpenAI configuration looks valid")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking Azure OpenAI config: {e}")
        return False


def test_database_config():
    """Test database configuration."""
    logger.info("Testing database configuration...")
    
    try:
        server = os.getenv("DB_SERVER")
        database = os.getenv("DB_DATABASE", "master")
        auth_type = os.getenv("DB_AUTH_TYPE", "windows")
        
        if not server or "your_" in server:
            logger.error("❌ DB_SERVER not configured")
            return False
        
        logger.info(f"✅ Database config: {server}/{database} (auth: {auth_type})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking database config: {e}")
        return False


def test_dependencies():
    """Test if all required dependencies are available."""
    logger.info("Testing Python dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "pydantic",
        "openai",
        "llama_index",
        "chromadb",
        "pandas",
        "plotly",
        "requests",
        "pyodbc"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} not installed")
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        return False
    
    logger.info("✅ All required packages are available")
    return True


def test_directory_structure():
    """Test if required directories exist."""
    logger.info("Testing directory structure...")
    
    required_dirs = [
        "app",
        "logs",
        "index"
    ]
    
    missing_dirs = []
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            logger.info(f"✅ {dir_name}/ directory exists")
        else:
            missing_dirs.append(dir_name)
            logger.error(f"❌ {dir_name}/ directory missing")
    
    # Create missing directories
    for dir_name in missing_dirs:
        try:
            Path(dir_name).mkdir(exist_ok=True)
            logger.info(f"✅ Created {dir_name}/ directory")
        except Exception as e:
            logger.error(f"❌ Failed to create {dir_name}/ directory: {e}")
    
    return len(missing_dirs) == 0


def test_app_imports():
    """Test if the main application can be imported."""
    logger.info("Testing application imports...")
    
    try:
        # Test basic imports
        from app.config import settings
        logger.info("✅ App config imported successfully")
        
        from app.main import create_app
        logger.info("✅ Main app factory imported successfully")
        
        # Test if app can be created
        app = create_app()
        logger.info("✅ FastAPI app created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error importing app components: {e}")
        return False


def test_vector_database():
    """Test vector database setup."""
    logger.info("Testing vector database...")
    
    try:
        import chromadb
        
        # Check if chroma directory exists
        chroma_path = Path("index/chroma_db")
        if chroma_path.exists():
            logger.info(f"✅ ChromaDB directory exists at {chroma_path}")
        else:
            logger.info(f"ℹ️  ChromaDB directory will be created at {chroma_path}")
            chroma_path.mkdir(parents=True, exist_ok=True)
            
        # Test chromadb client creation
        client = chromadb.PersistentClient(path=str(chroma_path))
        logger.info("✅ ChromaDB client created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error with vector database: {e}")
        return False


def main():
    """Run all health checks."""
    logger.info("Starting Text2SQL API Health Check...")
    logger.info("=" * 60)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Dependencies", test_dependencies),
        ("Directory Structure", test_directory_structure),
        ("Azure OpenAI Config", test_azure_openai_config),
        ("Database Config", test_database_config),
        ("Vector Database", test_vector_database),
        ("App Imports", test_app_imports),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("HEALTH CHECK SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name:.<30} {status}")
    
    logger.info("-" * 60)
    logger.info(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All health checks passed! Application should be ready to run.")
        return True
    else:
        logger.warning("⚠️  Some health checks failed. Please address the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    logger.info(f"\nHealth check log saved to: {log_file}")
    sys.exit(0 if success else 1)
