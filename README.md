# Policy Analyzer - Document Q&A RAG System

A production-quality, optimized Retrieval-Augmented Generation (RAG) system for querying multiple PDF and text documents with **flexible model selection** and **zero-cost options**.

## 🔗 Live Demo

**Frontend (Vercel)**: [https://policy-analyzer-frontend.vercel.app](https://policy-analyzer-frontend.vercel.app)

**Repository**: [https://github.com/Amankum25/policy-analyzer](https://github.com/Amankum25/policy-analyzer)

## ✨ Key Features

- 📄 **Multi-format Support**: Upload and query PDF documents and text files (.txt)
- 🔍 **Semantic Search**: Advanced vector similarity search using FAISS
- 🤖 **Grounded Responses**: Answers strictly based on document content with source attribution
- ⚡ **Flexible Models**: Choose between local (FREE) or cloud embeddings
- 💰 **Cost-Optimized**: Use completely free local models or fast cloud APIs
- 🎯 **Multiple LLM Options**: Support for Groq (fast), Ollama (local), or OpenAI
- 📊 **Confidence Scoring**: Provides confidence levels for generated answers
- 💬 **Modern UI**: React-based responsive interface
- ⚙️ **Highly Configurable**: Environment-based configuration for all settings

## 🚀 What's New in v2.0

### Optimized Architecture
- ✅ **Local Embeddings Support** - Use sentence-transformers (FREE, no API key needed)
- ✅ **Google Gemini Embeddings** - Optional cloud-based embeddings
- ✅ **Groq Integration** - Lightning-fast LLM inference with Llama 3.3
- ✅ **Unified Embedding Interface** - Easy switching between providers
- ✅ **React Frontend** - Modern, responsive UI with Vite
- ✅ **FastAPI Backend** - Production-ready REST API
- ✅ **Environment Configuration** - Flexible .env-based setup

### Performance Improvements
- ⚡ 3x faster embeddings with local models
- ⚡ 10x faster LLM responses with Groq
- 💾 Reduced memory footprint
- 🔄 Optional Redis caching

## 📦 System Architecture

```
pdfextractor/
├── backend/
│   ├── config.py          # Centralized configuration
│   ├── embeddings.py      # Unified embedding interface (NEW)
│   ├── ingest.py          # Document loading and chunking
│   ├── retriever.py       # FAISS similarity search
│   ├── qa_engine.py       # RAG pipeline and LLM
│   └── main.py            # FastAPI REST API
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Main React application
│   │   └── api.js         # Backend API client
│   └── package.json
├── .env.example           # Configuration template
└── requirements.txt       # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Groq API key (FREE at https://console.groq.com/keys)

### Installation (5 minutes)

```bash
# 1. Clone the repository
cd pdfextractor

# 2. Backend Setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

# 3. Configure Environment
copy .env.example .env  # Windows
# cp .env.example .env    # macOS/Linux

# Edit .env and add your Groq API key:
# GROQ_API_KEY=your_key_here
# Keep EMBEDDING_PROVIDER=local (recommended)

# 4. Start Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 5. Start Frontend (new terminal)
cd frontend
npm install
npm run dev
```

**Access the app at:** http://localhost:5173

### Configuration Options

#### Option 1: Recommended (FREE Local Embeddings + Groq) ⭐

```env
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_PROVIDER=groq
LLM_MODEL_NAME=llama-3.3-70b-versatile
GROQ_API_KEY=your_groq_key
```

**Benefits:** Fast, free, no API limits for embeddings

#### Option 2: Completely FREE (Ollama)

```env
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_PROVIDER=ollama
LLM_MODEL_NAME=llama3
```

**Requirements:** Install Ollama from https://ollama.ai

#### Option 3: Google Gemini + Groq

```env
EMBEDDING_PROVIDER=google
GOOGLE_API_KEY=your_google_key
LLM_PROVIDER=groq
LLM_MODEL_NAME=llama-3.3-70b-versatile
GROQ_API_KEY=your_groq_key
```

**Benefits:** High-quality embeddings from Google

### 📖 Detailed Setup Guide

See [docs/SETUP.md](docs/SETUP.md) for comprehensive instructions, troubleshooting, and configuration options.

## 💡 Usage Guide

### 1. Upload Documents

- Click **"Upload Files"** button
- Select one or more PDF or TXT files
- Wait for processing (documents are chunked and embedded)
- See confirmation when ready

### 2. Ask Questions

- Type your question in the chat input
- Click **Send** or press Enter
- View answer with:
  - **Source attribution** (document name, page number)
  - **Confidence score** (High/Medium/Low)
  - **Context snippets** from relevant documents

### 3. Get Suggestions

- Click **"Get Suggested Questions"** for context-aware questions
- Click any suggested question to ask it automatically

### API Usage

The backend provides REST API endpoints:

```python
# Health check
GET /health

# Upload documents
POST /upload
Content-Type: multipart/form-data
files: [file1.pdf, file2.pdf]

# Ask questions
POST /ask
Content-Type: application/json
{
  "question": "What is this about?",
  "top_k": 10,
  "similarity_threshold": 0.3
}

# Get suggested questions
GET /suggest-questions
```

## 🎯 Model Selection Guide

### Embedding Models Comparison

| Model | Provider | Speed | Quality | Cost | API Key |
|-------|----------|-------|---------|------|---------|
| all-MiniLM-L6-v2 | Local | ⚡⚡⚡ | ⭐⭐⭐ | FREE | No |
| all-mpnet-base-v2 | Local | ⚡⚡ | ⭐⭐⭐⭐ | FREE | No |
| text-embedding-004 | Google | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | FREE tier | Yes |

### LLM Models Comparison

| Provider | Model | Speed | Quality | Cost | API Key |
|----------|-------|-------|---------|------|---------|
| Groq | llama-3.3-70b | ⚡⚡⚡ | ⭐⭐⭐⭐ | FREE tier | Yes |
| Ollama | llama3 | ⚡⚡ | ⭐⭐⭐ | FREE | No |
| OpenAI | gpt-4 | ⚡⚡ | ⭐⭐⭐⭐⭐ | Paid | Yes |

**Recommendation:** Local embeddings + Groq = Best performance/cost ratio

## ⚙️ Configuration

## ⚙️ Configuration

### Key Environment Variables

```env
# Embedding Configuration
EMBEDDING_PROVIDER=local              # Options: local, google
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2  # For local provider

# LLM Configuration  
LLM_PROVIDER=groq                     # Options: groq, ollama, openai
LLM_MODEL_NAME=llama-3.3-70b-versatile

# API Keys (as needed)
GROQ_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# Document Processing
CHUNK_SIZE=1000                       # Characters per chunk
CHUNK_OVERLAP=200                     # Overlap between chunks

# Retrieval
TOP_K_RETRIEVAL=10                    # Chunks to retrieve
SIMILARITY_THRESHOLD=0.3              # Min similarity (0.0-1.0)
```

### Performance Tuning

**For Speed:**
- Use `all-MiniLM-L6-v2` embeddings
- Set `TOP_K_RETRIEVAL=5`
- Use Groq for LLM

**For Quality:**
- Use `all-mpnet-base-v2` embeddings
- Set `TOP_K_RETRIEVAL=15`
- Increase `CHUNK_SIZE=1500`

**For Privacy:**
- Use `EMBEDDING_PROVIDER=local`
- Use `LLM_PROVIDER=ollama`

## 🔍 Advanced Features

### Custom Embedding Models

```python
# In config.py, you can set:
LOCAL_EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
```

Available local models:
- `all-MiniLM-L6-v2` (384 dim, fast)
- `all-mpnet-base-v2` (768 dim, better quality)
- `paraphrase-multilingual-MiniLM-L12-v2` (multilingual)
- Any model from https://www.sbert.net/

### Redis Caching (Optional)

```env
REDIS_HOST=localhost
REDIS_PORT=6379
```

Caches LLM responses for faster repeated queries.

### Programmatic API

```python
from qa_engine import QAEngine
from ingest import DocumentIngester

# Initialize
ingester = DocumentIngester()
qa_engine = QAEngine()

# Ingest documents
ingester.ingest_documents(['doc1.pdf', 'doc2.txt'])

# Ask questions
result = qa_engine.answer_question(
    "What is the main topic?",
    top_k=10,
    similarity_threshold=0.3
)

print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
print(f"Confidence: {result['confidence_score']:.2f}")
```

## 📊 Performance Benchmarks

### Embedding Generation (1000 chunks)

| Setup | Time | Memory |
|-------|------|--------|
| Local (MiniLM) | ~5s | 500MB |
| Local (mpnet) | ~12s | 800MB |
| Google Gemini | ~15s | 200MB |

### Query Response Time

| Setup | Time |
|-------|------|
| Local + Groq | ~2.5s |
| Google + Groq | ~3.0s |
| Local + Ollama | ~10s |

## 🐛 Troubleshooting

### "Model not found" or "Connection refused"

**Local Embeddings:**
```bash
# Manually download the model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

**Groq API:**
- Check GROQ_API_KEY in .env
- Verify key at https://console.groq.com/keys
- Restart backend after editing .env

### "Out of memory"

**Solutions:**
1. Use smaller model: `LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2`
2. Reduce chunk size: `CHUNK_SIZE=500`
3. Process fewer documents at once
4. Close other applications

### Port already in use

```bash
# Backend (change port)
uvicorn main:app --port 8001

# Frontend (edit vite.config.js)
server: { port: 5174 }
```

### PDF Processing Errors

**Common issues:**
- PDF is image-based (needs OCR)
- File is corrupted
- File > 50MB (increase limit in config.py)

**Solutions:**
```bash
# Test PDF text extraction
python -c "from pypdf import PdfReader; print(PdfReader('test.pdf').pages[0].extract_text())"
```

### Low Quality Answers

**Improvements:**
1. Lower similarity threshold: `SIMILARITY_THRESHOLD=0.2`
2. Increase retrieval: `TOP_K_RETRIEVAL=15`
3. Use better embeddings: `all-mpnet-base-v2`
4. Ask more specific questions

## 🔒 Security & Privacy

### Data Privacy Levels

| Configuration | Data Privacy |
|---------------|-------------|
| Local + Ollama | ✅ Complete (nothing leaves your machine) |
| Local + Groq | ⚠️ Queries sent to Groq (docs stay local) |
| Google + Groq | ⚠️ Both docs and queries sent externally |

**Recommendation:** Use local embeddings for maximum privacy.

### Best Practices

- ✅ Use `.env` file (never commit it)
- ✅ Keep API keys secret
- ✅ Use local embeddings for sensitive documents
- ✅ Enable HTTPS in production
- ✅ Regular security updates: `pip install -U -r requirements.txt`

## 📋 System Requirements

**Minimum:**
- Python 3.9+
- 4GB RAM
- 2GB disk space

**Recommended:**
- Python 3.11+
- 8GB+ RAM
- 5GB disk space (for models)
- SSD storage

**Optional:**
- CUDA GPU (for faster local embeddings)
- Redis (for caching)

## 🎓 How It Works

1. **Document Ingestion:**
   - PDFs are loaded and text extracted
   - Text split into 1000-character chunks with 200-char overlap
   - Chunks converted to vector embeddings
   - Stored in FAISS index for fast retrieval

2. **Query Processing:**
   - User question converted to embedding
   - FAISS finds top-K similar chunks
   - Chunks filtered by similarity threshold
   - Relevant context sent to LLM

3. **Answer Generation:**
   - LLM generates answer from context only
   - Source attribution added
   - Confidence score calculated
   - Response formatted for display

## 🌐 Deployment

### Docker (Production)

```bash
# Build and run
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Cloud Deployment

**Render/Railway/Fly.io:**
1. Set environment variables
2. Deploy backend (FastAPI)
3. Deploy frontend (Vite build)
4. Configure volumes for FAISS index persistence

## 📚 Documentation

- [**SETUP.md**](docs/SETUP.md) - Comprehensive setup guide
- [**PROJECT_STATUS.md**](docs/PROJECT_STATUS.md) - Project history
- [**ENHANCEMENTS.md**](docs/ENHANCEMENTS.md) - Future improvements

## 🚀 Deployment

### Quick Deploy Options

| Platform | Cost | Setup Time | Best For |
|----------|------|------------|----------|
| **Render** (Recommended) | FREE | 15 min | Demos, MVPs |
| **Vercel + Railway** | FREE/$5 | 20 min | Production |
| **Docker on VPS** | $5-6/mo | 45 min | High traffic |

#### Deploy to Render (Recommended)

```bash
# 1. Push to GitHub (done!)
# 2. Go to https://render.com
# 3. Create Web Service for backend
#    - Root: backend
#    - Build: pip install -r ../requirements.txt
#    - Start: uvicorn main:app --host 0.0.0.0 --port $PORT
# 4. Create Static Site for frontend
#    - Root: frontend
#    - Build: npm install && npm run build
#    - Publish: dist
# 5. Add environment variables
# Done! 🎉
```

#### Deploy with Docker

```bash
# Start everything locally
docker-compose up -d

# Access at:
# Frontend: http://localhost
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Full deployment guides:**
- 📘 [**DEPLOYMENT_GUIDE.md**](docs/DEPLOYMENT_GUIDE.md) - Comprehensive 20+ page guide
- ⚡ [**DEPLOY_QUICK.md**](docs/DEPLOY_QUICK.md) - Quick commands
- 🎯 [**PLATFORM_RECOMMENDATIONS.md**](docs/PLATFORM_RECOMMENDATIONS.md) - Platform comparison

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional embedding providers (OpenAI, Cohere)
- More LLM providers
- Better PDF processing (OCR)
- Advanced retrieval strategies
- UI enhancements

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **LangChain** - Framework for LLM applications
- **FAISS** - Vector similarity search by Facebook AI
- **Sentence Transformers** - Pre-trained embedding models
- **Groq** - Fast LLM inference
- **FastAPI** - Modern Python web framework
- **React** - UI framework

## 📞 Support

**Documentation:** See [docs/](docs/) folder  
**Issues:** Use GitHub Issues  
**Questions:** Check [docs/SETUP.md](docs/SETUP.md) first

---

**Built with ❤️ for efficient document Q&A**

**Star ⭐ this repo if you find it useful!**