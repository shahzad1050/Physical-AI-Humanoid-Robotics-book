# RAG Chatbot - Frontend & Backend Integration & Vercel Deployment Guide

## Overview
This guide explains how to connect your React/Docusaurus frontend with the FastAPI backend and deploy to Vercel.

## Architecture

```
https://physical-ai-humanoid-book-theta.vercel.app/
├── / (root)              → Docusaurus static site
├── /api/health           → FastAPI health check
├── /api/chat             → FastAPI chat endpoint
└── /api/sources/preview  → FastAPI sources endpoint
```

## Step 1: Frontend Configuration

The frontend is already configured to connect to the backend via environment variables:

**File**: `physical-ai-humanoid-robotics/src/components/RAGChatbot.jsx`

```javascript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
```

The frontend will automatically:
- Use `NEXT_PUBLIC_API_BASE_URL` in production (set in Vercel)
- Fall back to `http://localhost:8000` for local development

## Step 2: Environment Variables to Set in Vercel

Go to your Vercel project settings and add these environment variables:

### Required Backend Variables:
```
OPENAI_API_KEY=<your-openai-api-key>
COHERE_API_KEY=<your-cohere-api-key>
NEON_CONNECTION_STRING=<your-neon-postgres-connection-string>
```

### Frontend Variables:
```
NEXT_PUBLIC_API_BASE_URL=https://physical-ai-humanoid-book-theta.vercel.app/api
DOCUSAURUS_URL=https://physical-ai-humanoid-book-theta.vercel.app
DOCUSAURUS_BASE_URL=/
```

## Step 3: Deployment Process

### Option A: Direct Vercel Push (Recommended)

1. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Connect frontend and backend for Vercel deployment"
   git push origin 001-rag-chatbot
   ```

2. **Create Pull Request to main branch:**
   - Go to GitHub → Your repo → Create PR from `001-rag-chatbot` to `main`
   - This triggers Vercel preview deployment

3. **Set Environment Variables:**
   - Go to https://vercel.com/dashboard
   - Select your project → Settings → Environment Variables
   - Add all required variables above

4. **Merge to Main:**
   - Once tests pass, merge PR to main
   - Vercel automatically deploys to production

### Option B: Manual Vercel CLI Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from project root
vercel

# Set production environment variables and deploy to production
vercel --prod
```

## Step 4: Verify Deployment

Test these endpoints after deployment:

### 1. Health Check
```bash
curl https://physical-ai-humanoid-book-theta.vercel.app/api/health
```
Expected response:
```json
{"status": "healthy", "rag_agent_ready": true}
```

### 2. Chat Endpoint
```bash
curl -X POST https://physical-ai-humanoid-book-theta.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is RAG?", "top_k": 3}'
```

### 3. Frontend Test
- Open https://physical-ai-humanoid-book-theta.vercel.app
- Click the chatbot icon (bottom right)
- Send a message
- Verify you get a response

## Step 5: Local Development Setup

### Backend Development:
```bash
cd /c/book/book
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r backend/requirements.txt
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

### Frontend Development:
```bash
cd physical-ai-humanoid-robotics
npm install
npm run start
```

The frontend will use `http://localhost:8000` for API calls (from .env configuration).

## Troubleshooting

### Issue: "Failed to fetch from /api/chat"
**Solution:** Make sure environment variables are set in Vercel dashboard

### Issue: "CORS Error"
**Solution:** Backend is configured with CORS for:
- http://localhost:3000 (local dev)
- https://physical-ai-humanoid-book-theta.vercel.app (production)
- https://*.vercel.app (preview deployments)

### Issue: "API returns 500 error"
**Solution:** Check Vercel logs:
```bash
vercel logs
```

### Issue: Chatbot in frontend not showing
**Solution:** Check browser console for errors and verify API_BASE_URL is correct

## File Structure

```
c:/book/book/
├── backend/                          # FastAPI backend
│   ├── app.py                       # Main FastAPI application
│   ├── services/                    # RAG, citation, session services
│   ├── requirements.txt             # Python dependencies
│   └── config/settings.py          # Configuration
├── api/
│   └── index.py                    # Vercel serverless function entry point
├── physical-ai-humanoid-robotics/   # Docusaurus frontend
│   ├── src/
│   │   └── components/
│   │       └── RAGChatbot.jsx       # Chat UI component
│   ├── package.json
│   └── .env.production             # Production env config
├── vercel.json                      # Vercel configuration
└── VERCEL_DEPLOYMENT.md            # This file
```

## Key Files Modified

1. **vercel.json** - Updated routing rules for API and static assets
2. **api/index.py** - New entry point for Vercel serverless functions
3. **physical-ai-humanoid-robotics/.env.production** - Production URLs
4. **backend/app.py** - Configured CORS for production domains

## Next Steps

1. ✅ Code is ready for deployment
2. Push to GitHub
3. Set environment variables in Vercel
4. Merge to main branch
5. Verify production deployment
6. Test all endpoints

## Support

For issues or questions:
- Check Vercel logs: `vercel logs`
- Backend logs on Vercel dashboard
- Verify all environment variables are set
- Test API endpoints with curl before frontend testing
