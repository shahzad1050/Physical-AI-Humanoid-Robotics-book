"""
FastAPI application for the RAG Chatbot
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import re
from pydantic import BaseModel, field_validator
from typing import List, Dict, Any, Optional
import logging
import os
from dotenv import load_dotenv
from uuid import uuid4
from datetime import datetime
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Import models and services
from backend.models import DocumentChunk, Query, Response as ResponseModel
from backend.models.response import SourceReference
from backend.models.session import Session as SessionModel
from backend.services import RAGAgent
from backend.services.citation_service import CitationService
from backend.services.session_service import SessionService

from backend.utils import get_logger

# Configure logging
logger = get_logger(__name__)

# Initialize services
rag_agent = None
citation_service = None
session_service = None

def init_services():
    """Initialize services on first use"""
    global rag_agent, citation_service, session_service
    if rag_agent is None:
        try:
            rag_agent = RAGAgent()
            citation_service = CitationService()
            session_service = SessionService()
            logger.info("RAG Agent, Citation Service, and Session Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize services: {str(e)}")
            raise

# Initialize rate limiter
# limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="RAG Chatbot API",
    description="API for the RAG Chatbot for Physical AI & Humanoid Robotics Documentation",
    version="1.0.0"
)

# Set up rate limit handler (disabled for now)
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"  # Prevent clickjacking
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
        return response

# Add security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "https://shahzad1050.github.io",
        "https://physical-ai-humanoid-book-theta.vercel.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware to prevent HTTP Host Header attacks
# Disabled for testing with TestClient - enable in production
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0", "shahzad1050.github.io", "*.github.io", "testclient"],
# )

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    top_k: int = 5

    class Config:
        # Strip whitespace and limit length
        anystr_strip_whitespace = True

    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        if len(v) > 2000:  # Limit message length
            raise ValueError('Message too long, maximum 2000 characters')
        # Basic sanitization - remove potentially harmful characters
        # Note: For production, use a proper HTML sanitization library
        v = v.replace('<script', '&lt;script').replace('javascript:', 'javascript-')
        return v

    @field_validator('session_id', 'user_id', mode='before')
    @classmethod
    def validate_id(cls, v):
        if v is None:
            return v
        # Validate ID format (alphanumeric and hyphens/underscores)
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Invalid ID format')
        if len(v) > 100:  # Limit ID length
            raise ValueError('ID too long, maximum 100 characters')
        return v

    @field_validator('top_k')
    @classmethod
    def validate_top_k(cls, v):
        if v < 1 or v > 20:  # Reasonable limits for top_k
            raise ValueError('top_k must be between 1 and 20')
        return v


class DocumentContext(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]
    score: float


class SourceReferenceResponse(BaseModel):
    document_id: str
    relative_path: str
    score: float
    content_preview: str


class ChatResponse(BaseModel):
    response: str
    context_used: List[DocumentContext]
    sources: List[SourceReferenceResponse]
    query: str
    session_id: str


def _format_sources(result_sources, context_used):
    """
    Helper function to format source references from either the RAG agent result
    or by creating them from context documents using the citation service
    """
    if result_sources:
        # If the RAG agent already provides source references, use them
        formatted_sources = []
        for source in result_sources:
            source_ref = SourceReferenceResponse(
                document_id=source.document_id,
                relative_path=source.relative_path,
                score=source.score,
                content_preview=source.content_preview
            )
            formatted_sources.append(source_ref)
        return formatted_sources
    else:
        # Otherwise, create source references from context documents using citation service
        sources = citation_service.create_source_references(context_used)
        # Convert to response format
        formatted_sources = []
        for source in sources:
            source_ref = SourceReferenceResponse(
                document_id=source.document_id,
                relative_path=source.relative_path,
                score=source.score,
                content_preview=source.content_preview
            )
            formatted_sources.append(source_ref)
        return formatted_sources


# Health check endpoint
@app.get("/health")
async def health_check():
    init_services()
    status = "healthy" if rag_agent is not None else "unhealthy"
    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "rag_agent_ready": rag_agent is not None
    }


# Chat endpoint (now with actual RAG implementation and conversation context)
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Process user query and return RAG response with conversation context
    """
    try:
        init_services()  # Initialize services on first use
        logger.info(f"Received chat request: {request.message[:50]}...")

        if rag_agent is None:
            raise HTTPException(status_code=500, detail="RAG Agent not initialized")

        if citation_service is None:
            raise HTTPException(status_code=500, detail="Citation Service not initialized")

        if session_service is None:
            raise HTTPException(status_code=500, detail="Session Service not initialized")

        # Get or create session
        session_id = request.session_id
        if not session_id:
            # Create a new session
            session = session_service.create_session(user_id=request.user_id)
            session_id = session.id
        else:
            # Get existing session or create a new one if it doesn't exist
            session = session_service.get_session(session_id)
            if not session:
                session = session_service.create_session(user_id=request.user_id)
                session_id = session.id

        # Add user message to session
        session_service.add_message_to_session(session_id, "user", request.message)

        # Get recent conversation history for context (last 5 messages or so)
        recent_messages = session_service.get_session_messages(session_id, limit=10)  # Get last 10 messages
        conversation_context = []
        if recent_messages:
            for msg in recent_messages:
                conversation_context.append(f"{msg.role.title()}: {msg.content}")

        # Process the query with the RAG agent, including conversation context
        result = rag_agent.chat_with_context(request.message, conversation_context, top_k=request.top_k)

        # Add assistant message to session
        session_service.add_message_to_session(session_id, "assistant", result['response'])

        # Format the context documents
        context_docs = []
        for ctx in result['context_used']:
            # Create DocumentContext from the retrieved context
            doc_context = DocumentContext(
                id=str(ctx.get('id', 'unknown')),
                content=ctx['content'],
                metadata=ctx['metadata'],
                score=ctx['score']
            )
            context_docs.append(doc_context)

        # Format the source references
        sources = _format_sources(result.get('sources', []), result['context_used'])

        response = ChatResponse(
            response=result['response'],
            context_used=context_docs,
            sources=sources,
            query=result['query'],
            session_id=session_id
        )

        logger.info(f"Successfully processed chat request with conversation context, session: {session_id}")
        return response
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


# Additional endpoints can be added here as needed
@app.get("/")
async def root():
    return {"message": "RAG Chatbot API is running!"}


# Source preview endpoint
@app.post("/sources/preview")
async def source_preview_endpoint(request: ChatRequest):
    """
    Generate preview for sources based on a query
    """
    try:
        init_services()  # Initialize services on first use
        logger.info(f"Received source preview request: {request.message[:50]}...")

        if rag_agent is None:
            raise HTTPException(status_code=500, detail="RAG Agent not initialized")

        if citation_service is None:
            raise HTTPException(status_code=500, detail="Citation Service not initialized")

        # Get relevant documents for the query using the RAG agent's retrieval method
        context_docs = rag_agent.retrieve_context(request.message, top_k=request.top_k)

        # Create source references from context docs
        source_refs = citation_service.create_source_references(context_docs)

        # Create detailed previews for each source
        previews = []
        for i, source_ref in enumerate(source_refs):
            # Get the full content from context_docs for better preview
            full_content = context_docs[i]['content'] if i < len(context_docs) else None
            preview = citation_service.create_source_preview(source_ref, full_content)
            previews.append(preview)

        logger.info(f"Generated previews for {len(previews)} sources")
        return {
            "query": request.message,
            "previews": previews,
            "count": len(previews)
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing source preview request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)