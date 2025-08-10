"""
Test the text2sql/generate endpoint to diagnose CORS issues.
"""
import requests
import json
import time

def test_cors_preflight():
    """Test CORS preflight request"""
    print("🔍 Testing CORS Preflight Request")
    print("=" * 50)
    
    try:
        # Send OPTIONS request (CORS preflight)
        response = requests.options(
            'http://127.0.0.1:8000/api/v1/text2sql/generate',
            headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type',
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Check CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials'),
        }
        
        print(f"CORS Headers: {cors_headers}")
        
        if response.status_code == 200:
            print("✅ CORS preflight successful")
            return True
        else:
            print(f"❌ CORS preflight failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ CORS preflight error: {type(e).__name__}: {e}")
        return False

def test_generate_endpoint():
    """Test the actual generate endpoint"""
    print("\n🔍 Testing text2sql/generate Endpoint")
    print("=" * 50)
    
    payload = {
        "query": "What tables are available in the database?",
        "include_charts": False,
        "chat_history": []
    }
    
    try:
        print(f"Sending POST request to: http://127.0.0.1:8000/api/v1/text2sql/generate")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        start_time = time.time()
        
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/text2sql/generate',
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'Origin': 'http://localhost:3000',  # Simulate browser request
            },
            timeout=30
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✅ Request completed in {duration:.2f}s")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            print(f"Response: {result.get('response', 'No response')[:100]}...")
            if result.get('sql_results'):
                print(f"SQL Results: {len(result.get('sql_results', []))} results")
            return True
        else:
            print(f"❌ Error Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after 30 seconds")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - make sure the API server is running")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        return False

def test_server_health():
    """Test if server is running and healthy"""
    print("🔍 Testing Server Health")
    print("=" * 30)
    
    try:
        response = requests.get('http://127.0.0.1:8000/api/v1/health/', timeout=5)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Health status: {response.json()}")
            return True
        else:
            print(f"Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Server health check failed: {e}")
        return False

def test_swagger_access():
    """Test if Swagger UI is accessible"""
    print("\n🔍 Testing Swagger UI Access")
    print("=" * 35)
    
    try:
        response = requests.get('http://127.0.0.1:8000/docs', timeout=5)
        print(f"Swagger UI: {response.status_code}")
        if response.status_code == 200:
            print("✅ Swagger UI is accessible")
            return True
        else:
            print(f"❌ Swagger UI not accessible: {response.text[:100]}...")
            return False
    except Exception as e:
        print(f"❌ Swagger UI access failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CORS and Generate Endpoint Diagnosis")
    print("=" * 60)
    
    # Test server health first
    health_ok = test_server_health()
    
    if not health_ok:
        print("❌ Server is not healthy - check if API is running")
        exit(1)
    
    # Test Swagger access
    swagger_ok = test_swagger_access()
    
    # Test CORS preflight
    cors_ok = test_cors_preflight()
    
    # Test the actual endpoint
    generate_ok = test_generate_endpoint()
    
    print("\n" + "=" * 60)
    print("📊 Diagnosis Results:")
    print(f"Server Health: {'✅ OK' if health_ok else '❌ FAIL'}")
    print(f"Swagger UI: {'✅ OK' if swagger_ok else '❌ FAIL'}")
    print(f"CORS Preflight: {'✅ OK' if cors_ok else '❌ FAIL'}")
    print(f"Generate Endpoint: {'✅ OK' if generate_ok else '❌ FAIL'}")
    
    if not cors_ok:
        print("\n🔧 CORS Issue Detected!")
        print("Recommendations:")
        print("1. Check CORS_ORIGINS setting in .env file")
        print("2. Verify CORSMiddleware configuration in main.py")
        print("3. Check if server is binding to correct host/port")
    
    if not generate_ok:
        print("\n🔧 Generate Endpoint Issue Detected!")
        print("Check the error details above for specific issues.")
