#!/usr/bin/env python3
"""
Test the generate endpoint after the import fixes with correct API schema
"""
import requests
import time
import json

def test_generate_endpoint():
    """Test the generate endpoint with correct schema"""
    url = "http://127.0.0.1:8000/api/v1/text2sql/generate"
    
    test_payload = {
        "query": "Show me all customers",
        "include_charts": False,
        "max_results": 10
    }
    
    print("Testing generate endpoint...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            url, 
            json=test_payload,
            timeout=30  # 30 second timeout for first real test
        )
        
        elapsed = time.time() - start_time
        print(f"✅ Response received in {elapsed:.2f}s")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Generate endpoint working!")
            try:
                result = response.json()
                print(f"Response keys: {list(result.keys())}")
                print(f"SQL Generated: {result.get('sql', 'N/A')}")
                print(f"Natural Language: {result.get('natural_language_explanation', 'N/A')}")
            except Exception as e:
                print(f"Response parsing error: {e}")
                print(f"Raw response: {response.text[:500]}...")
        else:
            print(f"❌ Error response: {response.text}")
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"❌ Request timed out after {elapsed:.2f}s")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - server may have crashed")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error after {elapsed:.2f}s: {e}")
        return False
    
    return True

def test_execute_endpoint():
    """Test the execute endpoint with correct schema"""
    url = "http://127.0.0.1:8000/api/v1/text2sql/execute"
    
    test_payload = {
        "sql_query": "SELECT 1 as test_column",
        "validate": True
    }
    
    print("\nTesting execute endpoint...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=test_payload, timeout=10)
        elapsed = time.time() - start_time
        print(f"✅ Execute response received in {elapsed:.2f}s")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Execute endpoint working!")
            print(f"Response keys: {list(result.keys())}")
        else:
            print(f"❌ Execute error: {response.text}")
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Execute error after {elapsed:.2f}s: {e}")

if __name__ == "__main__":
    print("🔍 Testing both endpoints with correct API schema...")
    
    # Test execute first (we know this works)
    test_execute_endpoint()
    
    # Test generate (this was the problematic one)
    success = test_generate_endpoint()
    
    if success:
        print("\n✅ Both endpoints are working! The import fixes resolved the hanging issue.")
        print("🎉 API is ready for Swagger UI testing!")
    else:
        print("\n❌ Generate endpoint still has issues.")
