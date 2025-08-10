#!/usr/bin/env python3
"""
Test script to verify embedding configuration and vector database functionality.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.append(project_root)

def test_imports():
    """Test if all required imports work."""
    print("Testing imports...")
    try:
        from app.services import get_services
        print("✓ Services import successful")
        
        from llama_index.core import Settings as LlamaSettings
        print("✓ LlamaIndex Settings import successful")
        
        from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
        print("✓ Azure OpenAI Embedding import successful")
        
        from llama_index.llms.azure_openai import AzureOpenAI as LlamaAzureOpenAI
        print("✓ LlamaIndex Azure OpenAI import successful")
        
        import chromadb
        print("✓ ChromaDB import successful")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_services_initialization():
    """Test if services can be initialized."""
    print("\nTesting services initialization...")
    try:
        import asyncio
        from app.services import get_services
        
        async def test():
            services = await get_services()
            print("✓ Services initialized successfully")
            
            # Test OpenAI service
            openai_service = services['openai']
            print(f"✓ OpenAI service available: {type(openai_service).__name__}")
            
            # Test if embedding model is configured
            if hasattr(openai_service, 'embedding_model'):
                embedding_model = openai_service.embedding_model
                print(f"✓ Embedding model available: {type(embedding_model).__name__}")
            else:
                print("✗ Embedding model not available")
            
            # Test vector service
            vector_service = services['vector']
            print(f"✓ Vector service available: {type(vector_service).__name__}")
            
            return True
            
        return asyncio.run(test())
        
    except Exception as e:
        print(f"✗ Services initialization failed: {e}")
        return False

def test_vector_search():
    """Test vector search functionality."""
    print("\nTesting vector search...")
    try:
        import asyncio
        from app.services import get_services
        
        async def test():
            services = await get_services()
            vector_service = services['vector']
            
            # Test search functionality
            result = await vector_service.search_tables("customer transaction data")
            print(f"✓ Vector search completed")
            print(f"  Result (first 100 chars): {str(result)[:100]}...")
            
            return True
            
        return asyncio.run(test())
        
    except Exception as e:
        print(f"✗ Vector search failed: {e}")
        return False

def test_environment_variables():
    """Test if required environment variables are set."""
    print("\nTesting environment variables...")
    
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_KEY",
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "AZURE_OPENAI_VERSION",
        "AZURE_OPENAI_EMBEDDING_ENDPOINT",
        "AZURE_OPENAI_EMBEDDING_KEY", 
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME",
        "AZURE_OPENAI_EMBEDDING_API_VERSION"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
        else:
            print(f"✓ {var} is set")
    
    if missing_vars:
        print(f"✗ Missing environment variables: {missing_vars}")
        return False
    else:
        print("✓ All required environment variables are set")
        return True

def main():
    """Run all tests."""
    print("=== Embedding Configuration Test ===\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Environment Variables", test_environment_variables),
        ("Services Initialization", test_services_initialization),
        ("Vector Search", test_vector_search)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n=== Test Summary ===")
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 All tests passed! Embedding configuration is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the configuration.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
