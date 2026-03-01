# Document Q&A RAG System

A production-quality Retrieval-Augmented Generation (RAG) system for querying multiple PDF and text documents using semantic search and Google's Gemini AI language models.

## Features

- 📄 **Multi-format Support**: Upload and query PDF documents and text files (.txt)
- 🔍 **Semantic Search**: Advanced vector similarity search using FAISS
- 🤖 **Grounded Responses**: Answers strictly based on document content with source attribution
- 🎯 **Hybrid Search**: Combines semantic similarity with keyword matching
- 📊 **Confidence Scoring**: Provides confidence levels for generated answers
- 💬 **Interactive Chat**: Streamlit-based user interface with chat history
- ⚙️ **Configurable**: Adjustable retrieval parameters and search modes

## System Architecture

```
├── config.py       # Centralized configuration management
├── ingest.py       # Document loading, chunking, and indexing
├── retriever.py    # FAISS similarity search and retrieval
├── qa_engine.py    # RAG pipeline and response generation
├── app.py          # Streamlit user interface
└── requirements.txt # Python dependencies
```

## Quick Start

### 🐳 Docker Deployment (Recommended)

#### 1. Prerequisites
```bash
# Install Docker and Docker Compose
# Windows: Download Docker Desktop from https://docker.com
# macOS: Download Docker Desktop from https://docker.com
# Linux: sudo apt install docker.io docker-compose
```

#### 2. Setup
```bash
# Clone or download the project
cd pdfextractor

# Copy environment template
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux

# Edit .env file and add your Google API key
# Get key from: https://aistudio.google.com/app/apikey
```

#### 3. Run with Docker
```bash
# Windows
run.bat

# macOS/Linux
./run.sh

# Or manually:
docker-compose up --build
```

#### 4. Access the Application
Open your browser and go to: **http://localhost:8501**

### 🐍 Local Python Installation (Alternative)

#### 1. Installation

```bash
# Clone or download the project files
cd pdfextractor

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. API Key Setup

Get your Google API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

**Option A: Environment Variable**
```bash
# Windows (Command Prompt)
set GOOGLE_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:GOOGLE_API_KEY="your_api_key_here"

# macOS/Linux
export GOOGLE_API_KEY="your_api_key_here"
```

**Option B: .env File**
Create a `.env` file in the project directory:
```
GOOGLE_API_KEY=your_api_key_here
```

#### 3. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Docker Commands

```bash
# Build and start the application
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Development mode (with live reload)
docker-compose --profile dev up

# Rebuild after code changes
docker-compose up --build

# Access container shell
docker-compose exec pdfextractor bash

# Remove everything (including volumes)
docker-compose down -v
```

## Usage Guide

1. **Open the sidebar** and navigate to "Document Management"
2. **Click "Choose PDF or TXT files"** and select your documents
3. **Click "Process Documents"** to build the knowledge base
4. **Wait for processing** - you'll see a success message when complete

### Asking Questions

1. **Type your question** in the main chat interface
2. **Click "Ask"** for a standard answer
3. **Click "Explain"** for detailed retrieval information
4. **View sources** and confidence scores with each answer

### Settings

- **Documents to retrieve**: Number of chunks to consider (1-10)
- **Similarity threshold**: Minimum relevance score (0.0-1.0)
- **Hybrid search**: Enable keyword + semantic search combination

## Configuration

### Key Parameters (config.py)

```python
# Document Processing
CHUNK_SIZE = 1000          # Characters per chunk
CHUNK_OVERLAP = 200        # Overlap between chunks

# Retrieval
TOP_K_RETRIEVAL = 5        # Default chunks to retrieve
SIMILARITY_THRESHOLD = 0.7  # Minimum similarity score

# Models
EMBEDDING_MODEL = "models/text-embedding-004"
LLM_MODEL = "gemini-1.5-flash"
LLM_TEMPERATURE = 0.0      # Factual responses
```

### File Limits

- **Supported formats**: PDF, TXT
- **Maximum file size**: 50 MB per file
- **Recommended**: < 10 MB for optimal performance

## API Usage

You can also use the system programmatically:

```python
from qa_engine import QAEngine
from ingest import DocumentIngester

# Initialize components
ingester = DocumentIngester()
qa_engine = QAEngine()

# Ingest documents
ingester.ingest_documents(['document1.pdf', 'document2.txt'])

# Ask questions
result = qa_engine.answer_question("What is the main topic?")
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
print(f"Confidence: {result['confidence_score']:.2f}")
```

## Advanced Features

### Batch Processing

```python
queries = [
    "What is the main topic?",
    "Who are the key stakeholders?",
    "What are the recommendations?"
]

results = qa_engine.batch_answer_questions(queries)
for result in results:
    print(f"Q: {result['query']}")
    print(f"A: {result['answer']}\n")
```

### Hybrid Search

```python
# Enable hybrid search for better keyword matching
result = qa_engine.answer_question(
    "specific technical term",
    use_hybrid_search=True
)
```

### Index Management

```python
# Check index statistics
stats = qa_engine.retriever.get_index_statistics()
print(f"Total documents: {stats['total_sources']}")
print(f"Total chunks: {stats['total_chunks']}")

# Add new documents to existing index
ingester.add_documents_to_existing_index(['new_document.pdf'])
qa_engine.reload_retriever()
```

## Troubleshooting

### Common Issues

**1. "No Google API key found"**
- Ensure your API key is set as an environment variable or in a .env file
- Verify the key is valid and has Gemini API access enabled

**2. "No document index found"**
- Upload and process documents first using the Streamlit interface
- Check that files are in supported formats (PDF, TXT)

**3. "Processing error"**
- Verify file is not corrupted
- Check file size is under 50MB
- Ensure PDF is text-searchable (not just images)

**4. "Low confidence answers"**
- Try adjusting similarity threshold (lower values)
- Use more descriptive, specific questions
- Enable hybrid search for better keyword matching

### Performance Optimization

**For Large Document Collections:**
- Increase `TOP_K_RETRIEVAL` for more comprehensive answers
- Adjust `CHUNK_SIZE` based on document structure
- Monitor memory usage with very large indexes

**For Better Answer Quality:**
- Use specific, focused questions
- Include relevant keywords from documents
- Enable hybrid search for technical documents

## System Requirements

- **Docker & Docker Compose**: For containerized deployment (Recommended)
- **Python**: 3.8 or higher (if running without Docker)
- **Memory**: 4GB+ RAM recommended for large document sets
- **Storage**: Space for document index (typically 10-50MB per 100 documents)
- **Network**: Internet connection for Google AI API calls

## Security Notes

- API keys are not stored in the application
- Documents are processed locally
- Only text content is sent to Google AI (not entire files)
- FAISS index is stored locally on disk

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Ensure your Google API key is valid and has Gemini access enabled

## License

This project is provided for educational and development purposes.