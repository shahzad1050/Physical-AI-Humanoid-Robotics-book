
import os
import sys
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.embeddings.chunking import DocumentChunker, preprocess_text, extract_metadata_from_path
from backend.services.embedding_service import EmbeddingService

def get_all_markdown_files(directory):
    """
    Recursively finds all markdown files in a directory.
    """
    markdown_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(root, file))
    return markdown_files

def main():
    """
    Main function to embed all docusaurus content.
    """
    print("Starting the embedding process for Docusaurus content...")

    # --- 1. Get all markdown files ---
    docs_directory = "physical-ai-humanoid-robotics/docs"
    markdown_files = get_all_markdown_files(docs_directory)
    print(f"Found {len(markdown_files)} markdown files.")

    # --- 2. Initialize the EmbeddingService ---
    try:
        embedding_service = EmbeddingService()
    except Exception as e:
        print(f"Error initializing EmbeddingService: {e}")
        return

    chunker = DocumentChunker(chunk_size=500, overlap=50)

    # --- 3. Process each file ---
    for file_path in markdown_files:
        print(f"Processing file: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            preprocessed_content = preprocess_text(content)
            chunks = chunker.chunk_text(preprocessed_content)
            metadata = extract_metadata_from_path(file_path)

            if not chunks:
                print(f"No chunks generated for file: {file_path}")
                continue

            # --- 4. Embed and store chunks ---
            embedding_service.embed_and_store(chunks, metadata)
            print(f"Successfully embedded and stored {len(chunks)} chunks.")
            time.sleep(1)

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    print("Embedding process finished.")

if __name__ == "__main__":
    main()
