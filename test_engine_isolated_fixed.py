#!/usr/bin/env python3
"""
Simple test to check if the Text2SQL engine can process a basic query
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from app.core.text2sql_engine import Text2SQLEngine
    from app.services import get_services
    
    print("✅ Imports successful")
    
    async def test_engine():
        # Get services (async) - returns a dict
        services = await get_services()
        
        print(f"✅ Services loaded: {list(services.keys())}")
        
        # Initialize engine
        engine = Text2SQLEngine(services)
        print("✅ Text2SQL engine initialized")
        
        return engine
    
    # Run async test
    engine = asyncio.run(test_engine())
    
    # Test a simple query
    test_query = "SELECT 1 as test"
    
    print("🔍 Testing simple query processing...")
    
    try:
        result = engine.process_query(user_input=test_query)
        print("✅ Query processed successfully!")
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        print(f"Success: {result.get('success', False)}")
        print(f"Response: {result.get('response', 'No response')[:100]}...")
        
    except Exception as e:
        print(f"❌ Error during query processing: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"❌ Import or initialization error: {e}")
    import traceback
    traceback.print_exc()
