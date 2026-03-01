import os
import shutil
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys

# Add current directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qa_engine import QAEngine
from ingest import DocumentIngester
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF Extractor API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the URL of the React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
qa_engine = None

def get_qa_engine():
    global qa_engine
    if qa_engine is None:
        try:
            qa_engine = QAEngine()
        except Exception as e:
            logger.error(f"Failed to initialize QA engine: {e}")
            raise HTTPException(status_code=500, detail="QA Engine not available")
    return qa_engine

class QuestionRequest(BaseModel):
    question: str
    similarity_threshold: float = 0.3
    top_k: int = 10

class QuestionResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence_score: float
    has_answer: bool

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    try:
        global qa_engine
        qa_engine = QAEngine()
        logger.info("QA Engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize QA engine during startup: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    engine = get_qa_engine()
    ready = engine.is_ready()
    
    stats = {}
    if ready:
        try:
            stats = engine.retriever.get_index_statistics()
        except:
            pass
            
    return {
        "status": "online",
        "ready": ready,
        "document_stats": stats
    }

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about uploaded documents"""
    engine = get_qa_engine()
    
    if not engine.is_ready():
        raise HTTPException(status_code=400, detail="System not ready. Please upload documents first.")
    
    try:
        result = engine.answer_question(
            request.question,
            similarity_threshold=request.similarity_threshold,
            top_k=request.top_k,
            include_chunk_details=True
        )
        
        return QuestionResponse(
            answer=result.get('answer', 'No answer generated'),
            sources=result.get('sources', []),
            confidence_score=result.get('confidence_score', 0.0),
            has_answer=result.get('has_answer', False)
        )
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload PDF files for ingestion"""
    temp_files = []
    try:
        for file in files:
            file_path = f"temp_{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            temp_files.append(file_path)
        
        # Ingest documents
        ingester = DocumentIngester()
        ingester.ingest_documents(temp_files)
        
        # Reload QA engine
        global qa_engine
        qa_engine = QAEngine()
        
        return {"message": f"Successfully processed {len(files)} files", "files": [f.filename for f in files]}
        
    except Exception as e:
        logger.error(f"Error uploading files: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    finally:
        # Cleanup
        for path in temp_files:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except:
                pass

@app.get("/suggested-questions")
async def get_suggested_questions():
    """Get suggested questions based on content"""

    engine = get_qa_engine()
    if not engine.is_ready():
         return {"questions": ["Upload a document to see relevant questions"]}
         
    try:
        # Generate dynamic questions from the uploaded content
        questions = engine.generate_questions(num_questions=15)
        
        if not questions:
            # Fallback if generation fails or returns empty
            return {"questions": [
                "What are the main topics covered?",
                "Summarize the key concepts.",
                "What are the important definitions?",
                "How does this relate to real-world applications?",
                "What are the critical success factors?"
            ]}
            
        return {"questions": questions}
        
    except Exception as e:
        logger.error(f"Error getting suggested questions: {e}")
        return {"questions": ["Error generating questions. Please try again."]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
