#!/usr/bin/env python3
"""
Simple test script to verify core Text2SQL functionality.
This script tests the main flow: Query -> Route -> SQL -> Response
"""

import sys
import os
import asyncio
import logging

# Add project root to path
project_root = os.path.dirname(__file__)
if project_root not in sys.path:
    sys.path.append(project_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_simple_query():
    """Test a simple query through the Text2SQL engine"""
    try:
        # Import after path setup
        from app.services import get_services
        from app.core.text2sql_engine import Text2SQLEngine
        
        logger.info("Getting services...")
        services = await get_services()
        logger.info("Services obtained successfully")
        
        logger.info("Creating Text2SQL engine...")
        engine = Text2SQLEngine(services)
        logger.info("Engine created successfully")
        
        # Test with a simple query
        test_query = "Hello, can you help me with SQL queries?"
        logger.info(f"Testing query: {test_query}")
        
        result = await engine.process_query(test_query)
        
        logger.info("Query processing completed!")
        logger.info(f"Success: {result.get('success')}")
        logger.info(f"Response: {result.get('response', 'No response')[:100]}...")
        
        return result
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}

async def test_sql_query():
    """Test a SQL-related query"""
    try:
        from app.services import get_services
        from app.core.text2sql_engine import Text2SQLEngine
        
        services = await get_services()
        engine = Text2SQLEngine(services)
        
        # Test with an SQL query
        sql_test_query = "Show me the customer transactions from last month"
        logger.info(f"Testing SQL query: {sql_test_query}")
        
        result = await engine.process_query(sql_test_query)
        
        logger.info("SQL Query processing completed!")
        logger.info(f"Success: {result.get('success')}")
        logger.info(f"Response: {result.get('response', 'No response')[:200]}...")
        logger.info(f"SQL Results: {len(result.get('sql_results', []))} results")
        logger.info(f"Chart HTML: {'Yes' if result.get('chart_html') else 'No'}")
        
        return result
        
    except Exception as e:
        logger.error(f"SQL Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}

async def main():
    """Run all tests"""
    logger.info("="*60)
    logger.info("TESTING TEXT2SQL CORE FUNCTIONALITY")
    logger.info("="*60)
    
    # Test 1: Simple query
    logger.info("\n" + "="*40)
    logger.info("TEST 1: Simple Query")
    logger.info("="*40)
    result1 = await test_simple_query()
    
    # Test 2: SQL query 
    logger.info("\n" + "="*40)
    logger.info("TEST 2: SQL Query")
    logger.info("="*40)
    result2 = await test_sql_query()
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    logger.info(f"Simple Query Test: {'PASSED' if result1.get('success') else 'FAILED'}")
    logger.info(f"SQL Query Test: {'PASSED' if result2.get('success') else 'FAILED'}")
    
    if result1.get('success') and result2.get('success'):
        logger.info("🎉 ALL TESTS PASSED! Core functionality is working.")
    else:
        logger.info("❌ Some tests failed. Check logs above.")

if __name__ == "__main__":
    asyncio.run(main())
