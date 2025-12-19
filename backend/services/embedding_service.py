import os
import google.generativeai as genai
import psycopg2
from psycopg2 import extras
import numpy as np
from dotenv import load_dotenv

from backend.config import settings

load_dotenv()

class EmbeddingService:
    """
    Service to handle embedding and storing of documents.
    """
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.conn = psycopg2.connect(settings.neon_connection_string)
        from pgvector.psycopg2 import register_vector
        register_vector(self.conn)
        self.table_name = "documents"

    def embed_and_store(self, chunks, metadata):
        """
        Embeds a list of text chunks and stores them in the database.
        """
        if not chunks:
            return

        # --- Embed chunks ---
        embeddings = self.embed_texts(chunks)

        # --- Store in database ---
        with self.conn.cursor() as cur:
            for i, chunk in enumerate(chunks):
                # Add chunk index to metadata
                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_index"] = i
                
                cur.execute(
                    f"INSERT INTO {self.table_name} (content, metadata, embedding) VALUES (%s, %s, %s)",
                    (chunk, extras.Json(chunk_metadata), np.array(embeddings[i]))
                )
        self.conn.commit()

    def embed_texts(self, texts):
        """
        Embeds a list of texts using the Google Generative AI client.
        """
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=texts,
            task_type="retrieval_document"
        )
        return result['embedding']

    def embed_text(self, text):
        """
        Embeds a single text using the Google Generative AI client.
        """
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_query"
        )
        return result['embedding']

    def __del__(self):
        """
        Destructor to close the database connection.
        """
        if self.conn:
            self.conn.close()
