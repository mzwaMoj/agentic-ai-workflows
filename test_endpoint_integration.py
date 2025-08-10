"""
Comprehensive test to check if executor and generate endpoints work together correctly
and diagnose any integration issues.
"""
import requests
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

def check_server_status():
    """Check if the server is running"""
    print("🔍 Checking Server Status")
    print("=" * 30)
    
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        print(f"✅ Server is running: {response.status_code}")
        print(f"Server info: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running!")
        print("Please start the server with: python -m app.main")
        return False
    except Exception as e:
        print(f"❌ Server check failed: {e}")
        return False

def test_generate_endpoint_detailed():
    """Test the generate endpoint in detail"""
    print("\n🔍 Testing Generate Endpoint (Detailed)")
    print("=" * 45)
    
    payload = {
        "query": "Show me the available tables in the database",
        "include_charts": False,
        "chat_history": []
    }
    
    try:
        print(f"Request URL: http://127.0.0.1:8000/api/v1/text2sql/generate")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Send request with detailed headers
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Origin': 'http://127.0.0.1:8000',
            'User-Agent': 'FastAPI Test Client'
        }
        
        start_time = time.time()
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/text2sql/generate',
            json=payload,
            headers=headers,
            timeout=30
        )
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📊 Response Details:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {duration:.2f}s")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Generate endpoint SUCCESS")
            print(f"Success: {result.get('success', False)}")
            print(f"Response: {result.get('response', 'No response')[:200]}...")
            
            # Check if SQL was generated
            sql_results = result.get('sql_results', [])
            if sql_results:
                print(f"SQL Results: {len(sql_results)} results")
                for i, sql_result in enumerate(sql_results[:2]):
                    print(f"  SQL {i+1}: {sql_result.get('query', 'No query')[:100]}...")
            else:
                print("No SQL results returned")
                
            return True, result
        else:
            print(f"❌ Generate endpoint FAILED")
            print(f"Error: {response.text}")
            return False, None
            
    except requests.exceptions.Timeout:
        print(f"❌ Generate endpoint TIMEOUT (30s)")
        return False, None
    except Exception as e:
        print(f"❌ Generate endpoint ERROR: {type(e).__name__}: {e}")
        return False, None

def test_execute_endpoint_detailed():
    """Test the execute endpoint in detail"""
    print("\n🔍 Testing Execute Endpoint (Detailed)")
    print("=" * 43)
    
    payload = {
        "sql_query": "SELECT TOP 5 TABLE_NAME FROM INFORMATION_SCHEMA.TABLES",
        "validate_only": False,
        "include_validation": True
    }
    
    try:
        print(f"Request URL: http://127.0.0.1:8000/api/v1/text2sql/execute")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Origin': 'http://127.0.0.1:8000'
        }
        
        start_time = time.time()
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/text2sql/execute',
            json=payload,
            headers=headers,
            timeout=30
        )
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📊 Response Details:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {duration:.2f}s")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Execute endpoint SUCCESS")
            print(f"Success: {result.get('success', False)}")
            print(f"Row Count: {result.get('row_count', 0)}")
            print(f"Execution Time: {result.get('execution_time', 0):.2f}s")
            return True, result
        else:
            print(f"❌ Execute endpoint FAILED")
            print(f"Error: {response.text}")
            return False, None
            
    except requests.exceptions.Timeout:
        print(f"❌ Execute endpoint TIMEOUT (30s)")
        return False, None
    except Exception as e:
        print(f"❌ Execute endpoint ERROR: {type(e).__name__}: {e}")
        return False, None

def test_integration_flow():
    """Test the integration between generate and execute"""
    print("\n🔍 Testing Generate -> Execute Integration")
    print("=" * 47)
    
    # Step 1: Generate SQL from natural language
    print("Step 1: Generate SQL from natural language")
    generate_payload = {
        "query": "Show me information about tables in the database",
        "include_charts": False,
        "chat_history": []
    }
    
    try:
        gen_response = requests.post(
            'http://127.0.0.1:8000/api/v1/text2sql/generate',
            json=generate_payload,
            timeout=30
        )
        
        if gen_response.status_code != 200:
            print(f"❌ Generate step failed: {gen_response.text}")
            return False
            
        gen_result = gen_response.json()
        print(f"✅ Generate step successful")
        
        # Extract SQL from generate response
        sql_results = gen_result.get('sql_results', [])
        if not sql_results:
            print("❌ No SQL generated from natural language")
            return False
            
        generated_sql = sql_results[0].get('query')
        if not generated_sql:
            print("❌ No SQL query found in results")
            return False
            
        print(f"Generated SQL: {generated_sql[:100]}...")
        
        # Step 2: Execute the generated SQL
        print("\nStep 2: Execute the generated SQL")
        execute_payload = {
            "sql_query": generated_sql,
            "validate_only": False,
            "include_validation": True
        }
        
        exec_response = requests.post(
            'http://127.0.0.1:8000/api/v1/text2sql/execute',
            json=execute_payload,
            timeout=30
        )
        
        if exec_response.status_code != 200:
            print(f"❌ Execute step failed: {exec_response.text}")
            return False
            
        exec_result = exec_response.json()
        print(f"✅ Execute step successful")
        print(f"Row count: {exec_result.get('row_count', 0)}")
        
        print("\n🎉 INTEGRATION SUCCESS: Generate -> Execute flow working!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {type(e).__name__}: {e}")
        return False

def test_swagger_ui_simulation():
    """Simulate exactly what Swagger UI does"""
    print("\n🔍 Simulating Swagger UI Request Flow")
    print("=" * 42)
    
    # Step 1: OPTIONS preflight request (what browser does first)
    print("Step 1: CORS Preflight (OPTIONS)")
    try:
        options_response = requests.options(
            'http://127.0.0.1:8000/api/v1/text2sql/generate',
            headers={
                'Origin': 'http://127.0.0.1:8000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=10
        )
        print(f"OPTIONS Status: {options_response.status_code}")
        
        if options_response.status_code != 200:
            print(f"❌ CORS preflight failed!")
            return False
            
    except Exception as e:
        print(f"❌ CORS preflight error: {e}")
        return False
    
    # Step 2: Actual POST request (what Swagger UI does after preflight)
    print("Step 2: Actual POST Request")
    payload = {
        "query": "What tables exist?",
        "include_charts": False,
        "chat_history": []
    }
    
    # Exact headers that Swagger UI sends
    swagger_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'http://127.0.0.1:8000',
        'Referer': 'http://127.0.0.1:8000/docs',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin'
    }
    
    try:
        post_response = requests.post(
            'http://127.0.0.1:8000/api/v1/text2sql/generate',
            json=payload,
            headers=swagger_headers,
            timeout=30
        )
        
        print(f"POST Status: {post_response.status_code}")
        print(f"Response headers: {dict(post_response.headers)}")
        
        if post_response.status_code == 200:
            print("✅ Swagger UI simulation SUCCESSFUL!")
            result = post_response.json()
            print(f"Success: {result.get('success', False)}")
            return True
        else:
            print(f"❌ Swagger UI simulation FAILED: {post_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Swagger UI simulation error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Comprehensive Endpoint Integration Test")
    print("=" * 60)
    
    # Check if server is running
    if not check_server_status():
        exit(1)
    
    # Test individual endpoints
    generate_ok, generate_result = test_generate_endpoint_detailed()
    execute_ok, execute_result = test_execute_endpoint_detailed()
    
    # Test integration
    integration_ok = test_integration_flow()
    
    # Test Swagger UI simulation
    swagger_ok = test_swagger_ui_simulation()
    
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS:")
    print(f"Generate Endpoint: {'✅ WORKING' if generate_ok else '❌ FAILED'}")
    print(f"Execute Endpoint: {'✅ WORKING' if execute_ok else '❌ FAILED'}")
    print(f"Integration Flow: {'✅ WORKING' if integration_ok else '❌ FAILED'}")
    print(f"Swagger UI Sim: {'✅ WORKING' if swagger_ok else '❌ FAILED'}")
    
    if generate_ok and execute_ok and integration_ok and swagger_ok:
        print("\n🎉 ALL TESTS PASSED! Endpoints are working correctly.")
        print("If Swagger UI still shows 'Failed to fetch', try:")
        print("1. Hard refresh your browser (Ctrl+F5)")
        print("2. Clear browser cache")
        print("3. Try in an incognito window")
    else:
        print("\n⚠️  Some issues detected. Check the detailed output above.")
        
        if not generate_ok:
            print("- Generate endpoint has issues")
        if not execute_ok:
            print("- Execute endpoint has issues")
        if not integration_ok:
            print("- Integration between endpoints has issues")
        if not swagger_ok:
            print("- Swagger UI compatibility has issues")
