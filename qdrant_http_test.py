import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('backend/.env')

# Get Qdrant configuration from environment variables
cluster_endpoint = os.getenv('QDRANT_CLUSTER_ENDPOINT', '')
qdrent_token = os.getenv('QDRANT_API_KEY')

# Ensure we have the required environment variables
if not cluster_endpoint or not qdrent_token:
    raise ValueError("Qdrant Cluster Endpoint or QDRANT_API_KEY not found in environment variables")

print(f"Connecting to Qdrant at: {cluster_endpoint}")

# Use the HTTP API to test the connection
headers = {
    'api-key': qdrent_token,
    'Content-Type': 'application/json'
}

try:
    # Test the connection by getting collections via HTTP API
    response = requests.get(f"{cluster_endpoint}/collections", headers=headers)

    if response.status_code == 200:
        collections = response.json()
        print("Successfully connected to Qdrant!")
        print(f"Available collections: {collections}")
    else:
        print(f"Error connecting to Qdrant: {response.status_code} - {response.text}")

except Exception as e:
    print(f"Error connecting to Qdrant: {e}")