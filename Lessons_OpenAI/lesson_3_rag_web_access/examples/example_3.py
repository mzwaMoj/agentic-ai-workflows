#!/usr/bin/env python

import requests
import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

print(
    requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={
            "X-Subscription-Token": os.environ.get("BRAVE_SEARCH_API_KEY"),
        },
        params={
            "q": "greek restaurants in san francisco",
            "count": 20,
            "country": "us",
            "search_lang": "en",
        },
    ).json()
)

# from serpapi import GoogleSearch
# import json

# # Get SerpAPI key from environment
# SERPAPI_KEY = os.environ.get("SERPAPI_API_KEY")

# if not SERPAPI_KEY:
#     print("⚠️ SERPAPI_API_KEY not found in .env file")
#     print("Please add SERPAPI_API_KEY=your_key_here to your .env file")
#     print("Get your key from: https://serpapi.com/")
# else:
#     params = {
#       "engine": "google",
#       "q": "Coffee",
#       "api_key": SERPAPI_KEY
#     }
    
#     try:
#         search = GoogleSearch(params)
#         results = search.get_dict()
        
#         # Check if there's an error in the response
#         if "error" in results:
#             print("❌ SerpAPI Error:")
#             print(json.dumps(results, indent=2))
#         elif "organic_results" in results:
#             print("✅ Search Results for 'Coffee':")
#             print("=" * 60)
#             organic_results = results["organic_results"]
            
#             # Print only important fields from first 5 results
#             for i, result in enumerate(organic_results[:5], 1):
#                 print(f"\n{i}. {result.get('title', 'No title')}")
#                 print(f"   URL: {result.get('link', 'No link')}")
#                 print(f"   Snippet: {result.get('snippet', 'No snippet')[:150]}...")
                
#             print("\n" + "=" * 60)
#             print(f"Total results shown: {len(organic_results[:5])}")
#         else:
#             print("⚠️ Unexpected response format:")
#             print(json.dumps(results, indent=2))
            
#     except Exception as e:
#         print(f"❌ Exception occurred: {str(e)}")