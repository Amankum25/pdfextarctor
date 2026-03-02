# 🚀 Vercel Deployment Guide for Policy Analyzer

## Quick Deploy with Vercel CLI

### Prerequisites
- ✅ Vercel CLI installed (you have v50.25.4)
- ✅ GitHub repository pushed (done)
- ✅ Vercel account (create at vercel.com)

---

## Step-by-Step Deployment

### 1. Login to Vercel (if needed)

```bash
vercel login
```

This will open a browser to authenticate.

---

### 2. Deploy Frontend

```bash
cd frontend
vercel --prod
```

**Answer the prompts:**

```
? Set up and deploy "frontend"?
  → YES

? Which scope should contain your project?
  → Select your username/team

? Link to existing project?
  → NO

? What's your project's name?
  → policy-analyzer

? In which directory is your code located?
  → ./   (just press Enter)
```

Vercel will now:
- ✅ Install dependencies (npm install)
- ✅ Build your project (npm run build)
- ✅ Upload to Vercel
- ✅ Give you a URL

**You'll get a URL like:** `https://policy-analyzer.vercel.app`

---

### 3. Add Environment Variables

After deployment, add your backend URL:

#### Option A: Via CLI
```bash
cd frontend

# Add environment variable
vercel env add VITE_API_URL production

# When prompted, enter:
https://your-backend-url.onrender.com

# Or if backend is local/not deployed yet:
http://localhost:8000
```

#### Option B: Via Dashboard (Easier)

1. Go to: https://vercel.com/dashboard
2. Click on your project: **policy-analyzer**
3. Go to **Settings** → **Environment Variables**
4. Add variable:
   ```
   Name:  VITE_API_URL
   Value: https://your-backend-url.onrender.com
   ```
5. Select: **Production**, **Preview**, **Development**
6. Click **Save**

---

### 4. Redeploy with Environment Variables

```bash
cd frontend
vercel --prod
```

Or just push to GitHub (Vercel auto-deploys).

---

## Important Environment Variables

### Required:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `VITE_API_URL` | Backend API URL | `https://policy-analyzer.onrender.com` |

### Optional:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `VITE_APP_NAME` | Application name | `Policy Analyzer` |
| `VITE_MAX_FILE_SIZE` | Max upload size | `10485760` (10MB) |

---

## Alternative: Deploy via GitHub Integration

### 1. Connect GitHub to Vercel

1. Go to: https://vercel.com/new
2. Click **"Import Git Repository"**
3. Select: `policy-analyser` repository
4. Configure:
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   ```
5. Add Environment Variables:
   ```
   VITE_API_URL = https://your-backend-url.onrender.com
   ```
6. Click **"Deploy"**

✅ **Benefit:** Vercel will auto-deploy on every git push!

---

## Verify Deployment

### Check if it's working:

1. **Open your Vercel URL**: https://policy-analyzer.vercel.app
2. **Open browser console** (F12)
3. **Check API URL**:
   ```javascript
   console.log(import.meta.env.VITE_API_URL)
   ```
4. **Test upload**: Try uploading a PDF

---

## Common Issues & Solutions

### Issue 1: "VITE_API_URL is undefined"

**Solution:** Add the environment variable in Vercel dashboard and redeploy:
```bash
vercel env add VITE_API_URL production
vercel --prod
```

### Issue 2: "CORS error when calling API"

**Solution:** Update `backend/main.py` CORS settings:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://policy-analyzer.vercel.app",  # Add your Vercel URL
        "http://localhost:5173",
        "*"  # Or keep wildcard
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 3: "Build fails"

**Solution:** Check your frontend dependencies:
```bash
cd frontend
npm install
npm run build  # Test locally first
```

### Issue 4: "API not responding"

**Solution:** 
1. Check if backend is deployed and running
2. Verify `VITE_API_URL` is correct (no trailing slash)
3. Test backend: `curl https://your-backend.onrender.com/health`

---

## Update Deployment

### When you make code changes:

```bash
# Option 1: Just push to Git (if using GitHub integration)
git add .
git commit -m "Update frontend"
git push origin main
# Vercel auto-deploys!

# Option 2: Deploy manually
cd frontend
vercel --prod
```

---

## View Deployment Logs

```bash
# View logs
vercel logs

# Follow logs in real-time
vercel logs --follow

# View specific deployment
vercel inspect <deployment-url>
```

---

## Domains & URLs

### Default Vercel URLs:

```
Production:  https://policy-analyzer.vercel.app
Preview:     https://policy-analyzer-<git-branch>.vercel.app
Latest:      https://policy-analyzer-<random>.vercel.app
```

### Add Custom Domain (Optional):

1. Go to **Project Settings** → **Domains**
2. Add your domain: `policyanalyzer.com`
3. Update DNS records as shown
4. Wait for SSL certificate

---

## Performance Optimizations

### 1. Enable Vercel Analytics (Free)

In `frontend/package.json`:
```json
{
  "dependencies": {
    "@vercel/analytics": "^1.0.0"
  }
}
```

In `frontend/src/main.jsx`:
```javascript
import { inject } from '@vercel/analytics'
inject()
```

### 2. Enable Caching

Vite already does this, but verify your `vite.config.js`:
```javascript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
        },
      },
    },
  },
})
```

---

## Cost

**Vercel Free Tier:**
- ✅ 100GB bandwidth/month
- ✅ Unlimited deployments
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Perfect for your use case!

---

## Complete Deployment Checklist

- [ ] Push code to GitHub
- [ ] Login to Vercel CLI: `vercel login`
- [ ] Deploy frontend: `cd frontend && vercel --prod`
- [ ] Add environment variable: `VITE_API_URL`
- [ ] Verify deployment works
- [ ] Update backend CORS if needed
- [ ] Test uploading PDF and asking questions
- [ ] (Optional) Connect GitHub for auto-deploy
- [ ] (Optional) Add custom domain

---

## Next Steps After Deployment

1. **Deploy Backend to Render**
   - See: `docs/DEPLOYMENT_GUIDE.md` (Option 1)
2. **Update Frontend with Backend URL**
   - Add `VITE_API_URL` in Vercel
3. **Test Full Flow**
   - Upload PDF → Ask Question → Get Answer
4. **Monitor Performance**
   - Check Vercel Analytics
   - Monitor Render logs

---

## Quick Commands Reference

```bash
# Login
vercel login

# Deploy to production
cd frontend
vercel --prod

# Add environment variable
vercel env add VITE_API_URL production

# View logs
vercel logs

# List deployments
vercel ls

# Remove deployment
vercel rm <deployment-id>

# Help
vercel --help
```

---

## Support

- **Vercel Docs**: https://vercel.com/docs
- **Vercel CLI Docs**: https://vercel.com/docs/cli
- **Community**: https://vercel.com/community

---

**Ready to deploy?** 🚀

Run:
```bash
cd frontend
vercel --prod
```

Then add `VITE_API_URL` in the Vercel dashboard!
