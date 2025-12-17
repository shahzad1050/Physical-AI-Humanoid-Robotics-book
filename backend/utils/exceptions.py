"""
Custom exceptions for the RAG Chatbot
"""


class RAGException(Exception):
    """
    Base exception class for RAG Chatbot
    """
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class DocumentProcessingError(RAGException):
    """
    Exception raised when document processing fails
    """
    def __init__(self, message: str, document_path: Optional[str] = None):
        self.document_path = document_path
        super().__init__(f"Document processing error: {message}", "DOC_PROCESS_ERROR")


class QueryProcessingError(RAGException):
    """
    Exception raised when query processing fails
    """
    def __init__(self, message: str, query_id: Optional[str] = None):
        self.query_id = query_id
        super().__init__(f"Query processing error: {message}", "QUERY_PROCESS_ERROR")


class EmbeddingGenerationError(RAGException):
    """
    Exception raised when embedding generation fails
    """
    def __init__(self, message: str):
        super().__init__(f"Embedding generation error: {message}", "EMBED_GEN_ERROR")


class VectorDBError(RAGException):
    """
    Exception raised when vector database operations fail
    """
    def __init__(self, message: str):
        super().__init__(f"Vector database error: {message}", "VECTOR_DB_ERROR")


class APIConnectionError(RAGException):
    """
    Exception raised when API connections fail
    """
    def __init__(self, message: str, api_name: Optional[str] = None):
        self.api_name = api_name
        super().__init__(f"API connection error: {message}", "API_CONN_ERROR")