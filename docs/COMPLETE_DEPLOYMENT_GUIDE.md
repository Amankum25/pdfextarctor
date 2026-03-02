# Policy Analyzer - Complete Deployment Guide

**From Zero to Production in 30 Minutes**

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Deploy Backend to Render](#step-1-deploy-backend-to-render)
4. [Step 2: Get API Keys](#step-2-get-api-keys)
5. [Step 3: Configure Environment Variables](#step-3-configure-environment-variables)
6. [Step 4: Deploy Frontend to Vercel](#step-4-deploy-frontend-to-vercel)
7. [Step 5: Connect Frontend to Backend](#step-5-connect-frontend-to-backend)
8. [Step 6: Test Your Deployment](#step-6-test-your-deployment)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance](#maintenance)

---

## Overview

### What You're Deploying

- **Backend**: FastAPI application with AI/ML capabilities (Render)
- **Frontend**: React application with modern UI (Vercel)
- **Cost**: **$0/month** (100% FREE)

### Architecture

```
User → Vercel (Frontend) → Render (Backend) → Groq API (LLM)
                                           └→ Local Embeddings (FREE)
```

### Time Required

- Backend deployment: 15 minutes
- Frontend deployment: 10 minutes
- Configuration: 5 minutes
- **Total**: 30 minutes

---

## Prerequisites

### Required Accounts

1. **GitHub Account** ✅ (You have this)
   - Repository: https://github.com/Amankum25/pdfextarctor

2. **Render Account** (Sign up: https://render.com)
   - Free tier: 750 hours/month
   - Sign up with GitHub

3. **Vercel Account** ✅ (You have this)
   - Already deployed frontend
   - URL: https://policy-analyzer-frontend.vercel.app

4. **Groq Account** (Sign up: https://console.groq.com)
   - Free tier: 30 requests/min
   - Required for LLM responses

### Optional Accounts

5. **Google AI Studio** (Optional)
   - Only if using Google embeddings
   - https://aistudio.google.com

---

## Step 1: Deploy Backend to Render

### 1.1 Create Render Account

1. Go to: **https://render.com**
2. Click **"Get Started"**
3. Choose **"Sign in with GitHub"**
4. Authorize Render to access your repositories
5. Complete your profile

### 1.2 Create Web Service

1. Click **"New +"** button (top right)
2. Select **"Web Service"**
3. Click **"Connect" to GitHub**
4. Find and select: **pdfextarctor** repository
5. Click **"Connect"**

### 1.3 Configure Service Settings

Fill in these exact values:

| Setting | Value |
|---------|-------|
| **Name** | `policy-analyzer-backend` |
| **Region** | `Oregon (US West)` or closest to you |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r ../requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` |

### 1.4 Advanced Settings (Expand this section)

| Setting | Value |
|---------|-------|
| **Auto-Deploy** | `Yes` (enabled) |
| **Health Check Path** | `/health` |

### 1.5 Click "Create Web Service"

**Do NOT deploy yet!** You need to add environment variables first.

---

## Step 2: Get API Keys

### 2.1 Get Groq API Key (Required)

1. Go to: **https://console.groq.com**
2. Click **"Sign Up"** or **"Log In"**
3. Complete registration (free)
4. Go to: **https://console.groq.com/keys**
5. Click **"Create API Key"**
6. Name it: `policy-analyzer`
7. Click **"Create"**
8. **Copy the key** (starts with `gsk_...`)
9. Save it somewhere safe (you'll need it in Step 3)

**Important**: Copy the key now! You won't see it again.

**Free Tier Limits**:
- 30 requests per minute
- 14,400 requests per day
- ✅ More than enough for your app!

### 2.2 Get Google API Key (Optional)

**Skip this if using local embeddings** (recommended)

1. Go to: **https://aistudio.google.com/app/apikey**
2. Sign in with Google account
3. Click **"Create API Key"**
4. Select project or create new one
5. Copy the API key
6. Save it (you'll need it if using Google embeddings)

---

## Step 3: Configure Environment Variables

### 3.1 Go to Render Dashboard

1. Go to: **https://dashboard.render.com**
2. Click on: **policy-analyzer-backend**
3. Click on: **"Environment"** tab (left sidebar)

### 3.2 Add Environment Variables

Click **"Add Environment Variable"** for each of these:

#### Required Variables (5 total):

**Variable 1: GROQ_API_KEY**
```
Key:   GROQ_API_KEY
Value: your_groq_api_key_here
```
(Paste the key from Step 2.1)

**Variable 2: EMBEDDING_PROVIDER**
```
Key:   EMBEDDING_PROVIDER
Value: local
```

**Variable 3: LLM_PROVIDER**
```
Key:   LLM_PROVIDER
Value: groq
```

**Variable 4: LLM_MODEL_NAME**
```
Key:   LLM_MODEL_NAME
Value: llama-3.3-70b-versatile
```

**Variable 5: LOCAL_EMBEDDING_MODEL**
```
Key:   LOCAL_EMBEDDING_MODEL
Value: all-MiniLM-L6-v2
```

#### Optional Variables (recommended defaults):

**Variable 6: CHUNK_SIZE**
```
Key:   CHUNK_SIZE
Value: 1000
```

**Variable 7: CHUNK_OVERLAP**
```
Key:   CHUNK_OVERLAP
Value: 200
```

**Variable 8: TOP_K**
```
Key:   TOP_K
Value: 10
```

**Variable 9: SIMILARITY_THRESHOLD**
```
Key:   SIMILARITY_THRESHOLD
Value: 0.3
```

### 3.3 Save and Deploy

1. Click **"Save Changes"** button
2. Render will automatically start deploying
3. Wait 5-10 minutes for first deployment

### 3.4 Monitor Deployment

Watch the **"Logs"** tab:

```
==> Building...
==> Installing dependencies from requirements.txt
==> Build successful
==> Starting service
==> Service is live
```

You'll see: ✅ **Live** (green indicator)

### 3.5 Get Your Backend URL

Copy your backend URL, it will look like:
```
https://policy-analyzer-backend.onrender.com
```

Save this URL! You'll need it for Step 5.

---

## Step 4: Deploy Frontend to Vercel

### 4.1 Verify Vercel Deployment

✅ **Already completed!**

Your frontend is live at:
```
https://policy-analyzer-frontend.vercel.app
```

If you need to redeploy:

```powershell
cd frontend
vercel --prod --yes
```

### 4.2 Verify Vercel Project

1. Go to: **https://vercel.com/dashboard**
2. Find: **policy-analyzer-frontend**
3. Status should show: ✅ **Ready**

---

## Step 5: Connect Frontend to Backend

### 5.1 Update Environment Variable in Vercel

**Option A: Via Vercel Dashboard (Easier)**

1. Go to: **https://vercel.com/dashboard**
2. Click on: **policy-analyzer-frontend**
3. Click: **Settings** tab
4. Click: **Environment Variables** (left sidebar)
5. Find: `VITE_API_URL`
6. Click: **Edit** (pencil icon)
7. Update value to your Render backend URL:
   ```
   https://policy-analyzer-backend.onrender.com
   ```
8. Make sure checked: ✅ Production, ✅ Preview, ✅ Development
9. Click: **Save**

**Option B: Via Vercel CLI**

```powershell
cd frontend

# Remove old variable
vercel env rm VITE_API_URL production

# Add new variable
vercel env add VITE_API_URL production
# When prompted, enter: https://policy-analyzer-backend.onrender.com

# Redeploy
vercel --prod --yes
```

### 5.2 Redeploy Frontend

After updating the environment variable:

**Via Dashboard:**
1. Go to: **Deployments** tab
2. Click: **...** (three dots) on latest deployment
3. Click: **Redeploy**

**Via CLI:**
```powershell
cd frontend
vercel --prod --yes
```

Wait 1-2 minutes for redeployment.

---

## Step 6: Test Your Deployment

### 6.1 Test Backend Health

Open in browser or use curl:

```
https://policy-analyzer-backend.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "online",
  "ready": true,
  "document_stats": {
    "total_documents": 0,
    "total_chunks": 0
  }
}
```

✅ **Status 200 OK** = Backend is working!

### 6.2 Test API Documentation

Visit:
```
https://policy-analyzer-backend.onrender.com/docs
```

You should see interactive Swagger API docs.

### 6.3 Test Frontend

1. Open: **https://policy-analyzer-frontend.vercel.app**
2. You should see: Policy Analyzer interface
3. Click: **Upload PDF** button
4. Upload a test PDF document
5. Wait for processing (shows progress)
6. Type a question in the chat
7. Click **Send** or press Enter
8. You should get an AI-generated answer!

### 6.4 Test End-to-End Flow

**Full Test Scenario:**

1. ✅ Open frontend URL
2. ✅ Upload a PDF (e.g., a policy document)
3. ✅ Wait for "Document processed successfully"
4. ✅ Ask: "What is this document about?"
5. ✅ Receive answer with confidence score
6. ✅ Ask follow-up questions
7. ✅ Verify responses are accurate

**If all steps pass = Deployment successful!** 🎉

---

## Troubleshooting

### Issue 1: Backend Shows "Service Unavailable"

**Symptoms:**
- Render shows: "Service unavailable"
- Logs show: "Application startup failed"

**Solutions:**

1. **Check Environment Variables**
   - Go to Render → Environment
   - Verify all 5 required variables are set
   - Check for typos (especially in `GROQ_API_KEY`)

2. **Check Logs**
   ```
   Render Dashboard → Logs tab
   ```
   Look for error messages

3. **Common Errors:**
   - `GROQ_API_KEY not found` → Add the variable
   - `Invalid API key` → Check your Groq key
   - `Model download failed` → Use `all-MiniLM-L6-v2`

### Issue 2: Backend Cold Start (Slow First Request)

**Symptoms:**
- First request takes 30-60 seconds
- Subsequent requests are fast

**This is normal!** 

Render's free tier sleeps after 15 minutes of inactivity.

**Solutions:**
- **Accept it** (it's free!)
- **Keep alive service** (use UptimeRobot to ping every 10 min)
- **Upgrade to paid tier** ($7/month for always-on)

### Issue 3: Frontend Can't Reach Backend (CORS Error)

**Symptoms:**
```
Access to fetch has been blocked by CORS policy
```

**Solution:**

1. **Update backend CORS settings**
   
   Edit: `backend/main.py`
   
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "https://policy-analyzer-frontend.vercel.app",
           "http://localhost:5173",
           "*"
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Commit and push:**
   ```powershell
   git add backend/main.py
   git commit -m "Update CORS for Vercel frontend"
   git push origin main
   ```

3. **Render will auto-deploy** (wait 5 minutes)

### Issue 4: Frontend Shows Wrong API URL

**Symptoms:**
- Frontend tries to call `http://localhost:8000`
- Network errors in browser console

**Solution:**

1. Verify `VITE_API_URL` in Vercel:
   ```
   Vercel Dashboard → Settings → Environment Variables
   ```

2. Make sure value is:
   ```
   https://policy-analyzer-backend.onrender.com
   ```

3. Redeploy frontend:
   ```powershell
   vercel --prod --yes
   ```

### Issue 5: "Rate Limit Exceeded" Error

**Symptoms:**
```
429 Too Many Requests
Rate limit exceeded for Groq API
```

**Groq Free Tier Limits:**
- 30 requests per minute
- 14,400 requests per day

**Solutions:**
- Wait 1 minute and try again
- Reduce request frequency
- Create multiple Groq accounts (not recommended)
- Upgrade to Groq Pro (paid)

### Issue 6: Build Fails in Render

**Symptoms:**
- Build command fails
- "requirements.txt not found"

**Solution:**

1. Check build command in Render:
   ```
   pip install -r ../requirements.txt
   ```

2. Check root directory is set to: `backend`

3. Verify `requirements.txt` exists in repository root

### Issue 7: Model Download Timeout

**Symptoms:**
```
Timeout while downloading sentence-transformers model
```

**Solution:**

Use the smallest model:
```
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
```

This model is only ~80MB and downloads quickly.

---

## Maintenance

### How to Update Your App

#### Update Backend Code

1. Make changes locally
2. Commit and push:
   ```powershell
   git add .
   git commit -m "Update backend"
   git push origin main
   ```
3. Render auto-deploys in 5 minutes ✅

#### Update Frontend Code

1. Make changes locally
2. Option A - Auto deploy (if GitHub integration):
   ```powershell
   git add .
   git commit -m "Update frontend"
   git push origin main
   ```
   Vercel auto-deploys in 2 minutes ✅

2. Option B - Manual deploy:
   ```powershell
   cd frontend
   vercel --prod --yes
   ```

### How to View Logs

**Backend Logs (Render):**
```
Render Dashboard → policy-analyzer-backend → Logs tab
```

**Frontend Logs (Vercel):**
```
Vercel Dashboard → policy-analyzer-frontend → Deployments → View Logs
```

### How to Restart Services

**Restart Backend:**
```
Render Dashboard → policy-analyzer-backend → Manual Deploy → Deploy
```

**Restart Frontend:**
```powershell
vercel --prod --yes
```

### How to Monitor Uptime

**Recommended Tools:**
- **UptimeRobot** (free): https://uptimerobot.com
- **Pingdom** (free tier): https://pingdom.com

**Setup:**
1. Create account
2. Add monitor for: `https://policy-analyzer-backend.onrender.com/health`
3. Check every: 10 minutes
4. Get alerts via email if down

### How to Update Environment Variables

**Backend (Render):**
```
Render Dashboard → Environment → Edit → Save Changes
```
(Triggers auto-redeploy)

**Frontend (Vercel):**
```
Vercel Dashboard → Settings → Environment Variables → Edit → Save
```
(Redeploy required)

---

## Cost Summary

### Current Setup (100% FREE)

| Service | Tier | Cost | Limits |
|---------|------|------|--------|
| **Render** | Free | $0/mo | 750 hrs/mo, sleeps after 15min |
| **Vercel** | Hobby | $0/mo | 100GB bandwidth/mo |
| **Groq** | Free | $0/mo | 30 req/min, 14,400 req/day |
| **GitHub** | Free | $0/mo | Unlimited public repos |
| **Total** | | **$0/mo** | ✨ |

### When to Upgrade

**Upgrade Render to Starter ($7/mo) when:**
- You have consistent traffic
- Cold starts are annoying
- You need 24/7 uptime
- You want more RAM/CPU

**Upgrade Vercel to Pro ($20/mo) when:**
- Bandwidth >100GB/month
- Need advanced analytics
- Want better performance

**Upgrade Groq when:**
- Rate limit is an issue (>30 req/min)
- Need higher throughput

---

## Quick Reference

### Important URLs

| Resource | URL |
|----------|-----|
| **Frontend (Live)** | https://policy-analyzer-frontend.vercel.app |
| **Backend (Live)** | https://policy-analyzer-backend.onrender.com |
| **Backend Health** | https://policy-analyzer-backend.onrender.com/health |
| **API Docs** | https://policy-analyzer-backend.onrender.com/docs |
| **GitHub Repo** | https://github.com/Amankum25/pdfextarctor |
| **Render Dashboard** | https://dashboard.render.com |
| **Vercel Dashboard** | https://vercel.com/dashboard |
| **Groq Console** | https://console.groq.com |

### Command Reference

```powershell
# Redeploy frontend
cd frontend
vercel --prod --yes

# View Vercel env vars
vercel env ls

# Add Vercel env var
vercel env add VITE_API_URL production

# View Vercel logs
vercel logs

# Test backend health (PowerShell)
Invoke-WebRequest -Uri https://policy-analyzer-backend.onrender.com/health

# Test backend health (curl)
curl https://policy-analyzer-backend.onrender.com/health

# Push updates to GitHub
git add .
git commit -m "Update app"
git push origin main
```

### Support Contacts

- **Render Support**: https://render.com/support
- **Vercel Support**: https://vercel.com/support
- **Groq Discord**: https://groq.com/discord
- **GitHub Issues**: https://github.com/Amankum25/pdfextarctor/issues

---

## Success Checklist

### Pre-Deployment

- [ ] GitHub repository exists and is up to date
- [ ] Created Render account
- [ ] Created Vercel account  
- [ ] Created Groq account
- [ ] Obtained Groq API key

### Backend Deployment

- [ ] Created web service in Render
- [ ] Configured build and start commands
- [ ] Added all 5 required environment variables
- [ ] Service deployed successfully (✅ Live)
- [ ] Health endpoint returns 200 OK
- [ ] API docs accessible at /docs
- [ ] Copied backend URL

### Frontend Deployment

- [ ] Frontend deployed to Vercel
- [ ] Updated VITE_API_URL with backend URL
- [ ] Redeployed with new environment variable
- [ ] Frontend loads without errors
- [ ] Browser console shows no errors

### End-to-End Testing

- [ ] Can access frontend URL
- [ ] Can upload PDF document
- [ ] Document processes successfully
- [ ] Can ask questions
- [ ] Receives AI-generated answers
- [ ] Answers are relevant and accurate
- [ ] No CORS errors
- [ ] No API errors

### Post-Deployment

- [ ] Saved all URLs and credentials
- [ ] Set up uptime monitoring (optional)
- [ ] Tested on mobile device
- [ ] Shared with stakeholders
- [ ] Added to portfolio/resume

---

## Congratulations! 🎉

Your Policy Analyzer is now live in production!

**Your Deployment:**
- ✅ Backend: Render (FREE)
- ✅ Frontend: Vercel (FREE)
- ✅ AI/ML: Groq (FREE)
- ✅ Total Cost: $0/month
- ✅ Professional-grade architecture
- ✅ Scalable and maintainable

**What You Built:**
- AI-powered document Q&A system
- Retrieval-Augmented Generation (RAG)
- Vector similarity search
- Modern React frontend
- Production REST API
- Cost-optimized architecture

**Share Your Project:**
- Add to portfolio
- Share on LinkedIn
- Include in resume
- Demo to employers

---

**Document Version**: 1.0
**Last Updated**: March 2, 2026
**Author**: Policy Analyzer Deployment Team

**Need Help?** 
- Check: `docs/` folder for more guides
- Visit: GitHub Issues for community support

---

**END OF DOCUMENT**
