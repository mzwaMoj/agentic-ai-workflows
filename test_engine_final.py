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

async def main():
    try:
        from app.core.text2sql_engine import Text2SQLEngine
        from app.services import get_services
        
        print("✅ Imports successful")
        
        # Get services (async) - returns a dict
        services = await get_services()
        
        print(f"✅ Services loaded: {list(services.keys())}")
        
        # Initialize engine
        engine = Text2SQLEngine(services)
        print("✅ Text2SQL engine initialized")
        
        # Test a simple query
        test_query = "SELECT 1 as test"
        
        print("🔍 Testing simple query processing...")
        
        try:
            # AWAIT the async method
            result = await engine.process_query(user_input=test_query)
            print("✅ Query processed successfully!")
            print(f"Result type: {type(result)}")
            
            if isinstance(result, dict):
                print(f"Result keys: {list(result.keys())}")
                print(f"Success: {result.get('success', 'No success key')}")
                response = result.get('response', 'No response key')
                print(f"Response: {response[:200]}..." if len(str(response)) > 200 else f"Response: {response}")
                
                if result.get('sql_results'):
                    print(f"SQL Results: {len(result['sql_results'])} items")
                if result.get('chart_html'):
                    print("✅ Chart HTML generated")
            else:
                print(f"Unexpected result: {result}")
            
        except Exception as e:
            print(f"❌ Error during query processing: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Import or initialization error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
