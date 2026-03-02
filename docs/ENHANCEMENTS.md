# PDF Q&A System - Enhanced Exam Preparation Tool

## 🎯 Overview
An advanced RAG (Retrieval-Augmented Generation) system powered by Google Gemini AI that provides comprehensive, detailed answers from PDF and text documents, specifically designed for exam preparation.

## ✨ Key Features

### 1. **Extensive Question Generation**
- **LLM-Based Generation**: Uses Google Gemini to automatically generate 25+ contextually relevant questions from uploaded documents
- **Intelligent Fallback**: If LLM generation fails, uses smart programmatic generation based on content analysis
- **Dynamic Updates**: Questions refresh automatically based on document content
- **Multi-Level Coverage**: Questions span various difficulty levels and Bloom's taxonomy

### 2. **Detailed Answer Generation**
- **Structured Responses**: Answers follow a clear format with:
  - Direct answer upfront
  - Detailed explanations with subheadings
  - Key points in bullet format
  - Concrete examples from documents
  - Related concepts for fuller understanding
  - Exam tips for retention and application
- **High Confidence**: Retrieves top 10 most relevant chunks with 0.3 similarity threshold for comprehensive coverage
- **Markdown Formatting**: Answers include proper formatting with headers, bold text, bullet points, and numbered lists

### 3. **Enhanced Answer Visibility**
- **Beautiful UI**: Modern, gradient-styled interface with professional design
- **Confidence Indicators**: Visual badges showing High/Medium/Low confidence with color coding
- **Source Attribution**: Detailed source references with:
  - File name and page number
  - Relevance percentage
  - Content snippets from each source
- **Markdown Rendering**: Automatic conversion of markdown to formatted HTML for better readability
- **Smooth Animations**: Answer section slides in smoothly with fade effect

### 4. **Improved User Experience**
- **Real-Time Status**: System readiness indicator showing document count
- **Suggested Questions Panel**: Clickable questions that auto-fill and execute
- **Multi-File Upload**: Support for multiple PDF and TXT files simultaneously
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Keyboard Shortcuts**: Ctrl+Enter to submit questions quickly
- **Debug Tools**: Built-in debug and simple test pages for troubleshooting

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- Groq API Key

### Installation

1. **Clone/Download the repository**
```bash
cd pdfextractor
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
```

4. **Run the application**
```bash
python web_app.py
```

5. **Open in browser**
Navigate to: http://127.0.0.1:5000

## 📖 Usage Guide

### Uploading Documents
1. Click "Choose PDF or TXT files" button in the sidebar
2. Select one or more documents
3. Wait for processing confirmation
4. Status indicator will show "System Ready" with document count

### Asking Questions
1. **Option A**: Type your own question in the text area
2. **Option B**: Click on any suggested question from the sidebar
3. Press "Get Detailed Answer" or use Ctrl+Enter
4. View comprehensive answer with sources and confidence score

### Understanding Results
- **High Confidence (70%+)**: Very relevant information found
- **Medium Confidence (40-70%)**: Relevant information available
- **Low Confidence (<40%)**: Limited information in documents

### Suggested Questions
- Automatically generated from document content
- 25+ comprehensive questions covering:
  - Fundamental concepts and definitions
  - Analytical and critical thinking
  - Application and problem-solving
  - Evaluation and comparison
  - Specific content-based queries
- Click "🔄 Refresh Questions" to regenerate

## 🛠 Technical Architecture

### Backend Components

#### `qa_engine.py`
- **Enhanced Prompt Engineering**: Detailed system prompt for exam-oriented answers
- **Structured Answer Format**: Enforces consistent, comprehensive response structure
- **Markdown Support**: Returns well-formatted answers with headers, bullets, and emphasis
- **Source Attribution**: Tracks and formats source information with confidence scores

#### `web_app.py`
- **LLM-Based Question Generation**: `generate_dynamic_questions()` uses Gemini to create contextual questions
- **Comprehensive Retrieval Parameters**: 
  - `top_k=10` for more context chunks
  - `similarity_threshold=0.3` for broader coverage
  - `include_chunk_details=True` for detailed source info
- **Robust Error Handling**: Fallback mechanisms for all operations

#### `retriever.py`
- FAISS vector store for efficient similarity search
- Sample text extraction for question generation
- Index statistics and metadata tracking

#### `ingest.py`
- Multi-format support (PDF, TXT, MD)
- Chunking with overlap for context preservation
- Google Gemini embeddings (text-embedding-004)

### Frontend Components

#### `templates/index.html`
- **Modern Design**: Gradient backgrounds, smooth animations, professional styling
- **Dynamic Updates**: Auto-refreshing status and questions
- **Interactive Elements**: Clickable questions, hover effects, loading indicators
- **Markdown Rendering**: JavaScript-based markdown to HTML conversion
- **Source Display**: Formatted source cards with relevance scores
- **Responsive Layout**: Grid-based design that adapts to screen size

#### `templates/debug.html`
- Raw API testing interface
- JSON response viewer
- Endpoint testing buttons

#### `templates/simple_test.html`
- Minimal testing page
- Direct API call verification
- Quick debugging tool

## 📊 API Endpoints

### `GET /`
Main application interface

### `POST /upload`
Upload PDF/TXT files for processing
- **Input**: FormData with file(s)
- **Response**: Success/error message

### `POST /ask`
Get answer to a question
- **Input**: `{"question": "your question"}`
- **Response**: 
```json
{
  "success": true,
  "answer": "detailed formatted answer",
  "sources": [...],
  "confidence": 0.85,
  "has_answer": true
}
```

### `GET /status`
Check system readiness
- **Response**: 
```json
{
  "ready": true,
  "documents": 11,
  "message": "System ready"
}
```

### `GET /suggested-questions`
Get dynamically generated questions
- **Response**: 
```json
{
  "questions": ["question 1", "question 2", ...]
}
```

## 🎓 Best Practices for Exam Preparation

1. **Upload Comprehensive Materials**: Include all relevant study materials for best coverage
2. **Review Suggested Questions**: Auto-generated questions cover key topics
3. **Check Confidence Scores**: High confidence answers are more reliable
4. **Read Source References**: Verify information against original documents
5. **Use Exam Tips**: Pay attention to the exam tips section in answers
6. **Ask Follow-up Questions**: Dig deeper into complex topics
7. **Refresh Questions Regularly**: Generate new questions after uploading more documents

## 🐛 Debugging

### Debug Page
Access at: http://127.0.0.1:5000/debug
- Test individual endpoints
- View raw JSON responses
- Verify system status

### Simple Test Page
Access at: http://127.0.0.1:5000/simple
- Minimal interface for testing
- Direct API calls
- Quick verification

### Common Issues

**Problem**: "No documents loaded"
- **Solution**: Upload documents first using the upload button

**Problem**: Low confidence scores
- **Solution**: Upload more relevant documents or rephrase your question

**Problem**: Questions not showing
- **Solution**: Click "Refresh Questions" or check that documents are loaded

**Problem**: Server not responding
- **Solution**: Check terminal for errors, restart with `python web_app.py`

## 📁 Project Structure

```
pdfextarctor/
├── web_app.py              # Flask application & routes
├── qa_engine.py            # QA logic with enhanced prompts
├── retriever.py            # Document retrieval
├── ingest.py               # Document processing
├── config.py               # Configuration settings
├── templates/
│   ├── index.html          # Main UI (enhanced)
│   ├── debug.html          # Debug interface
│   └── simple_test.html    # Simple test page
├── faiss_index/            # Vector store (generated)
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Configuration

Edit `config.py` to customize:
- `GEMINI_MODEL`: Model to use (default: gemini-1.5-flash)
- `EMBEDDING_MODEL`: Embedding model (default: text-embedding-004)
- `TEMPERATURE`: LLM temperature (default: 0.2 for accuracy)
- `MAX_TOKENS`: Maximum response length (default: 2048)
- `TOP_K_RETRIEVAL`: Number of chunks to retrieve

## 📝 Recent Enhancements

### Version 2.0 (Current)
✅ LLM-based extensive question generation (25+ questions)
✅ Enhanced answer prompts for detailed, exam-oriented responses
✅ Improved answer visibility with markdown rendering
✅ Beautiful UI with confidence indicators and source displays
✅ Increased retrieval coverage (top_k=10, threshold=0.3)
✅ Structured answer format with exam tips
✅ Smooth animations and professional styling
✅ Auto-refreshing status and suggested questions
✅ Multi-format support for sources display

## 🤝 Contributing
Feel free to enhance and customize based on your needs!

## 📄 License
Open source - use as needed for educational purposes

## 🙏 Credits
- Powered by Google Gemini AI
- Built with Flask, LangChain, and FAISS
- Designed for comprehensive exam preparation
