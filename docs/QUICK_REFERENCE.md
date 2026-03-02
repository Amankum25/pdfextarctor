# 🚀 Quick Reference Guide

## One-Line Setup Commands

### Windows PowerShell

```powershell
# Complete setup
python -m venv .venv ; .\.venv\Scripts\Activate.ps1 ; pip install -r requirements.txt ; copy .env.example .env

# Start backend (from backend/ directory)
cd backend ; uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (from frontend/ directory, new terminal)
cd frontend ; npm install ; npm run dev
```

### macOS/Linux

```bash
# Complete setup
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && cp .env.example .env

# Start backend (from backend/ directory)
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (from frontend/ directory, new terminal)
cd frontend && npm install && npm run dev
```

---

## Environment Configuration Cheat Sheet

### Recommended Setup (Local + Groq)
```env
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_PROVIDER=groq
LLM_MODEL_NAME=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_your_key_here
```

### Completely FREE Setup
```env
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_PROVIDER=ollama
LLM_MODEL_NAME=llama3
```
*Requires Ollama: `ollama pull llama3 && ollama serve`*

### Google Gemini Setup
```env
EMBEDDING_PROVIDER=google
GOOGLE_API_KEY=your_google_key_here
LLM_PROVIDER=groq
LLM_MODEL_NAME=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_your_key_here
```

---

## API Keys Quick Links

| Service | Get Key From | Free Tier |
|---------|-------------|-----------|
| Groq | https://console.groq.com/keys | ✅ Yes |
| Google | https://aistudio.google.com/app/apikey | ✅ Yes |
| OpenAI | https://platform.openai.com/api-keys | ❌ Paid |

---

## Testing Commands

### Test Backend

```bash
# Health check
curl http://localhost:8000/health

# Expected: {"status":"online","ready":false,"document_stats":{}}
```

### Test Embedding Provider

```python
# In Python shell (with venv activated)
from backend.embeddings import get_embedding_provider
provider = get_embedding_provider()
print(provider.embed_query("test"))
```

### Test FAISS Index

```python
from backend.retriever import DocumentRetriever
retriever = DocumentRetriever()
print(retriever.is_index_available())
```

---

## Common Commands

### Backend Management

```bash
# Start backend (development)
cd backend
uvicorn main:app --reload --port 8000

# Start backend (production)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Check logs
# Logs appear in terminal, or redirect to file:
uvicorn main:app --log-level info > backend.log 2>&1
```

### Frontend Management

```bash
# Development mode
cd frontend
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

### Dependency Management

```bash
# Update all dependencies
pip install -U -r requirements.txt

# Install specific package
pip install package-name

# Freeze current versions
pip freeze > requirements.lock

# Install from lock file
pip install -r requirements.lock
```

### Environment Management

```bash
# Create .env from example
copy .env.example .env     # Windows
cp .env.example .env       # macOS/Linux

# Edit .env
notepad .env               # Windows
nano .env                  # macOS/Linux

# Load .env in terminal (for testing)
# Windows PowerShell:
Get-Content .env | ForEach-Object { $var = $_.Split('='); [Environment]::SetEnvironmentVariable($var[0], $var[1]) }

# macOS/Linux:
export $(cat .env | xargs)
```

---

## Model Downloads

### Pre-download Local Embeddings

```bash
# Activate venv first
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Pre-download Ollama Models

```bash
ollama pull llama3
ollama pull llama3:70b
ollama pull mixtral
```

---

## Port Configuration

| Service | Default Port | Change Command |
|---------|-------------|----------------|
| Backend | 8000 | `uvicorn main:app --port 8001` |
| Frontend | 5173 | Edit `vite.config.js` |
| Redis | 6379 | Edit `.env`: `REDIS_PORT=6380` |

---

## Troubleshooting Quick Fixes

### Backend won't start
```bash
# Check if port is in use
netstat -ano | findstr :8000     # Windows
lsof -i :8000                    # macOS/Linux

# Kill process using port
# Windows: taskkill /PID <PID> /F
# macOS/Linux: kill -9 <PID>
```

### Frontend won't build
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### FAISS index corrupted
```bash
# Delete and recreate
rm -rf backend/faiss_index
# Upload documents again via UI
```

### Out of memory
```bash
# Reduce chunk size in .env
CHUNK_SIZE=500
TOP_K_RETRIEVAL=5
```

---

## Performance Testing

### Load Test Backend

```bash
# Install hey (HTTP load testing)
# Windows: choco install hey
# macOS: brew install hey
# Linux: go install github.com/rakyll/hey@latest

# Test upload endpoint
hey -n 100 -c 10 http://localhost:8000/health

# Test ask endpoint
hey -n 100 -c 10 -m POST -H "Content-Type: application/json" \
  -d '{"question":"test","top_k":10}' \
  http://localhost:8000/ask
```

### Measure Embedding Speed

```python
import time
from backend.embeddings import get_embedding_provider

provider = get_embedding_provider()
texts = ["test text"] * 1000

start = time.time()
embeddings = provider.embed_documents(texts)
print(f"Time: {time.time() - start:.2f}s for 1000 chunks")
```

---

## Docker Commands (Optional)

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop
docker-compose down

# Clean everything
docker-compose down -v
```

---

## Useful Aliases (Add to your shell profile)

### PowerShell ($PROFILE)

```powershell
function Start-PDFBackend { cd backend; uvicorn main:app --reload --port 8000 }
function Start-PDFFrontend { cd frontend; npm run dev }
function Activate-PDFEnv { .\.venv\Scripts\Activate.ps1 }
```

### Bash/Zsh (~/.bashrc or ~/.zshrc)

```bash
alias pdf-backend="cd backend && uvicorn main:app --reload --port 8000"
alias pdf-frontend="cd frontend && npm run dev"
alias pdf-activate="source .venv/bin/activate"
alias pdf-setup="python -m venv .venv && pdf-activate && pip install -r requirements.txt"
```

---

## Environment Variables Reference

### Required Variables

```env
# For Groq LLM
GROQ_API_KEY=your_key

# For Google Embeddings (if EMBEDDING_PROVIDER=google)
GOOGLE_API_KEY=your_key
```

### Optional Variables

```env
# Embedding Configuration
EMBEDDING_PROVIDER=local              # local, google
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2

# LLM Configuration
LLM_PROVIDER=groq                     # groq, ollama, openai
LLM_MODEL_NAME=llama-3.3-70b-versatile

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Retrieval
TOP_K_RETRIEVAL=10
SIMILARITY_THRESHOLD=0.3

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## Model Selection Matrix

### When to use each embedding model:

| Use Case | Recommended Model | Reason |
|----------|------------------|--------|
| General documents | all-MiniLM-L6-v2 | Fast, good quality |
| High-quality needs | all-mpnet-base-v2 | Better accuracy |
| Multilingual | paraphrase-multilingual-MiniLM-L12-v2 | Multi-language support |
| Cloud-based | text-embedding-004 (Google) | Highest quality |

### When to use each LLM:

| Use Case | Recommended LLM | Reason |
|----------|----------------|--------|
| Speed + quality | Groq (llama-3.3-70b) | Fastest inference |
| Completely free | Ollama (llama3) | No API costs |
| Best quality | OpenAI (gpt-4) | Highest accuracy |

---

## Quick Debug Checklist

- [ ] Virtual environment activated?
- [ ] All dependencies installed? `pip list | grep langchain`
- [ ] .env file exists and configured?
- [ ] API keys valid and set?
- [ ] Backend running on port 8000?
- [ ] Frontend running on port 5173?
- [ ] Firewalls/antivirus not blocking?
- [ ] Documents uploaded via UI?

---

**For detailed guides, see:**
- [SETUP.md](SETUP.md) - Complete setup instructions
- [README.md](../README.md) - Project overview
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Current status

---

*Last updated: March 2026*
