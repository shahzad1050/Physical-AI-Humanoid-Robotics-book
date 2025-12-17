"""
Embedding pipeline for the RAG Chatbot
This script processes documentation files, generates embeddings, and stores them in a PostgreSQL database.
"""
import os
import json
import logging
from typing import List, Dict, Any
from pathlib import Path

import psycopg2
from pgvector.psycopg2 import register_vector

from ..services import EmbeddingService
from ..embeddings.chunking import chunk_text
from ..utils import get_logger
from ..config import settings


logger = get_logger(__name__)
TABLE_NAME = "documents"


def _check_and_create_table(conn):
    """
    Create a table in the Postgres database for storing document embeddings if it doesn't exist.
    """
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id SERIAL PRIMARY KEY,
            content TEXT,
            metadata JSONB,
            embedding VECTOR(1024)
        )
        """)
        conn.commit()
        logger.info(f"Table '{TABLE_NAME}' is ready.")


def load_documentation_files(docs_path: str = "physical-ai-humanoid-robotics/docs") -> List[Dict[str, Any]]:
    """
    Load documentation files from the specified directory

    Args:
        docs_path: Path to documentation directory

    Returns:
        List of documents with content and metadata
    """
    documents = []
    docs_dir = Path(docs_path)

    if not docs_dir.exists():
        logger.warning(f"Documentation directory does not exist: {docs_path}")
        return documents

    for file_path in docs_dir.rglob("*.md"):  # Process markdown files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            relative_path = str(file_path.relative_to(docs_dir))
            document = {
                'content': content,
                'metadata': {
                    'relative_path': relative_path,
                    'source_file': str(file_path),
                    'file_size': len(content)
                }
            }
            documents.append(document)
            logger.info(f"Loaded document: {relative_path}")

        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")

    return documents


def process_documentation_chunks(documents: List[Dict[str, Any]],
                               chunk_size: int = 500,
                               overlap: int = 50) -> List[Dict[str, Any]]:
    """
    Process documentation into chunks for embedding

    Args:
        documents: List of documents to process
        chunk_size: Size of each text chunk
        overlap: Overlap between chunks

    Returns:
        List of document chunks with metadata
    """
    chunks = []

    for doc_idx, doc in enumerate(documents):
        content = doc['content']
        metadata = doc['metadata']

        # Split content into chunks
        content_chunks = chunk_text(content, chunk_size=chunk_size, overlap=overlap)

        for chunk_idx, chunk in enumerate(content_chunks):
            chunk_doc = {
                'id': f"{metadata['relative_path']}_chunk_{chunk_idx}",
                'content': chunk,
                'metadata': {
                    **metadata,
                    'chunk_index': chunk_idx,
                    'total_chunks': len(content_chunks)
                }
            }
            chunks.append(chunk_doc)

    logger.info(f"Processed {len(documents)} documents into {len(chunks)} chunks")
    return chunks


def embed_document_chunks(embedding_service: EmbeddingService,
                         chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate embeddings for document chunks

    Args:
        embedding_service: Embedding service instance
        chunks: List of document chunks to embed

    Returns:
        List of document chunks with embeddings
    """
    logger.info(f"Generating embeddings for {len(chunks)} chunks...")

    # Extract content for batch processing
    chunk_contents = [chunk['content'] for chunk in chunks]

    # Generate embeddings in batches to avoid rate limits
    batch_size = 10  # Adjust based on API limits
    embedded_chunks = []

    for i in range(0, len(chunk_contents), batch_size):
        batch_contents = chunk_contents[i:i + batch_size]
        batch_chunks = chunks[i:i + batch_size]

        try:
            # Generate embeddings for the batch
            embeddings = embedding_service.embed_texts(batch_contents)

            # Add embeddings to chunks
            for j, chunk in enumerate(batch_chunks):
                chunk_with_embedding = chunk.copy()
                chunk_with_embedding['embedding'] = embeddings[j]
                embedded_chunks.append(chunk_with_embedding)

            logger.info(f"Embedded batch {i//batch_size + 1}/{(len(chunk_contents) - 1)//batch_size + 1}")

        except Exception as e:
            logger.error(f"Error embedding batch {i//batch_size + 1}: {str(e)}")
            # Skip problematic chunks but continue with others
            continue

    logger.info(f"Successfully embedded {len(embedded_chunks)} chunks")
    return embedded_chunks


def save_embeddings_to_db(embedded_chunks: List[Dict[str, Any]]):
    """
    Save embedded chunks to the PostgreSQL database.
    """
    conn = None
    try:
        conn = psycopg2.connect(settings.neon_connection_string)
        register_vector(conn)
        _check_and_create_table(conn)

        with conn.cursor() as cur:
            # Clear existing data
            cur.execute(f"TRUNCATE TABLE {TABLE_NAME} RESTART IDENTITY")
            logger.info(f"Cleared existing data from table '{TABLE_NAME}'.")

            for chunk in embedded_chunks:
                cur.execute(
                    f"INSERT INTO {TABLE_NAME} (content, metadata, embedding) VALUES (%s, %s, %s)",
                    (chunk['content'], json.dumps(chunk['metadata']), chunk['embedding'])
                )
            conn.commit()
        logger.info(f"Successfully saved {len(embedded_chunks)} chunks to the database.")

    except Exception as e:
        logger.error(f"Error saving embeddings to database: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def run_embedding_pipeline(docs_path: str = "physical-ai-humanoid-robotics/docs",
                         chunk_size: int = 500,
                         overlap: int = 50):
    """
    Run the complete embedding pipeline.
    """
    logger.info("Starting embedding pipeline...")

    try:
        documents = load_documentation_files(docs_path)
        if not documents:
            logger.warning("No documentation files found. Pipeline stopped.")
            return

        chunks = process_documentation_chunks(documents, chunk_size, overlap)
        if not chunks:
            logger.warning("No chunks generated. Pipeline stopped.")
            return

        embedding_service = EmbeddingService()
        embedded_chunks = embed_document_chunks(embedding_service, chunks)
        if not embedded_chunks:
            logger.warning("No embeddings generated. Pipeline stopped.")
            return

        save_embeddings_to_db(embedded_chunks)

        logger.info("Embedding pipeline completed successfully!")

    except Exception as e:
        logger.error(f"Error in embedding pipeline: {str(e)}")
        raise


if __name__ == "__main__":
    run_embedding_pipeline()
    print("Embedding pipeline finished.")