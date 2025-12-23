import sys
import os
# Add the parent directory to the path so we can import from frontend
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Test RAG Chatbot API", version="1.0.0")

class ChatRequest(BaseModel):
    message: str
    top_k: Optional[int] = 3

class ChatResponse(BaseModel):
    response: str
    context_used: List[Dict[str, Any]]

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Simple test endpoint
    """
    logger.info(f"Processing chat request: {request.message[:50]}...")
    return ChatResponse(
        response="Test response from backend",
        context_used=[{"id": 1, "content": "test context", "score": 0.9}]
    )

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)