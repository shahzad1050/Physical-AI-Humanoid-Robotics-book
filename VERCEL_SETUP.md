# Vercel Deployment Configuration for RAG Chatbot

## Environment Variables needed on Vercel:

Set these in your Vercel project settings:

### Backend Configuration
- `OPENAI_API_KEY`: Your OpenAI API key
- `COHERE_API_KEY`: Your Cohere API key  
- `NEON_CONNECTION_STRING`: Your Neon Postgres connection string

### Frontend Configuration
- `NEXT_PUBLIC_API_BASE_URL`: Set to your backend API URL (e.g., https://physical-ai-humanoid-book-theta.vercel.app/api)
- `DOCUSAURUS_URL`: https://physical-ai-humanoid-book-theta.vercel.app

## Deployment Structure:

- Frontend (React/Docusaurus): `/physical-ai-humanoid-robotics` → serves on `/`
- Backend API (FastAPI): `/backend` → serves on `/api/*`

## Routes:
- `/` → Docusaurus static site
- `/api/*` → FastAPI backend (chat, health, etc.)

## To Deploy:

1. Push your changes to GitHub
2. Connect your Vercel project
3. Set environment variables in Vercel dashboard
4. Vercel will automatically deploy

The vercel.json file is configured to:
- Build and deploy the Docusaurus site
- Run FastAPI backend on /api routes
