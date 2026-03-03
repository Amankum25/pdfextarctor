import os
import shutil
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import logging

# Add current directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qa_engine import QAEngine
from ingest import DocumentIngester
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF Extractor API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global QA engine instance
qa_engine: Optional[QAEngine] = None


def get_qa_engine() -> QAEngine:
    global qa_engine
    if qa_engine is None:
        try:
            qa_engine = QAEngine()
        except Exception as e:
            logger.error(f"Failed to initialize QA engine: {e}")
            raise HTTPException(status_code=500, detail="QA Engine initialization failed")
    return qa_engine


class QuestionRequest(BaseModel):
    question: str
    similarity_threshold: Optional[float] = None  # None = use backend default
    top_k: int = 10


class QuestionResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence_score: float
    has_answer: bool


@app.on_event("startup")
async def startup_event():
    """Initialize the QA engine on startup (lazy initialization)."""
    global qa_engine
    logger.info("Server started - QA Engine will initialize on first request")
    # Don't block port binding - initialize lazily on first request via get_qa_engine()
    pass


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    engine = get_qa_engine()
    # Refresh index from disk
    try:
        engine.retriever.reload_index()
    except Exception:
        pass
    ready = engine.is_ready()
    stats = {}
    if ready:
        try:
            stats = engine.retriever.get_index_statistics()
        except Exception:
            pass
    return {"status": "online", "ready": ready, "document_stats": stats}


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about uploaded documents."""
    engine = get_qa_engine()

    # Always reload from disk so newly uploaded PDFs are visible immediately
    try:
        engine.retriever.reload_index()
    except Exception:
        pass

    if not engine.is_ready():
        raise HTTPException(
            status_code=400,
            detail="No documents indexed yet. Please upload a PDF first."
        )

    try:
        result = engine.answer_question(
            request.question,
            similarity_threshold=request.similarity_threshold,
            top_k=request.top_k,
            include_chunk_details=True,
        )
        return QuestionResponse(
            answer=result.get("answer", "No answer generated"),
            sources=result.get("sources", []),
            confidence_score=result.get("confidence_score", 0.0),
            has_answer=result.get("has_answer", False),
        )
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload PDF files for ingestion into the vector store."""
    # Save uploaded files to the backend directory (absolute, reliable path)
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    temp_files = []
    try:
        for file in files:
            # Sanitise filename to avoid path traversal
            safe_name = os.path.basename(file.filename or "upload.pdf")
            file_path = os.path.join(backend_dir, f"temp_{safe_name}")
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            temp_files.append(file_path)

        # Ingest — append to existing index if present, create fresh otherwise
        ingester = DocumentIngester()
        ingester.add_documents_to_existing_index(temp_files)  # handles FileNotFoundError internally

        # Rebuild the global QA engine so it picks up the new index
        global qa_engine
        qa_engine = QAEngine()

        return {
            "message": f"Successfully processed {len(files)} file(s)",
            "files": [f.filename for f in files],
        }

    except Exception as e:
        logger.error(f"Error uploading files: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    finally:
        # Clean up temp files after ingestion is done
        for path in temp_files:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass


@app.get("/suggested-questions")
async def get_suggested_questions():
    """Generate suggested questions from the currently indexed documents."""
    engine = get_qa_engine()

    # Reload in case documents were just uploaded
    try:
        engine.retriever.reload_index()
    except Exception:
        pass

    if not engine.is_ready():
        return {"questions": ["Upload a document to see relevant questions"]}

    try:
        questions = engine.generate_questions(num_questions=8)
        if not questions:
            return {
                "questions": [
                    "What are the main topics covered in this document?",
                    "Can you give me a summary of this document?",
                    "What are the key exclusions mentioned?",
                    "What are the financial limits or sub-limits?",
                    "What is the claims process?",
                ]
            }
        return {"questions": questions}
    except Exception as e:
        logger.error(f"Error getting suggested questions: {e}")
        return {"questions": ["Error generating questions. Please try again."]}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on 0.0.0.0:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
