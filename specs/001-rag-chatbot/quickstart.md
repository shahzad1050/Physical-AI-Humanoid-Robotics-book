# Quickstart Guide: RAG Chatbot for Physical AI & Humanoid Robotics Documentation

## Prerequisites

- Python 3.14+
- Node.js (for Docusaurus development)
- API keys for:
  - OpenAI (for language model responses)
  - Cohere (for document embeddings)
  - Neon db 

## Setup

### 1. Clone and Navigate to Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 3. Frontend Setup
```bash
# Navigate to documentation directory
cd physical-ai-humanoid-robotics

# Install dependencies
npm install
```

## Initialize Documentation Embeddings

### 1. Run Embedding Pipeline
```bash
cd backend
python embeddings/embed_docs.py
```

### 2. Upload to Vector Database
```bash
python embeddings/upload_to_qdrant.py
```

## Running the Application

### 1. Start Backend API
```bash
cd backend
uvicorn app:app --reload --port 8000
```

### 2. Start Docusaurus Documentation Site
```bash
cd physical-ai-humanoid-robotics
npm start
```

## Testing the RAG Chatbot

### 1. API Endpoint Test
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the NVIDIA Isaac platform?",
    "top_k": 3
  }'
```

### 2. Frontend Widget Test
1. Open your browser to `http://localhost:3000`
2. Look for the floating chatbot widget in the bottom-right corner
3. Ask a question about Physical AI & Humanoid Robotics documentation
4. Verify that the response includes source citations

## Configuration

### Environment Variables (.env)
```
OPENAI_API_KEY=your_openai_api_key
COHERE_API_KEY=your_cohere_api_key
Neon = 
BACKEND_URL=http://localhost:8000
```

### API Endpoints
- `POST /chat` - Process user query and return RAG response
- `GET /health` - Check API health status
- `POST /embed` - Generate embeddings for text (optional)

## Troubleshooting

### Common Issues
1. **API Keys Not Set**: Ensure all required API keys are in the .env file
2. **Vector Database Connection**: Verify Qdrant URL and API key are correct
3. **Embedding Pipeline Failure**: Check that documentation files exist and are readable
4. **Frontend Widget Not Appearing**: Verify that the RAGChatbot component is properly integrated in docusaurus.config.js

### Verification Steps
1. Test API endpoint directly with curl
2. Check backend logs for error messages
3. Verify documentation files are properly chunked and embedded
4. Confirm frontend can reach backend API