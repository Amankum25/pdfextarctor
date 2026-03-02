# 🚀 Deployment Guide - Policy Analyzer

## Overview

Your app has two parts:
- **Backend**: FastAPI (Python) - needs to run continuously
- **Frontend**: React (Vite) - static files that can be served anywhere

---

## 🎯 Recommended Platform Combinations

### Option 1: Render (Easiest - FREE) ⭐ RECOMMENDED

**Backend + Frontend on Render**

| Component | Service | Cost | Performance |
|-----------|---------|------|-------------|
| Backend | Render Web Service | FREE (750 hrs/month) | Good |
| Frontend | Render Static Site | FREE | Excellent |
| Database/Storage | Persistent Disk | FREE (1GB) | Good |

**Pros:**
- ✅ Completely FREE for both
- ✅ Auto-deploy from GitHub
- ✅ Easy SSL/HTTPS
- ✅ Simple setup
- ✅ Good for production

**Cons:**
- ⚠️ Backend sleeps after 15min inactivity (cold starts ~30s)
- ⚠️ Limited resources on free tier

---

### Option 2: Vercel + Railway (FREE)

**Frontend on Vercel + Backend on Railway**

| Component | Service | Cost | Performance |
|-----------|---------|------|-------------|
| Frontend | Vercel | FREE | Excellent (CDN) |
| Backend | Railway | FREE ($5 credit) | Good |

**Pros:**
- ✅ Vercel has best frontend performance
- ✅ Railway doesn't sleep
- ✅ Easy GitHub integration

**Cons:**
- ⚠️ Railway credit expires after trial
- ⚠️ Two platforms to manage

---

### Option 3: Netlify + Render (FREE)

**Frontend on Netlify + Backend on Render**

| Component | Service | Cost | Performance |
|-----------|---------|------|-------------|
| Frontend | Netlify | FREE (100GB bandwidth) | Excellent |
| Backend | Render | FREE | Good |

**Pros:**
- ✅ Netlify has excellent UI
- ✅ Great build system
- ✅ Form handling built-in

**Cons:**
- ⚠️ Render backend sleeps
- ⚠️ Two platforms to manage

---

### Option 4: Railway (All-in-One) 💰

**Both on Railway**

| Component | Service | Cost | Performance |
|-----------|---------|------|-------------|
| Backend | Railway Web Service | $5/month after trial | Excellent |
| Frontend | Railway Static Site | Included | Good |

**Pros:**
- ✅ Single platform
- ✅ No cold starts
- ✅ Great performance
- ✅ Easy to scale

**Cons:**
- ❌ Not free long-term (~$5/month)

---

### Option 5: AWS/Azure/GCP (Enterprise)

**For Production/Scale**

| Platform | Backend | Frontend | Cost |
|----------|---------|----------|------|
| AWS | EC2/Lambda/ECS | S3 + CloudFront | ~$10-50/month |
| Azure | App Service/Container Apps | Static Web Apps | ~$10-50/month |
| GCP | Cloud Run/App Engine | Firebase Hosting | ~$10-50/month |

**Pros:**
- ✅ Full control
- ✅ Auto-scaling
- ✅ Enterprise features

**Cons:**
- ❌ More expensive
- ❌ Complex setup
- ❌ Requires cloud knowledge

---

### Option 6: Docker + VPS (Self-Hosted)

**DigitalOcean/Linode/Hetzner**

| Component | Service | Cost | Performance |
|-----------|---------|------|-------------|
| Backend + Frontend | VPS (Docker) | $5-10/month | Excellent |

**Pros:**
- ✅ Full control
- ✅ Best price/performance
- ✅ Single server

**Cons:**
- ❌ Manual setup
- ❌ You manage updates/security
- ❌ No auto-scaling

---

## 📋 Detailed Setup Instructions

### OPTION 1: Render (RECOMMENDED) ⭐

#### Step 1: Prepare Your Code

Your code is already GitHub-ready! Just ensure:
- Repository is public or Render has access
- `.env.example` exists (✓)
- `requirements.txt` exists (✓)

#### Step 2: Deploy Backend

1. Go to https://render.com and sign up
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account
4. Select your repository: `policy-analyser`
5. Configure:
   ```
   Name: policy-analyzer-backend
   Region: Choose closest to you
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r ../requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
6. Add Environment Variables:
   ```
   GROQ_API_KEY=your_groq_key
   EMBEDDING_PROVIDER=local
   LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
   LLM_PROVIDER=groq
   LLM_MODEL_NAME=llama-3.3-70b-versatile
   ```
7. Select **Free** plan
8. Click **"Create Web Service"**

**Wait 5-10 minutes for initial deployment**

You'll get a URL like: `https://policy-analyzer-backend.onrender.com`

#### Step 3: Deploy Frontend

1. In Render dashboard, click **"New +"** → **"Static Site"**
2. Select your repository: `policy-analyser`
3. Configure:
   ```
   Name: policy-analyzer-frontend
   Branch: main
   Root Directory: frontend
   Build Command: npm install && npm run build
   Publish Directory: dist
   ```
4. Add Environment Variable:
   ```
   VITE_API_URL=https://policy-analyzer-backend.onrender.com
   ```
5. Click **"Create Static Site"**

You'll get a URL like: `https://policy-analyzer-frontend.onrender.app`

#### Step 4: Update Frontend API URL

Update your frontend to use the backend URL:

In `frontend/.env.production`:
```env
VITE_API_URL=https://policy-analyzer-backend.onrender.com
```

In `frontend/src/api.js`, ensure it reads from env:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

Push changes:
```bash
git add .
git commit -m "Add production API URL"
git push origin main
```

Render will auto-redeploy!

#### Step 5: Configure CORS

Update `backend/main.py` CORS to allow your frontend:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://policy-analyzer-frontend.onrender.app",  # Add this
        "*"  # Or keep * for any origin
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### OPTION 2: Vercel + Railway

#### Deploy Backend to Railway

1. Go to https://railway.app and sign up
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select `policy-analyser`
4. Railway auto-detects Python
5. Configure:
   - Root Directory: `backend`
   - Build Command: `pip install -r ../requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variables (same as Render)
7. Click **"Deploy"**

You'll get: `https://policy-analyzer-backend.up.railway.app`

#### Deploy Frontend to Vercel

1. Go to https://vercel.com and sign up
2. Click **"Add New"** → **"Project"**
3. Import `policy-analyser` from GitHub
4. Configure:
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   ```
5. Add Environment Variable:
   ```
   VITE_API_URL=https://policy-analyzer-backend.up.railway.app
   ```
6. Click **"Deploy"**

You'll get: `https://policy-analyzer.vercel.app`

---

### OPTION 3: Docker on VPS (DigitalOcean)

#### Step 1: Create Droplet

1. Go to https://digitalocean.com
2. Create a Droplet:
   - Ubuntu 22.04
   - Basic Plan ($6/month)
   - Closest datacenter

#### Step 2: Setup Docker

SSH into your droplet:
```bash
ssh root@your_droplet_ip
```

Install Docker:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose -y
```

#### Step 3: Clone and Deploy

```bash
git clone https://github.com/Amankum25/policy-analyser.git
cd policy-analyser
```

Create `.env`:
```bash
nano .env
# Add your environment variables
```

Update `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./backend/faiss_index:/app/faiss_index
    restart: always

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    environment:
      - VITE_API_URL=http://your_droplet_ip:8000
    depends_on:
      - backend
    restart: always
```

Deploy:
```bash
docker-compose up -d --build
```

Access: `http://your_droplet_ip`

#### Step 4: Add SSL (Optional but Recommended)

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d yourdomain.com
```

---

## 🔧 Configuration Files Needed

### frontend/.env.production
```env
VITE_API_URL=https://your-backend-url.com
```

### frontend/vite.config.js (update)
```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  }
})
```

### backend/Dockerfile (create if needed)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Expose port
EXPOSE 8000

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### frontend/Dockerfile
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 📊 Platform Comparison Matrix

| Feature | Render | Vercel+Railway | Netlify+Render | Railway | VPS |
|---------|--------|---------------|----------------|---------|-----|
| **Cost** | FREE | FREE | FREE | $5/mo | $5-10/mo |
| **Setup** | ⭐⭐⭐⭐⭐ Easy | ⭐⭐⭐⭐ Easy | ⭐⭐⭐⭐ Easy | ⭐⭐⭐⭐⭐ Easy | ⭐⭐ Moderate |
| **Cold Starts** | Yes | No (Railway) | Yes | No | No |
| **Auto-Deploy** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ❌ Manual |
| **SSL/HTTPS** | ✅ Auto | ✅ Auto | ✅ Auto | ✅ Auto | Manual |
| **Scaling** | Limited | Good | Limited | Good | Manual |
| **Best For** | Hobby/MVP | Production | Content sites | Startups | Full control |

---

## 🎯 My Recommendation

### For Your Use Case (Policy Analyzer):

**🥇 BEST: Render (Frontend + Backend)**

**Why:**
1. ✅ Completely FREE
2. ✅ Single platform (easier to manage)
3. ✅ Auto-deploy from GitHub
4. ✅ Good enough performance
5. ✅ Easy SSL
6. ✅ Your backend will sleep when not in use (saves resources)

**Trade-off:**
- 30s cold start when backend wakes up
- Good for: Demos, portfolio projects, MVPs
- Not good for: High-traffic production apps

---

## 🚀 Quick Start - Deploy Now

### 1. Render Deployment (30 minutes)

```bash
# 1. Make sure code is pushed
git push origin main

# 2. Go to render.com → Sign up
# 3. New Web Service → Connect GitHub → Select policy-analyser
# 4. Configure as shown above
# 5. Deploy!
```

### 2. Vercel + Railway (45 minutes)

```bash
# Backend on Railway
1. railway.app → New Project → GitHub → policy-analyser
2. Set root: backend
3. Add env variables
4. Deploy

# Frontend on Vercel
1. vercel.com → New Project → policy-analyser
2. Root: frontend
3. Add VITE_API_URL=railway_url
4. Deploy
```

---

## 🐛 Common Deployment Issues

### Issue 1: CORS Errors

**Solution:** Update `backend/main.py`:
```python
allow_origins=["https://your-frontend-url.com", "*"]
```

### Issue 2: API Not Found (404)

**Solution:** Check `VITE_API_URL` in frontend env

### Issue 3: Backend Crashes

**Solution:** Check logs for:
- Missing dependencies
- API key not set
- Port binding issues

### Issue 4: Build Fails

**Solution:**
- Check `requirements.txt` has all deps
- Verify `package.json` scripts
- Check build logs

### Issue 5: Large Files/Models

**Solution:**
- Sentence-transformers models download on first run
- Ensure enough disk space (Render: 1GB free)
- Use smaller models if needed

---

## 📈 Performance Tips

1. **Enable Compression:** Already in Vite
2. **Use CDN:** Vercel/Netlify have built-in CDN
3. **Optimize Images:** Compress any images
4. **Cache Static Assets:** Already configured
5. **Use Redis:** Add Redis on Render for caching (optional)

---

## 💰 Cost Breakdown

### Free Tier Limits

| Platform | Backend | Frontend | Bandwidth | Storage |
|----------|---------|----------|-----------|---------|
| Render | 750 hrs/mo | Unlimited | 100GB/mo | 1GB |
| Vercel | N/A | Unlimited | 100GB/mo | N/A |
| Railway | $5 credit | Included | 100GB | 1GB |
| Netlify | N/A | 300 min/mo | 100GB/mo | N/A |

### When You Need to Pay

**Render:** Never (unless you need always-on backend)
**Railway:** After $5 trial credit (~1-2 months)
**Vercel:** Only if you exceed 100GB bandwidth
**VPS:** From day 1 (~$5-10/month)

---

## 🎓 Next Steps

1. **Choose a platform** (I recommend Render)
2. **Follow the setup guide** above
3. **Test your deployment**
4. **Share your URL** with users!

---

## 🆘 Need Help?

If you get stuck:
1. Check platform documentation
2. Review deployment logs
3. Test locally first with Docker
4. Ask in platform Discord/forums

---

**Ready to deploy? Let's start with Render!** 🚀
