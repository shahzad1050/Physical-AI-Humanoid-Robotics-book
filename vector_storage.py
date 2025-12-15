"""
Vector Database Storage Script for RAG Chatbot System
This script stores embedded documents in a Neon Postgres database using pgvector.
"""

import os
import json
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import Json
from pgvector.psycopg2 import register_vector
import numpy as np
from embed_docs import DocumentationEmbedder
from dotenv import load_dotenv

class VectorDBStorage:
    """
    A class to handle storage of embeddings in a Neon Postgres database.
    """

    def __init__(self, table_name: str = "docusaurus_docs"):
        # Initialize Postgres connection
        load_dotenv()
        self.conn = psycopg2.connect(os.getenv('NEON_CONNECTION_STRING'))
        self.table_name = table_name

    def create_table(self, vector_size: int = 1024):
        """
        Create a table in the Postgres database for storing document embeddings.
        """
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            register_vector(self.conn)
            cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id SERIAL PRIMARY KEY,
                doc_id VARCHAR(255),
                content TEXT,
                metadata JSONB,
                embedding VECTOR({vector_size})
            )
            """)
            self.conn.commit()
            print(f"Table '{self.table_name}' is ready.")

    def store_embeddings(self, embedded_docs: List[Dict[str, Any]]):
        """
        Store embedded documents in the Postgres table.
        """
        if not embedded_docs:
            print("No documents to store")
            return

        print(f"Storing {len(embedded_docs)} embedded documents in Postgres...")

        with self.conn.cursor() as cur:
            register_vector(self.conn)
            for i, doc in enumerate(embedded_docs):
                cur.execute(
                    f"INSERT INTO {self.table_name} (doc_id, content, metadata, embedding) VALUES (%s, %s, %s, %s)",
                    (doc.get('id', f'doc_{i}'), doc['content'], Json(doc['metadata']), np.array(doc['embedding']))
                )
        self.conn.commit()

        print(f"Successfully stored {len(embedded_docs)} documents in table '{self.table_name}'")

    def get_table_info(self):
        """
        Get information about the table.
        """
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            count = cur.fetchone()[0]
            return {"table_name": self.table_name, "points_count": count}

def main():
    """
    Main function to demonstrate vector storage.
    """
    print("Postgres Vector Database Storage")
    print("=" * 40)

    try:
        # Initialize the vector database storage
        vector_db = VectorDBStorage(table_name="docusaurus_docs")

        # Create table
        vector_db.create_table()

        # Check if we have embedded documents to store
        print("Checking for embedded documents...")

        # Try to embed some documentation content
        embedder = DocumentationEmbedder()

        # Look for documentation directory
        docs_dirs = [
            "./physical-ai-humanoid-robotics/docs",
        ]

        docs_dir = None
        for possible_dir in docs_dirs:
            if os.path.exists(possible_dir):
                docs_dir = possible_dir
                break

        if docs_dir:
            print(f"Found documentation directory: {docs_dir}")
            print("Embedding documentation content...")

            # Embed documentation
            embedded_docs = embedder.embed_documentation_directory(docs_dir)

            if embedded_docs:
                print(f"Storing {len(embedded_docs)} embedded documents...")
                vector_db.store_embeddings(embedded_docs)

                # Show table info
                info = vector_db.get_table_info()
                if info:
                    print(f"Table info: {info}")
            else:
                print("No documents found to embed.")
        else:
            print("Documentation directory not found.")

        print(f"\nVector storage completed!")
        print(f"Documents are now stored in Postgres table '{vector_db.table_name}'")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred during vector storage: {e}")

if __name__ == "__main__":
    main()