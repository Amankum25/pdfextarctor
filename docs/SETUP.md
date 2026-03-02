# 🚀 Setup Guide - PDF Extractor RAG System

## Overview

This system now supports **flexible model selection**:
- **Embeddings**: Local (sentence-transformers) or Google Gemini
- **LLM**: Groq (recommended), OpenAI, or local Ollama
- **Optimized for**: Speed, cost-efficiency, and privacy

---

## 📋 Prerequisites

- Python 3.9 or higher
- Node.js 18+ (for frontend)
- Git

---

## 🎯 Quick Start (Recommended Setup)

### Option 1: FREE Local Embeddings + Groq LLM (Recommended)

**Best for:** Most users, balance of speed and quality

```bash
# 1. Clone and navigate to project
cd pdfextarctor

# 2. Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env  # Windows
# cp .env.example .env    # macOS/Linux

# 5. Edit .env file:
# - Set EMBEDDING_PROVIDER=local
# - Set GROQ_API_KEY=<your_key_from_console.groq.com>
# - Leave LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2

# 6. Start backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 7. In a new terminal, start frontend
cd frontend
npm install
npm run dev
```

**Access at:** http://localhost:5173

---

## 🔧 Configuration Options

### Embedding Providers

#### 1. **Local Embeddings (Recommended)** 🆓

**Pros:**
- ✅ Completely FREE
- ✅ No API keys needed
- ✅ No rate limits
- ✅ Fast (runs on your machine)
- ✅ Privacy-friendly (no data leaves your computer)

**Configuration:**
```env
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
```

**Available Models:**
| Model | Dimensions | Speed | Quality | Use Case |
|-------|-----------|-------|---------|----------|
| all-MiniLM-L6-v2 | 384 | ⚡⚡⚡ Fast | Good | General use (recommended) |
| all-mpnet-base-v2 | 768 | ⚡⚡ Medium | Better | Higher quality needs |
| all-MiniLM-L12-v2 | 384 | ⚡⚡ Medium | Good | Balance speed/quality |
| paraphrase-multilingual-MiniLM-L12-v2 | 384 | ⚡⚡ Medium | Good | Multilingual documents |

#### 2. **Google Gemini Embeddings**

**Pros:**
- ✅ High quality
- ✅ Good for complex queries

**Cons:**
- ❌ Requires API key
- ❌ Has rate limits
- ❌ Sends data to Google

**Configuration:**
```env
EMBEDDING_PROVIDER=google
GOOGLE_API_KEY=your_google_api_key_here
```

Get API key: https://aistudio.google.com/app/apikey

---

### LLM Providers

#### 1. **Groq (Recommended)** ⚡

**Pros:**
- ✅ Extremely FAST (fastest inference)
- ✅ FREE tier with generous limits
- ✅ High quality (Llama 3.3 70B)
- ✅ Easy to use

**Configuration:**
```env
LLM_PROVIDER=groq
LLM_MODEL_NAME=llama-3.3-70b-versatile
GROQ_API_KEY=your_groq_api_key_here
```

Get API key: https://console.groq.com/keys

**Available Models:**
- `llama-3.3-70b-versatile` (recommended)
- `llama-3.1-70b-versatile`
- `mixtral-8x7b-32768`
- `gemma-7b-it`

#### 2. **Ollama (Completely FREE)** 🆓

**Pros:**
- ✅ Completely FREE
- ✅ Runs locally (privacy)
- ✅ No API keys
- ✅ No rate limits

**Cons:**
- ❌ Requires local installation
- ❌ Slower inference
- ❌ Requires good hardware (8GB+ RAM)

**Configuration:**
```env
LLM_PROVIDER=ollama
LLM_MODEL_NAME=llama3
```

**Setup Ollama:**
```bash
# Install from ollama.ai
# Then pull a model:
ollama pull llama3
ollama serve
```

#### 3. **OpenAI**

**Configuration:**
```env
LLM_PROVIDER=openai
LLM_MODEL_NAME=gpt-4
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 🎨 Recommended Configurations

### 1. **Best Overall: Local + Groq** 🌟

Best balance of speed, cost, and quality.

```env
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_PROVIDER=groq
LLM_MODEL_NAME=llama-3.3-70b-versatile
GROQ_API_KEY=your_groq_api_key_here
```

**Cost:** FREE (Groq free tier)  
**Speed:** ⚡⚡⚡ Very Fast  
**Quality:** ⭐⭐⭐⭐ Excellent

---

### 2. **Completely FREE Setup** 💰

No API keys needed at all.

```env
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_PROVIDER=ollama
LLM_MODEL_NAME=llama3
```

**Cost:** FREE  
**Speed:** ⚡⚡ Medium (depends on hardware)  
**Quality:** ⭐⭐⭐ Good

**Requirements:** Install Ollama from https://ollama.ai

---

### 3. **Highest Quality: Better Models + Groq**

Maximum quality embeddings and LLM.

```env
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=all-mpnet-base-v2
LLM_PROVIDER=groq
LLM_MODEL_NAME=llama-3.3-70b-versatile
GROQ_API_KEY=your_groq_api_key_here
```

**Cost:** FREE (Groq free tier)  
**Speed:** ⚡⚡ Medium (slower embeddings)  
**Quality:** ⭐⭐⭐⭐⭐ Excellent

---

### 4. **Google Gemini Embeddings + Groq**

Use Google for embeddings if you already have API access.

```env
EMBEDDING_PROVIDER=google
GOOGLE_API_KEY=your_google_api_key_here
LLM_PROVIDER=groq
LLM_MODEL_NAME=llama-3.3-70b-versatile
GROQ_API_KEY=your_groq_api_key_here
```

**Cost:** FREE (both have free tiers)  
**Speed:** ⚡⚡⚡ Fast  
**Quality:** ⭐⭐⭐⭐⭐ Excellent

---

## 📦 Installation Details

### Backend Setup

```bash
# Navigate to project
cd pdfextarctor

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env  # Windows
# cp .env.example .env    # macOS/Linux

# Edit .env with your preferred configuration

# Start backend server
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

### Frontend Setup

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

---

## 🔍 Testing Your Setup

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "online",
  "ready": false,
  "document_stats": {}
}
```

### 2. Upload a Test PDF

Open http://localhost:5173 and upload a PDF document.

### 3. Ask a Question

Try: "What is this document about?"

---

## 🐛 Troubleshooting

### Model Download Issues

**Problem:** Local embedding model not downloading

**Solution:**
```bash
# Manually download the model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Groq API Issues

**Problem:** "API key not found"

**Solution:**
1. Check your .env file has `GROQ_API_KEY=...`
2. Restart the backend server after editing .env
3. Verify key at https://console.groq.com/keys

### Memory Issues

**Problem:** "Out of memory" with local embeddings

**Solution:**
1. Use a smaller model: `all-MiniLM-L6-v2`
2. Process fewer documents at once
3. Reduce `CHUNK_SIZE` in .env

### Port Already in Use

**Problem:** Port 8000 or 5173 already in use

**Solution:**
```bash
# Backend - use different port
uvicorn main:app --port 8001

# Frontend - edit vite.config.js to change port
```

---

## 📊 Performance Benchmarks

### Embedding Generation (1000 chunks)

| Provider | Model | Time | Quality |
|----------|-------|------|---------|
| Local | all-MiniLM-L6-v2 | ~5s | Good |
| Local | all-mpnet-base-v2 | ~12s | Better |
| Google | text-embedding-004 | ~15s | Excellent |

### Query Response Time

| LLM Provider | Model | Time |
|--------------|-------|------|
| Groq | llama-3.3-70b | ~2s |
| Ollama | llama3 | ~10s |
| OpenAI | gpt-4 | ~5s |

---

## 🔒 Security & Privacy

### Data Privacy by Configuration

| Setup | Data Sent Externally |
|-------|---------------------|
| Local + Ollama | ❌ Nothing |
| Local + Groq | ✅ Only queries (not documents) |
| Google + Groq | ✅ Documents + queries |

**Recommendation:** Use local embeddings for maximum privacy. Documents stay on your machine, only queries are sent to LLM.

---

## 🌐 Docker Deployment (Optional)

```bash
# Build and run with Docker
docker-compose up --build

# Access at:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

---

## 📚 Additional Resources

- **Groq Documentation:** https://console.groq.com/docs
- **Sentence Transformers:** https://www.sbert.net/
- **Ollama Models:** https://ollama.ai/library
- **Google AI Studio:** https://aistudio.google.com/

---

## 💡 Tips for Best Performance

1. **Use local embeddings** - Faster and no API limits
2. **Use Groq for LLM** - Best speed/quality ratio
3. **Enable Redis caching** - Speeds up repeated queries
4. **Adjust chunk size** - Smaller = faster, larger = better context
5. **Use SSD storage** - Faster FAISS index loading

---

## 🆘 Support

Issues? Check:
1. All API keys are correct in .env
2. Virtual environment is activated
3. All dependencies installed: `pip install -r requirements.txt`
4. Backend is running on port 8000
5. Frontend is running on port 5173

Still stuck? Open an issue on GitHub!

---

**Happy Document Querying! 📄✨**
