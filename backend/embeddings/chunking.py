"""
Document chunking and preprocessing utilities for the RAG Chatbot
"""
import re
from typing import List, Dict, Any


class DocumentChunker:
    """Class wrapper for chunking operations"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, max_length: int = None) -> List[str]:
        """Chunk text with optional override of max_length"""
        chunk_size = max_length if max_length else self.chunk_size
        return chunk_text(text, chunk_size, self.overlap)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks

    Args:
        text: Input text to be chunked
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Ensure we don't cut in the middle of a sentence if possible
        if end < len(text):
            sentence_end = chunk.rfind('. ')
            if sentence_end > chunk_size // 2:
                chunk = text[start:start + sentence_end + 2]
                end = start + sentence_end + 2

        chunks.append(chunk)
        start = end - overlap if end < len(text) else len(text)

    # Filter out very small chunks
    chunks = [chunk for chunk in chunks if len(chunk.strip()) > 20]
    return chunks


def preprocess_text(text: str) -> str:
    """
    Preprocess text before chunking

    Args:
        text: Input text to preprocess

    Returns:
        Preprocessed text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove special characters that might interfere with embeddings
    text = re.sub(r'[^\w\s\.\-_,!?;:\'"/\[\](){}]', ' ', text)

    # Normalize whitespace
    text = ' '.join(text.split())

    return text


def extract_metadata_from_path(file_path: str) -> Dict[str, Any]:
    """
    Extract metadata from file path

    Args:
        file_path: Path to the document file

    Returns:
        Dictionary containing metadata
    """
    import os

    path_parts = file_path.split(os.sep)

    # Extract relative path, title, and section from path
    relative_path = file_path
    title = os.path.basename(file_path)
    if title.endswith('.md') or title.endswith('.txt'):
        title = title[:-3]  # Remove .md or .txt extension

    # Try to determine section from path structure
    section = "unknown"
    if len(path_parts) >= 2:
        # Look for module directories in the path
        for part in path_parts:
            if 'module' in part.lower():
                section = part
                break

    return {
        "relative_path": relative_path,
        "title": title,
        "section": section
    }