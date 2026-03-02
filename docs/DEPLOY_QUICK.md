# 🚀 Quick Deployment Commands

## Local Docker Deployment

### Start everything:
```bash
docker-compose up -d
```

### View logs:
```bash
docker-compose logs -f
```

### Stop everything:
```bash
docker-compose down
```

### Rebuild after changes:
```bash
docker-compose up -d --build
```

---

## Deploy to Render (FREE)

### 1. Backend Setup
```bash
# Render will auto-detect settings, but here's the config:
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
Root Directory: backend
```

### 2. Frontend Setup
```bash
# Render static site config:
Build Command: npm install && npm run build
Publish Directory: dist
Root Directory: frontend
```

### 3. Update frontend API URL
After backend is deployed, update `frontend/.env.production`:
```env
VITE_API_URL=https://your-backend-name.onrender.com
```

---

## Deploy to Railway

### Backend:
```bash
railway up
# It will auto-detect Python and deploy
```

### Frontend:
```bash
cd frontend
railway up
# Add VITE_API_URL in Railway dashboard
```

---

## Deploy to Vercel (Frontend Only)

```bash
cd frontend
npx vercel
# Follow prompts
# Add VITE_API_URL in Vercel dashboard
```

---

## Deploy to VPS (DigitalOcean/Linode)

### 1. SSH into VPS:
```bash
ssh root@your_server_ip
```

### 2. Install Docker:
```bash
curl -fsSL https://get.docker.com | sh
apt install docker-compose -y
```

### 3. Clone and run:
```bash
git clone https://github.com/Amankum25/policy-analyser.git
cd policy-analyser
nano .env  # Add your keys
docker-compose up -d
```

### 4. Access at:
```
http://your_server_ip
```

---

## Platform-Specific URLs

### Render:
- Backend: `https://[your-service-name].onrender.com`
- Frontend: `https://[your-static-site].onrender.app`

### Railway:
- Backend: `https://[your-project].up.railway.app`
- Frontend: `https://[your-frontend].up.railway.app`

### Vercel:
- Frontend: `https://[your-project].vercel.app`

---

## Environment Variables Needed

### Backend (Required):
```env
GROQ_API_KEY=your_key_here
EMBEDDING_PROVIDER=local
LLM_PROVIDER=groq
```

### Frontend (Required):
```env
VITE_API_URL=https://your-backend-url.com
```

---

## Troubleshooting

### Backend not starting:
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Missing API keys: Add to .env
# - Port in use: Change port in docker-compose.yml
# - Dependencies missing: Rebuild with --build flag
```

### Frontend can't reach backend:
```bash
# Check VITE_API_URL is correct
# Check CORS in backend/main.py
# Check backend is running
```

### Build fails:
```bash
# Clear cache and rebuild
docker-compose down
docker system prune -a
docker-compose up -d --build
```

---

## Performance Tips

1. **Use local embeddings** (faster, free)
2. **Enable Redis caching** (optional)
3. **Use Groq for LLM** (fast, free tier)
4. **Optimize chunk size** (1000 is good)
5. **Use CDN for frontend** (Vercel/Netlify)

---

## Cost Estimates

| Platform | Cost | Best For |
|----------|------|----------|
| Render (both) | FREE | MVP/Demo |
| Vercel + Railway | FREE trial | Production |
| VPS (DigitalOcean) | $6/month | Full control |
| AWS/Azure/GCP | $10-50/month | Enterprise |

---

## Quick Links

- [Full Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Setup Guide](./SETUP.md)
- [Project Status](./PROJECT_STATUS.md)

---

**Need help? Check the full [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)!**
