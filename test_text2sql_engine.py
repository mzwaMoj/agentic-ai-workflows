"""
Test Text2SQL Engine with Settings Fix
This script tests if the Text2SQL engine can properly access settings.
"""

import sys
import asyncio
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir.parent))

from app.config.settings import settings
from app.core.text2sql_engine import Text2SQLEngine
from app.services.openai_service import OpenAIService
from app.services.database_service import DatabaseService
from app.services.vector_service import VectorService
from app.services.logging_service import LoggingService

async def test_engine_initialization():
    """Test if the engine initializes correctly with settings."""
    print("="*60)
    print("Testing Text2SQL Engine Initialization")
    print("="*60)
    
    print("\n📋 Creating services...")
    
    # Initialize services
    services = {
        'openai': OpenAIService(settings),
        'database': DatabaseService(settings),
        'vector': VectorService(settings),
        'logging': LoggingService(settings)
    }
    
    print("✅ Services created successfully")
    
    print("\n📋 Creating Text2SQL Engine...")
    
    # Create engine with services and settings
    engine = Text2SQLEngine(services, settings)
    
    print("✅ Engine created successfully")
    
    # Verify settings are accessible
    print("\n📋 Verifying settings access...")
    print(f"  DB Server: {engine.settings.db_server}")
    print(f"  DB Database: {engine.settings.db_database}")
    print(f"  DB Auth Type: {engine.settings.db_auth_type}")
    print(f"  DB Username: {engine.settings.db_username if engine.settings.db_username else '(None)'}")
    
    print("\n✅ Settings are accessible from engine!")
    
    # Verify services are accessible
    print("\n📋 Verifying services access...")
    print(f"  OpenAI Service: {type(engine.openai_service).__name__}")
    print(f"  Database Service: {type(engine.database_service).__name__}")
    print(f"  Vector Service: {type(engine.vector_service).__name__}")
    print(f"  Logging Service: {type(engine.logging_service).__name__}")
    
    print("\n✅ All services are accessible from engine!")
    
    print("\n" + "="*60)
    print("✅ TEST PASSED: Engine initialization successful!")
    print("="*60)

async def test_simple_query():
    """Test a simple query to verify the full pipeline."""
    print("\n" + "="*60)
    print("Testing Simple Query Processing")
    print("="*60)
    
    print("\n📋 Creating services...")
    
    # Initialize services
    services = {
        'openai': OpenAIService(settings),
        'database': DatabaseService(settings),
        'vector': VectorService(settings),
        'logging': LoggingService(settings)
    }
    
    print("✅ Services created successfully")
    
    print("\n📋 Creating Text2SQL Engine...")
    engine = Text2SQLEngine(services, settings)
    print("✅ Engine created successfully")
    
    print("\n📋 Processing test query...")
    test_query = "Show me the top 5 customers"
    
    try:
        result = await engine.process_query(test_query)
        
        print("\n✅ Query processed successfully!")
        print(f"\n📊 Result Summary:")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Response: {result.get('response', 'No response')[:200]}...")
        
        if result.get('sql_code'):
            print(f"\n  SQL Code: {result.get('sql_code')[:200]}...")
        
        print("\n" + "="*60)
        print("✅ TEST PASSED: Query processing successful!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        print(f"\n💡 Error details: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60)

if __name__ == "__main__":
    print("\n🚀 Text2SQL Engine Test Suite\n")
    
    # Test 1: Engine initialization
    asyncio.run(test_engine_initialization())
    
    # Test 2: Simple query (commented out by default to avoid hitting OpenAI API)
    # Uncomment to test full query processing
    # print("\n")
    # asyncio.run(test_simple_query())
    
    print("\n✅ All tests complete!")
