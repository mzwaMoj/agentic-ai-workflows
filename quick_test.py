import requests
import json

print("Testing the /api/v1/text2sql/generate endpoint...")

payload = {"query": "Show me top ten customers by account balance"}
url = "http://127.0.0.1:8000/api/v1/text2sql/generate"

try:
    response = requests.post(url, json=payload, timeout=200)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text[:500]}...")
    
    if response.status_code == 200:
        print("✅ SUCCESS - Generate endpoint working!")
    else:
        print("❌ FAILED - Generate endpoint returned error")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
