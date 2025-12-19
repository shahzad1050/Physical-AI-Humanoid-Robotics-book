# Quick deployment script for Vercel (Windows)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "RAG Chatbot - Vercel Deployment Script" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is configured
Write-Host "Step 1: Committing changes..." -ForegroundColor Yellow
git add .
git commit -m "Deploy RAG Chatbot frontend and backend integration"

if ($LASTEXITCODE -ne 0) {
  Write-Host "Git commit failed. Please fix any conflicts." -ForegroundColor Red
  exit 1
}

Write-Host "Changes committed" -ForegroundColor Green
Write-Host ""

# Push to repository
Write-Host "Step 2: Pushing to GitHub..." -ForegroundColor Yellow
git push origin 001-rag-chatbot

if ($LASTEXITCODE -ne 0) {
  Write-Host "Git push failed." -ForegroundColor Red
  exit 1
}

Write-Host "Pushed to GitHub" -ForegroundColor Green
Write-Host ""

# Provide deployment instructions
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Open GitHub and create PR: 001-rag-chatbot -> main" -ForegroundColor White
Write-Host "   https://github.com/shahzad1050/Physical-AI-Humanoid-book/pulls" -ForegroundColor Blue
Write-Host ""
Write-Host "2. Go to Vercel Dashboard and set Environment Variables:" -ForegroundColor White
Write-Host "   https://vercel.com/dashboard/projects" -ForegroundColor Blue
Write-Host ""
Write-Host "3. Required Variables:" -ForegroundColor White
Write-Host "   - OPENAI_API_KEY" -ForegroundColor Gray
Write-Host "   - COHERE_API_KEY" -ForegroundColor Gray
Write-Host "   - NEON_CONNECTION_STRING" -ForegroundColor Gray
Write-Host "   - NEXT_PUBLIC_API_BASE_URL" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Merge PR to 'main' branch" -ForegroundColor White
Write-Host ""
Write-Host "5. Vercel will automatically deploy!" -ForegroundColor White
Write-Host ""
Write-Host "6. Visit your live site:" -ForegroundColor White
Write-Host "   https://physical-ai-humanoid-book-theta.vercel.app" -ForegroundColor Blue
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "For more details, see: DEPLOYMENT_READY.md" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
