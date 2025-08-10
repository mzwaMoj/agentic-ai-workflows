"""
Simple embedding test to identify hanging issue.
Writes output to file for clear results.
"""

import os
import time
import sys
import traceback
from datetime import datetime

# Output file
OUTPUT_FILE = "vector_test_results.txt"

def write_log(message):
    """Write to both console and file."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    
    print(log_message)
    
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")

def clear_log():
    """Clear the log file."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("Vector Service Test Results\n")
        f.write("=" * 50 + "\n")

def test_embedding_generation():
    """Test embedding generation - the suspected hanging point."""
    write_log("🧪 TESTING: Embedding Generation")
    
    try:
        # Setup environment
        from dotenv import load_dotenv, find_dotenv
        load_dotenv(find_dotenv())
        write_log("✅ Environment loaded")
        
        # Import required modules
        import httpx
        from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
        write_log("✅ Imports successful")
        
        # Get configuration
        endpoint = os.environ.get("AZURE_OPENAI_EMBEDDING_ENDPOINT")
        api_key = os.environ.get("AZURE_OPENAI_EMBEDDING_KEY") 
        deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
        api_version = os.environ.get("AZURE_OPENAI_EMBEDDING_API_VERSION", "2023-05-15")
        
        write_log(f"✅ Configuration loaded - Endpoint: {endpoint[:50]}...")
        write_log(f"✅ Deployment: {deployment}")
        
        # Create HTTP client
        http_client = httpx.Client(verify=False)
        write_log("✅ HTTP client created")
        
        # Create embedding model
        write_log("🔧 Creating embedding model...")
        embedding_model = AzureOpenAIEmbedding(
            deployment_name=deployment,
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version,
            http_client=http_client
        )
        write_log("✅ Embedding model created successfully")
        
        # Test embedding generation
        test_text = "customer information"
        write_log(f"🚀 Generating embedding for: '{test_text}'")
        write_log("⚠️  CRITICAL POINT: This is where hanging typically occurs...")
        
        start_time = time.time()
        embedding = embedding_model.get_text_embedding(test_text)
        end_time = time.time()
        
        write_log(f"🎉 SUCCESS: Embedding generated in {end_time - start_time:.2f} seconds")
        write_log(f"✅ Embedding dimensions: {len(embedding)}")
        write_log("🎯 CONCLUSION: No hanging detected - embedding generation works!")
        
        return True
        
    except Exception as e:
        write_log(f"❌ ERROR: {str(e)}")
        write_log(f"❌ TRACEBACK: {traceback.format_exc()}")
        return False

def main():
    """Run the embedding test."""
    clear_log()
    write_log("Starting Vector Service Embedding Test")
    write_log("=" * 50)
    
    success = test_embedding_generation()
    
    write_log("=" * 50)
    if success:
        write_log("🎉 TEST RESULT: SUCCESS - No hanging detected!")
        write_log("💡 The vector service embedding generation works correctly.")
        write_log("💡 If the API still hangs, the issue is elsewhere (e.g., LlamaIndex query).")
    else:
        write_log("❌ TEST RESULT: FAILED - Embedding generation has issues.")
    
    write_log(f"📝 Full results saved to: {OUTPUT_FILE}")
    write_log("Test completed!")

if __name__ == "__main__":
    main()
