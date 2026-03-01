"""
Configuration file for the RAG Document Q&A System.
Contains all configurable parameters to avoid hardcoded values throughout the codebase.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Centralized configuration class for the RAG system.
    All configuration parameters are defined here to ensure maintainability.
    """
    
    # Document Processing Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Embedding Configuration
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"  # Open Source HF model
    EMBEDDING_DIMENSION: int = 384  # Dimension for all-MiniLM-L6-v2
    
    # LLM Configuration (Switched to Groq)
    LLM_MODEL_NAME: str = "llama-3.3-70b-versatile"  # Groq Llama 3 model
    LLM_TEMPERATURE: float = 0.2  
    LLM_MAX_TOKENS: int = 4096 
    
    # Retrieval Configuration
    TOP_K_RETRIEVAL: int = 10  
    SIMILARITY_THRESHOLD: float = 0.3  
    
    # File Processing Configuration
    SUPPORTED_EXTENSIONS: tuple = ('.pdf', '.txt')
    MAX_FILE_SIZE_MB: int = 50
    
    # FAISS Configuration
    # Use absolute paths to ensure files are found regardless of execution directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FAISS_INDEX_PATH: str = os.path.join(BASE_DIR, "faiss_index")
    FAISS_INDEX_FILE: str = "document_index.faiss"
    FAISS_METADATA_FILE: str = "document_metadata.pkl"
    
    # API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY") or ""
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # Streamlit Configuration (Legacy but can influence default metadata)
    PAGE_TITLE: str = "Insurance Policy Analyzer"
    PAGE_ICON: str = "🛡️"
    LAYOUT: str = "wide"
    
    # Error Messages
    ERROR_MESSAGES: Dict[str, str] = {
        "no_api_key": "Google API key not found. Please set GOOGLE_API_KEY environment variable.",
        "no_index": "No document index found. Please upload documents first.",
        "no_results": "I couldn't find relevant information in the uploaded documents to answer your question.",
        "file_too_large": f"File size exceeds {MAX_FILE_SIZE_MB}MB limit.",
        "unsupported_format": f"Unsupported file format. Supported formats: {SUPPORTED_EXTENSIONS}",
        "processing_error": "Error processing document. Please check the file format and try again."
    }
    
    # RAG Prompt Template
    RAG_PROMPT_TEMPLATE: str = """
You are a helpful assistant that answers questions based strictly on the provided document context.

IMPORTANT INSTRUCTIONS:
1. Answer ONLY using information from the provided context
2. Do NOT use external knowledge or make assumptions
3. If the answer is not in the context, clearly state "I cannot find this information in the provided documents"
4. Always cite the source document name and page number when available
5. Be concise and factual

Context from documents:
{context}

Question: {question}

Answer:
"""

    @classmethod
    def validate_config(cls) -> bool:
        """
        Validate that all required configuration is properly set.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not cls.GROQ_API_KEY:
             return False
        
        if cls.CHUNK_SIZE <= 0 or cls.CHUNK_OVERLAP < 0:
            return False
            
        if cls.CHUNK_OVERLAP >= cls.CHUNK_SIZE:
            return False
            
        return True

    @classmethod
    def get_file_path(cls, filename: str) -> str:
        """
        Get full path for FAISS index files.
        
        Args:
            filename (str): Name of the file
            
        Returns:
            str: Full file path
        """
        os.makedirs(cls.FAISS_INDEX_PATH, exist_ok=True)
        return os.path.join(cls.FAISS_INDEX_PATH, filename)