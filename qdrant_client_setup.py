import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('backend/.env')

# Get Qdrant configuration from environment variables
cluster_endpoint = os.getenv('QDRANT_CLUSTER_ENDPOINT', '')
qdrent_token = os.getenv('QDRANT_API_KEY')

# Ensure we have the required environment variables
if not cluster_endpoint or not qdrent_token:
    raise ValueError("Qdrant Cluster Endpoint or QDRANT_API_KEY not found in environment variables")

# Extract the host from the cluster endpoint URL (remove https:// prefix)
qdrant_host = cluster_endpoint.replace('https://', '').replace('http://', '')

# Construct the full URL with the proper port
full_url = f"https://{qdrant_host}:6333"
qdrant_api_key = qdrent_token

print(f"Connecting to Qdrant at: {full_url}")

# Initialize the Qdrant client
try:
    qdrant_client = QdrantClient(
        url=full_url,
        api_key=qdrant_api_key,
    )

    # Test the connection by getting collections
    collections = qdrant_client.get_collections()
    print("Successfully connected to Qdrant!")
    print(f"Available collections: {collections}")
except Exception as e:
    print(f"Error connecting to Qdrant: {e}")
    print("Attempting to connect with alternative method...")

    # Alternative: Try using the api_key directly without the URL scheme issues
    try:
        # Just use the host without https:// prefix in URL, and specify https=True
        qdrant_client = QdrantClient(
            host=qdrant_host,
            api_key=qdrant_api_key,
            https=True,
            port=6333
        )

        collections = qdrant_client.get_collections()
        print("Successfully connected to Qdrant using alternative method!")
        print(f"Available collections: {collections}")
    except Exception as e2:
        print(f"Error with alternative connection method: {e2}")