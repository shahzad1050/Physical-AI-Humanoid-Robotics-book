#!/usr/bin/env python
"""
Script to index documentation and populate the Postgres database with embeddings
Run this script once to index all documentation files
"""

import os
import sys
import logging
from pathlib import Path
import psycopg2
from psycopg2.extras import DictCursor
from pgvector.psycopg2 import register_vector
import numpy as np

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.config import settings
from backend.embeddings.chunking import DocumentChunker
from backend.services.embedding_service import EmbeddingService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def index_documentation():
    """
    Index all documentation files and populate the Postgres database
    """
    logger.info("Starting documentation indexing...")
    
    # Initialize services
    embedder = EmbeddingService()
    chunker = DocumentChunker()
    
    # Connect to Postgres
    conn = psycopg2.connect(settings.neon_connection_string)
    register_vector(conn)
    
    try:
        # Create table if not exists
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                metadata JSONB NOT NULL,
                embedding VECTOR(1024),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            # Create index for faster similarity search
            cur.execute("""
            CREATE INDEX IF NOT EXISTS documents_embedding_idx 
            ON documents USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
            """)
            conn.commit()
            logger.info("Database tables created successfully")
        
        # Find all markdown files in docs directory
        docs_dir = Path(settings.docs_directory)
        if not docs_dir.exists():
            logger.error(f"Documentation directory not found: {docs_dir}")
            logger.info("Using default Physical AI & Humanoid Robotics documentation structure")
            # Use a default structure
            docs_dir = Path(__file__).parent.parent.parent / "physical-ai-humanoid-robotics" / "docs"
        
        if not docs_dir.exists():
            logger.warning(f"Documentation directory not found: {docs_dir}")
            logger.info("Creating sample documents for testing...")
            sample_docs = [
                {
                    "path": "intro.md",
                    "content": """# Introduction to Physical AI & Humanoid Robotics
This is an online textbook covering physical AI and humanoid robotics concepts.
Topics include embodied AI, robotic systems, control theory, and more."""
                },
                {
                    "path": "module1/basics.md",
                    "content": """# Basics of Robotics
Robotics is the branch of technology that deals with the design, construction, and use of robots.
Key concepts include kinematics, dynamics, and control systems."""
                }
            ]
            
            # Process sample documents
            total_chunks = 0
            for doc in sample_docs:
                try:
                    chunks = chunker.chunk_text(doc['content'], max_length=settings.chunk_size)
                    
                    for chunk in chunks:
                        # Generate embedding
                        embedding = embedder.embed_text(chunk)
                        
                        # Insert into database
                        with conn.cursor() as cur:
                            cur.execute("""
                            INSERT INTO documents (content, metadata, embedding)
                            VALUES (%s, %s, %s)
                            """, (
                                chunk,
                                psycopg2.extras.Json({
                                    "relative_path": doc['path'],
                                    "title": doc['path'].split('/')[-1],
                                    "source": "sample"
                                }),
                                embedding
                            ))
                        total_chunks += 1
                        logger.info(f"Indexed chunk from {doc['path']}")
                    
                    conn.commit()
                except Exception as e:
                    logger.error(f"Error processing document {doc['path']}: {str(e)}")
                    continue
            
            logger.info(f"Indexing complete! Processed {total_chunks} chunks")
            return
        
        # Process all markdown files
        md_files = list(docs_dir.rglob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files to index")
        
        total_chunks = 0
        for md_file in md_files:
            try:
                # Read file
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Skip empty files
                if not content.strip():
                    logger.warning(f"Skipping empty file: {md_file}")
                    continue
                
                # Chunk the content
                chunks = chunker.chunk_text(content, max_length=settings.chunk_size)
                
                relative_path = str(md_file.relative_to(docs_dir))
                logger.info(f"Processing {relative_path}: {len(chunks)} chunks")
                
                for i, chunk in enumerate(chunks):
                    try:
                        # Generate embedding
                        embedding = embedder.embed_text(chunk)
                        
                        # Insert into database
                        with conn.cursor() as cur:
                            cur.execute("""
                            INSERT INTO documents (content, metadata, embedding)
                            VALUES (%s, %s, %s)
                            """, (
                                chunk,
                                psycopg2.extras.Json({
                                    "relative_path": relative_path,
                                    "title": md_file.stem,
                                    "chunk_number": i,
                                    "total_chunks": len(chunks),
                                    "source": "documentation"
                                }),
                                embedding
                            ))
                        total_chunks += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing chunk {i} from {relative_path}: {str(e)}")
                        continue
                
                conn.commit()
                logger.info(f"✓ Successfully indexed {relative_path}")
                
            except Exception as e:
                logger.error(f"Error processing file {md_file}: {str(e)}")
                continue
        
        logger.info(f"✓ Indexing complete! Processed {total_chunks} total chunks")
        
        # Print statistics
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as count FROM documents")
            result = cur.fetchone()
            logger.info(f"Database now contains {result[0]} documents")
        
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        index_documentation()
        logger.info("✓ Documentation indexing successful!")
    except Exception as e:
        logger.error(f"✗ Documentation indexing failed: {str(e)}")
        sys.exit(1)
