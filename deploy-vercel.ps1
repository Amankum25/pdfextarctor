# Vercel Deployment Script for Policy Analyzer Frontend

Write-Host "🚀 Deploying Policy Analyzer to Vercel..." -ForegroundColor Cyan
Write-Host ""

# Navigate to frontend directory
Set-Location -Path "frontend"

# Step 1: Login to Vercel (if not already)
Write-Host "Step 1: Login to Vercel" -ForegroundColor Yellow
Write-Host "If you're not logged in, run: vercel login" -ForegroundColor Gray
Write-Host ""

# Step 2: Deploy to Vercel
Write-Host "Step 2: Deploying..." -ForegroundColor Yellow
Write-Host "Running: vercel --prod" -ForegroundColor Gray
Write-Host ""
Write-Host "When prompted, answer:" -ForegroundColor Cyan
Write-Host "  - Set up and deploy? YES" -ForegroundColor White
Write-Host "  - Link to existing project? NO" -ForegroundColor White
Write-Host "  - Project name? policy-analyzer" -ForegroundColor White
Write-Host "  - Code directory? ./ (current directory)" -ForegroundColor White
Write-Host ""

# User should run this manually
Write-Host "Please run this command manually:" -ForegroundColor Green
Write-Host "  cd frontend" -ForegroundColor White
Write-Host "  vercel --prod" -ForegroundColor White
Write-Host ""

# Step 3: Instructions for environment variables
Write-Host "Step 3: After deployment, add environment variables:" -ForegroundColor Yellow
Write-Host "  vercel env add VITE_API_URL" -ForegroundColor White
Write-Host '  Enter value: https://your-backend-url.onrender.com' -ForegroundColor White
Write-Host '  Select environments: Production, Preview, Development' -ForegroundColor White
Write-Host ""

# Step 4: Redeploy with env vars
Write-Host "Step 4: Redeploy with environment variables:" -ForegroundColor Yellow
Write-Host "  vercel --prod" -ForegroundColor White
Write-Host ""

Write-Host "Done! 🎉" -ForegroundColor Green
