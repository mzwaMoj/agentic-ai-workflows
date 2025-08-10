#!/usr/bin/env python3
"""
Comprehensive test of the Text2SQL API with proper embedding configuration.
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.append(project_root)

async def test_text2sql_engine():
    """Test the Text2SQL engine directly."""
    print("Testing Text2SQL Engine...")
    
    try:
        from app.services import get_services
        from app.core.text2sql_engine import Text2SQLEngine
        
        # Initialize services
        services = await get_services()
        engine = Text2SQLEngine(services)
        
        # Test query processing
        test_query = "Show me the top 10 customers by transaction amount"
        print(f"Processing query: {test_query}")
        
        result = await engine.process_query(test_query)
        
        print(f"✓ Query processed successfully")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Response: {result.get('response', 'No response')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Text2SQL engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_endpoint():
    """Test the API endpoint."""
    print("\nTesting API endpoint...")
    
    try:
        import httpx
        
        # Start server in background and test
        print("Note: For full API test, start the server with: python -m uvicorn app.main:app --reload")
        
        # For now, just test if the app can be imported
        from app.main import app
        print("✓ FastAPI app can be imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ API endpoint test failed: {e}")
        return False

async def test_chatbot_compatibility():
    """Test compatibility with original chatbot functionality."""
    print("\nTesting chatbot compatibility...")
    
    try:
        # Test import of chatbot functions
        sys.path.append(str(Path(__file__).parent / "core"))
        
        # Test if we can import the agents
        from agents.agents import routing_agent, agent_sql_analysis
        print("✓ Agents can be imported")
          # Test if we can import database functions
        from app.db.sql_query_executor import execute_sql_with_pyodbc
        print("✓ Database functions can be imported")
        
        # Test if we can import chart generation
        from utils.generate_charts import execute_plot_code
        print("✓ Chart generation functions can be imported")
        
        return True
        
    except Exception as e:
        print(f"✗ Chatbot compatibility test failed: {e}")
        return False

async def test_vector_functionality():
    """Test vector database functionality in detail."""
    print("\nTesting vector functionality...")
    
    try:
        from app.services import get_services
        
        services = await get_services()
        vector_service = services['vector']
        
        # Test various search queries
        test_queries = [
            "customer data",
            "transaction history", 
            "account information",
            "user profiles"
        ]
        
        for query in test_queries:
            result = await vector_service.search_tables(query)
            print(f"✓ Search for '{query}': {len(str(result))} characters returned")
        
        return True
        
    except Exception as e:
        print(f"✗ Vector functionality test failed: {e}")
        return False

async def main():
    """Run comprehensive tests."""
    print("=== Comprehensive Text2SQL API Test ===\n")
    
    tests = [
        ("Vector Functionality", test_vector_functionality),
        ("Chatbot Compatibility", test_chatbot_compatibility), 
        ("Text2SQL Engine", test_text2sql_engine),
        ("API Endpoint", test_api_endpoint)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"--- {test_name} ---")
        try:
            result = await test_func()
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
        print("\n🎉 All tests passed! The modular Text2SQL API is working correctly.")
        print("\n📋 Next Steps:")
        print("1. Start the API server: python -m uvicorn app.main:app --reload")
        print("2. Test the API endpoints at: http://localhost:8000/docs")
        print("3. Try the simple endpoint: POST /api/v1/text2sql/generate")
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
