# 🔐 Render Environment Variables - Complete List

## Copy-Paste Ready Values for Render Dashboard

When deploying your backend to Render, add these environment variables in the **Environment** section:

---

## ✅ REQUIRED Environment Variables

### 1. Groq API Key (Required for LLM)
```
GROQ_API_KEY=your_groq_api_key_here
```
**Get your key**: https://console.groq.com/keys

---

### 2. Embedding Provider (Required)
```
EMBEDDING_PROVIDER=local
```
**Options**: `local` (recommended, FREE) or `google`

---

### 3. LLM Provider (Required)
```
LLM_PROVIDER=groq
```
**Options**: `groq` (recommended), `ollama`, `openai`

---

### 4. LLM Model Name (Required)
```
LLM_MODEL_NAME=llama-3.3-70b-versatile
```
**For Groq**: `llama-3.3-70b-versatile` (fastest, recommended)

---

## 📋 OPTIONAL Environment Variables (with defaults)

### Local Embedding Model
```
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
```
**Options**: 
- `all-MiniLM-L6-v2` (fast, 384 dim)
- `all-mpnet-base-v2` (better quality, 768 dim)

---

### Google API Key (only if using Google embeddings)
```
GOOGLE_API_KEY=your_google_api_key_here
```
**Only needed if**: `EMBEDDING_PROVIDER=google`
**Get key**: https://aistudio.google.com/app/apikey

---

### OpenAI API Key (only if using OpenAI LLM)
```
OPENAI_API_KEY=your_openai_api_key_here
```
**Only needed if**: `LLM_PROVIDER=openai`

---

### Ollama Base URL (only if using Ollama)
```
OLLAMA_BASE_URL=http://localhost:11434
```
**Only needed if**: `LLM_PROVIDER=ollama`

---

### Chunking Configuration
```
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```
**Defaults**: 1000 characters with 200 overlap (optimal for most documents)

---

### Retrieval Configuration
```
TOP_K=10
SIMILARITY_THRESHOLD=0.3
```
**Defaults**: Retrieve top 10 chunks, minimum 30% similarity

---

### CORS Origins (Optional)
```
CORS_ORIGINS=*
```
**Default**: `*` (allows all origins)
**Production**: Set to your frontend URL: `https://policy-analyzer-frontend.vercel.app`

---

## 🎯 Recommended Configuration for Render (FREE Tier)

Copy these exact values into Render:

```
GROQ_API_KEY=your_groq_api_key_here
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_PROVIDER=groq
LLM_MODEL_NAME=llama-3.3-70b-versatile
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=10
SIMILARITY_THRESHOLD=0.3
```

---

## 📝 How to Add in Render Dashboard

### Step-by-Step:

1. **Go to Render**: https://render.com/dashboard
2. **Select your service**: `policy-analyzer-backend`
3. **Click**: Environment → **Add Environment Variable**
4. **For each variable**:
   - Click **"Add Environment Variable"**
   - Key: `GROQ_API_KEY`
   - Value: `your_actual_key_here`
   - Click **"Save"**
5. **Repeat** for all variables above
6. **Render will auto-redeploy** after saving

---

## 🔑 Where to Get API Keys

### Groq API Key (FREE - Required)
1. Go to: https://console.groq.com/keys
2. Sign up (free)
3. Click **"Create API Key"**
4. Copy the key
5. Paste in Render as `GROQ_API_KEY`

**Free tier**: 30 requests/minute, 14,400/day

---

### Google API Key (Optional - only if using Google embeddings)
1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with Google
3. Click **"Create API Key"**
4. Copy the key
5. Paste in Render as `GOOGLE_API_KEY`

**Free tier**: 1,500 requests/day

---

## ✅ Verification Checklist

After adding environment variables in Render:

- [ ] `GROQ_API_KEY` is set (required)
- [ ] `EMBEDDING_PROVIDER=local` is set
- [ ] `LLM_PROVIDER=groq` is set
- [ ] `LLM_MODEL_NAME=llama-3.3-70b-versatile` is set
- [ ] All other optional variables use defaults (or are set)
- [ ] Service deployed successfully
- [ ] Health check passes: `https://your-backend.onrender.com/health`

---

## 🧪 Test Your Backend After Deployment

```bash
# Test health endpoint
curl https://your-backend-name.onrender.com/health

# Expected response:
{
  "status": "online",
  "ready": true,
  "document_stats": {...}
}
```

---

## ⚠️ Common Issues

### Issue 1: "GROQ_API_KEY not found"
**Solution**: Make sure you added the variable without quotes and saved

### Issue 2: "Model download failed"
**Solution**: Render's free tier has 512MB RAM. Use `all-MiniLM-L6-v2` (small model)

### Issue 3: "Cold start timeout"
**Solution**: Normal for free tier. First request takes 30-60 seconds

---

## 💡 Pro Tips

1. **Use local embeddings** (`EMBEDDING_PROVIDER=local`) to avoid API costs
2. **Use Groq** for fast, free LLM inference
3. **all-MiniLM-L6-v2** is the smallest model that fits in Render's free tier
4. **Don't use quotes** around environment variable values in Render
5. **Render auto-deploys** when you save env variables

---

## 📋 Quick Copy-Paste for Render

**Minimal setup (only what you need):**

| Key | Value |
|-----|-------|
| `GROQ_API_KEY` | `your_groq_key_here` |
| `EMBEDDING_PROVIDER` | `local` |
| `LLM_PROVIDER` | `groq` |
| `LLM_MODEL_NAME` | `llama-3.3-70b-versatile` |
| `LOCAL_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` |

---

## 🚀 Next Steps After Setting Environment Variables

1. ✅ Render will automatically redeploy
2. ✅ Wait 5-10 minutes for deployment
3. ✅ Test health endpoint
4. ✅ Update Vercel frontend with backend URL:
   ```bash
   vercel env add VITE_API_URL production
   # Enter: https://your-backend-name.onrender.com
   vercel --prod --yes
   ```

---

**Ready to deploy? Get your Groq API key at: https://console.groq.com/keys** 🚀
