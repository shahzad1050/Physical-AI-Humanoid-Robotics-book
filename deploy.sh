#!/bin/bash
# Quick deployment script for RAG Chatbot to Vercel

echo "🚀 RAG Chatbot Vercel Deployment Script"
echo "========================================"

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

echo ""
echo "📋 Deployment Checklist:"
echo "========================"
echo "Before deploying, make sure you have:"
echo "✓ [ ] Backend deployed (Render/Railway/etc.)"
echo "✓ [ ] Backend URL copied (e.g., https://your-api.onrender.com)"
echo "✓ [ ] GitHub repository synced"
echo ""

read -p "Enter your backend API URL (e.g., https://rag-chatbot-api.onrender.com): " BACKEND_URL

if [ -z "$BACKEND_URL" ]; then
    echo "❌ Backend URL is required!"
    exit 1
fi

echo ""
echo "🔧 Setting up environment variables..."
echo "Backend URL: $BACKEND_URL"
echo ""

# Navigate to Docusaurus directory
cd "$(dirname "$0")/physical-ai-humanoid-robotics" || exit

echo "📦 Installing dependencies..."
npm install

echo ""
echo "🔨 Building project..."
npm run build

echo ""
echo "🚀 Deploying to Vercel..."
echo "When prompted, set the environment variable:"
echo "  Key: REACT_APP_API_BASE_URL"
echo "  Value: $BACKEND_URL"
echo ""

vercel --prod \
  --env REACT_APP_API_BASE_URL=$BACKEND_URL \
  --env NEXT_PUBLIC_API_BASE_URL=$BACKEND_URL

echo ""
echo "✅ Deployment complete!"
echo "Visit: https://physical-ai-humanoid-book-theta.vercel.app"
