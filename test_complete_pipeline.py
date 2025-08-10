"""
Complete Text2SQL Pipeline Testing
Tests the full end-to-end pipeline: Router -> SQL Analysis -> SQL Executor -> Final Response
"""

import requests
import json
import time
import logging

# Set up logging to see detailed pipeline execution
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def test_complete_pipeline():
    """Test the complete Text2SQL pipeline with detailed tracing."""
    
    print("🔍 TESTING COMPLETE TEXT2SQL PIPELINE")
    print("=" * 60)
    
    # Test query - exactly as specified
    test_query = "which client has the highest account balance? Which quarter had the highest amount? Show me a line graph of transactions over time."
    
    print(f"📝 Test Query: '{test_query}'")
    print(f"🎯 Expected: Client name with highest balance + details")
    print(f"📋 Pipeline Steps to Verify:")
    print(f"   1. Router -> Route to SQL analysis")
    print(f"   2. SQL Analysis -> Generate SQL query")  
    print(f"   3. SQL Executor -> Execute query and get results")
    print(f"   4. Final Response -> Format natural language response")
    print()
    
    # Prepare request payload
    payload = {
        "query": test_query,
        "include_charts": True,
        "max_results": 100
    }
    
    print("🚀 Sending request to /api/v1/text2sql/generate...")
    print(f"📤 Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        # Make the request with extended timeout for pipeline processing
        start_time = time.time()
        
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/text2sql/generate",
            json=payload,
            timeout=200  # Extended timeout for full pipeline
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⏱️  Total Processing Time: {processing_time:.2f} seconds")
        print(f"📊 Response Status: {response.status_code}")
        print()
        
        if response.status_code == 200:
            print("✅ REQUEST SUCCESSFUL - Analyzing Pipeline Results...")
            print("=" * 60)
            
            # Parse response
            try:
                data = response.json()
                analyze_pipeline_response(data, test_query)
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON Decode Error: {e}")
                print(f"Raw response: {response.text[:500]}...")
                return False
                
        else:
            print(f"❌ REQUEST FAILED - Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ REQUEST TIMEOUT - Pipeline took too long")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - Could not connect to server")
        return False
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

def analyze_pipeline_response(data, original_query):
    """Analyze the response to verify each pipeline step worked correctly."""
    
    print("🔬 PIPELINE STEP ANALYSIS")
    print("=" * 40)
    
    # Check overall success
    success = data.get('success', False)
    print(f"📈 Overall Success: {'✅ YES' if success else '❌ NO'}")
    
    if not success:
        error = data.get('error', 'Unknown error')
        print(f"❌ Error: {error}")
        return False
    
    print()
    
    # Step 1: Router Analysis
    print("🎯 STEP 1: ROUTER ANALYSIS")
    print("-" * 30)
    
    response_text = data.get('response', '')
    if response_text:
        print("✅ Router successfully processed the query")
        print(f"📝 Response Length: {len(response_text)} characters")
    else:
        print("❌ No response text generated")
        return False
    
    print()
    
    # Step 2: SQL Generation
    print("🛠️  STEP 2: SQL GENERATION")
    print("-" * 30)
    
    sql_query = data.get('sql_query', '')
    if sql_query:
        print("✅ SQL query was generated")
        print(f"📋 Generated SQL:")
        print(f"   {sql_query}")
        
        # Validate SQL looks correct for the query
        sql_lower = sql_query.lower()
        if 'select' in sql_lower and ('balance' in sql_lower or 'customer' in sql_lower):
            print("✅ SQL appears relevant to the query (contains SELECT and balance/customer)")
        else:
            print("⚠️  SQL might not be relevant to the original query")
            
    else:
        print("❌ No SQL query was generated")
        return False
    
    print()
    
    # Step 3: SQL Execution
    print("🏃 STEP 3: SQL EXECUTION")
    print("-" * 30)
    
    sql_results = data.get('sql_results', [])
    execution_time = data.get('execution_time', 0)
    
    if sql_results:
        print(f"✅ SQL executed successfully")
        print(f"📊 Results Count: {len(sql_results)} rows")
        print(f"⏱️  Execution Time: {execution_time:.3f} seconds")
        
        # Show first result to verify data
        if len(sql_results) > 0:
            first_result = sql_results[0]
            print(f"📋 First Result: {json.dumps(first_result, indent=2)}")
            
            # Check if result contains client name and balance
            has_name = any(key for key in first_result.keys() if 'name' in key.lower())
            has_balance = any(key for key in first_result.keys() if 'balance' in key.lower())
            
            if has_name and has_balance:
                print("✅ Result contains client name and balance data")
            else:
                print("⚠️  Result might be missing expected fields")
                print(f"   Available fields: {list(first_result.keys())}")
                
    else:
        print("❌ No SQL results returned")
        return False
        
    print()
    
    # Step 4: Final Response Generation
    print("📝 STEP 4: FINAL RESPONSE GENERATION")
    print("-" * 40)
    
    if response_text:
        print("✅ Natural language response generated")
        print(f"📄 Response Preview:")
        print(f"   {response_text[:300]}...")
        
        # Check if response mentions client name
        if sql_results and len(sql_results) > 0:
            first_result = sql_results[0]
            
            # Look for name fields in the result
            name_fields = [v for k, v in first_result.items() if 'name' in k.lower() and isinstance(v, str)]
            
            if name_fields:
                client_name = name_fields[0]
                if client_name.lower() in response_text.lower():
                    print(f"✅ Response includes client name: '{client_name}'")
                else:
                    print(f"⚠️  Response might not include client name: '{client_name}'")
            else:
                print("⚠️  Could not find client name in results to verify")
        
        # Check if response mentions balance
        if 'balance' in response_text.lower():
            print("✅ Response mentions balance information")
        else:
            print("⚠️  Response might not mention balance")
            
    else:
        print("❌ No final response generated")
        return False
    
    print()
    
    # Step 5: Chart Generation (if applicable)
    print("📊 STEP 5: CHART GENERATION")
    print("-" * 30)
    
    chart_html = data.get('chart_html', '')
    if chart_html:
        print(f"✅ Chart generated")
        print(f"📏 Chart HTML Length: {len(chart_html)} characters")
    else:
        print("ℹ️  No chart generated (might not be applicable for this query)")
    
    print()
    
    # Overall Pipeline Assessment
    print("🎯 OVERALL PIPELINE ASSESSMENT")
    print("=" * 40)
    
    pipeline_health = []
    pipeline_health.append(("Router Processing", bool(response_text)))
    pipeline_health.append(("SQL Generation", bool(sql_query)))
    pipeline_health.append(("SQL Execution", bool(sql_results)))
    pipeline_health.append(("Response Generation", bool(response_text)))
    
    passed_steps = sum(1 for _, status in pipeline_health if status)
    total_steps = len(pipeline_health)
    
    for step_name, status in pipeline_health:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {step_name}")
    
    print()
    print(f"📊 Pipeline Success Rate: {passed_steps}/{total_steps} steps ({(passed_steps/total_steps)*100:.1f}%)")
    
    if passed_steps == total_steps:
        print("🎉 COMPLETE PIPELINE SUCCESS!")
        print("✅ All steps executed correctly")
        print("✅ End-to-end functionality verified")
        return True
    else:
        print("⚠️  Pipeline has issues - some steps failed")
        return False

def main():
    """Main test execution."""
    print("🧪 TEXT2SQL COMPLETE PIPELINE TEST")
    print("=" * 60)
    print("Testing end-to-end functionality with real query...")
    print()
    
    success = test_complete_pipeline()
    
    print()
    print("=" * 60)
    
    if success:
        print("🎉 PIPELINE TEST PASSED!")
        print("✅ Complete Text2SQL functionality verified")
        print("✅ All pipeline steps working correctly")
    else:
        print("❌ PIPELINE TEST FAILED!")
        print("⚠️  One or more pipeline steps have issues")
        print("🔧 Review the analysis above for specific problems")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
