import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('backend/.env')

# Get Qdrant configuration from environment variables
cluster_endpoint = os.getenv('QDRANT_CLUSTER_ENDPOINT', '')
qdrant_api_key = os.getenv('QDRANT_API_KEY')

# Ensure we have the required environment variables
if not cluster_endpoint or not qdrant_api_key:
    raise ValueError("Qdrant Cluster Endpoint or QDRANT_API_KEY not found in environment variables")

print(f"Qdrant Cluster Endpoint: {cluster_endpoint}")
print(f"QDRANT API Key available: {qdrant_api_key is not None}")

# For environments where the QdrantClient import works, you would use:
print("\nFor proper QdrantClient usage (when protobuf compatibility is resolved):")
print("qdrant_client = QdrantClient(")
print(f"    url=\"{cluster_endpoint}:6333\",")
print(f"    api_key=\"{qdrant_api_key}\",")
print(")")
print("\nprint(qdrant_client.get_collections())")

# For immediate testing without the problematic import, we can use the HTTP API:
print("\nFor immediate testing, using HTTP API (as demonstrated in qdrant_http_test.py):")
print("import requests")
print()
print("headers = {")
print("    'api-key': os.getenv('QDRANT_API_KEY'),")
print("    'Content-Type': 'application/json'")
print("}")
print()
print("response = requests.get(f\"{cluster_endpoint}/collections\", headers=headers)")
print("print(response.json())")