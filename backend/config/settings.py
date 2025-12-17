"""
Settings configuration for the RAG Chatbot
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # API Keys
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    cohere_api_key: str = Field(..., env="COHERE_API_KEY")

    # Qdrant Configuration
    qdrant_url: Optional[str] = Field(default=None, env="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, env="QDRANT_API_KEY")

    # Neon Postgres Configuration
    neon_connection_string: str = Field(..., env="NEON_CONNECTION_STRING")

    # Application Configuration
    app_name: str = "RAG Chatbot API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Embedding Configuration
    embedding_model: str = "embed-multilingual-v3.0"
    embedding_input_type: str = "search_query"
    embedding_dimensions: int = 1024  # Standard for Cohere multilingual model

    # RAG Configuration
    default_top_k: int = 5
    max_top_k: int = 10
    min_similarity_score: float = 0.3

    # Document Processing
    chunk_size: int = 500
    chunk_overlap: int = 50

    # API Configuration
    backend_url: str = "http://localhost:8000"
    cors_origins: str = "*"  # In production, specify exact origins

    # File paths
    embedded_docs_path: str = "embedded_docs.json"
    docs_directory: str = "../physical-ai-humanoid-robotics/docs"

    # Performance
    response_timeout: int = 30  # seconds
    embedding_timeout: int = 10  # seconds

    class Config:
        env_file = ".env" if os.path.exists(".env") else None
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create a singleton instance of settings
settings = Settings()

# Validate required settings are present
if not settings.openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

if not settings.cohere_api_key:
    raise ValueError("COHERE_API_KEY environment variable is required")

if not settings.neon_connection_string: # NEW
    raise ValueError("NEON_CONNECTION_STRING environment variable is required")