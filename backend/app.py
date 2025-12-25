# FastAPI server for Vercel deployment
from fastapi import FastAPI
from typing import List, Optional, Dict, Any

# Initialize FastAPI app with documentation
app = FastAPI(
    title="Physical AI & Humanoid Robotics RAG API",
    description="API for the Physical AI & Humanoid Robotics documentation chatbot",
    version="1.0.0",
    docs_url="/api/docs",  # Changed to avoid conflicts with Docusaurus routes
    redoc_url="/api/redoc"  # Changed to avoid conflicts with Docusaurus routes
)

# Simple dictionary-based approach to avoid Pydantic BaseModel issues
@app.post("/chat")
async def chat_endpoint(message: str, top_k: Optional[int] = 3):
    """
    Main RAG chat endpoint that retrieves context and generates response
    """
    # Mock response for testing - in production, this would connect to your RAG system
    response = f"Mock response to: {message}"
    context_used = [
        {
            "id": 1,
            "content": "Mock context for testing purposes",
            "score": 0.9
        }
    ]

    return {
        "response": response,
        "context_used": context_used
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "api": "RAG Chatbot API",
        "version": "1.0.0"
    }

@app.get("/test_json")
async def test_json_endpoint():
    """
    Test endpoint that returns a simple JSON response
    """
    return {"hello": "world", "status": "ok"}

# For local development only
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)