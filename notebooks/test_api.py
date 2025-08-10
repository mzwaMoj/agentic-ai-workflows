import ssl
import urllib3
import httpx

# Disable SSL certificate verification globally (for development only!)
ssl._create_default_https_context = ssl._create_unverified_context

# For requests and urllib3, suppress warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from openai import AzureOpenAI
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Get the Keys
API_KEY = os.environ.get("AZURE_OPENAI_KEY") 
API_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
API_VERSION = os.environ.get("AZURE_OPENAI_VERSION")
MODEL = os.environ.get("AZURE_OPENAI_MODEL")

# Create httpx client with SSL verification disabled
http_client = httpx.Client(verify=True)

# Create client with custom http_client
client = AzureOpenAI(
    default_headers={"Ocp-Apim-Subscription-Key": API_KEY},
    api_key=API_KEY,
    azure_endpoint=API_ENDPOINT,
    api_version=API_VERSION,
    http_client=http_client
)

try:
    # Create completions
    completion = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,  # Use deployment name, not model name
        stream=True,
        messages=[
            {
                "role": "user",
                "content": "Tell me a long joke",
            },
        ],
    )

    print("API call successful! Response:")
    for chunk in completion:
        try:
            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="")
        except (AttributeError, IndexError):
            pass
    print("\n")  # Add newline at the end

except Exception as e:
    print(f"Error making API call: {e}")
    print(f"API Endpoint: {API_ENDPOINT}")
    print(f"API Version: {API_VERSION}")
    print(f"Deployment: {AZURE_DEPLOYMENT}")