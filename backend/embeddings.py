"""
Unified embedding interface supporting multiple providers.
Supports: Local (sentence-transformers), Google Gemini
"""

import logging
from typing import List, Union
import numpy as np

from config import Config

logger = logging.getLogger(__name__)


class EmbeddingProvider:
    """
    Unified embedding interface that abstracts different embedding providers.
    Automatically selects the provider based on Config.EMBEDDING_PROVIDER.
    """
    
    def __init__(self):
        """Initialize the embedding provider based on configuration."""
        self.provider = Config.EMBEDDING_PROVIDER.lower()
        self.model = None
        
        if self.provider == "local":
            self._init_local_embeddings()
        elif self.provider == "google":
            self._init_google_embeddings()
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")
        
        logger.info(f"Initialized {self.provider} embeddings")
    
    def _init_local_embeddings(self):
        """Initialize local sentence-transformers model."""
        try:
            from sentence_transformers import SentenceTransformer
            
            model_name = Config.LOCAL_EMBEDDING_MODEL
            logger.info(f"Loading local embedding model: {model_name}")
            
            # Download and cache the model
            self.model = SentenceTransformer(model_name)
            
            logger.info(f"Local model loaded successfully. Dimension: {self.model.get_sentence_embedding_dimension()}")
            
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install it with: pip install sentence-transformers"
            )
        except Exception as e:
            logger.error(f"Failed to load local embedding model: {e}")
            raise
    
    def _init_google_embeddings(self):
        """Initialize Google Gemini embeddings."""
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            
            if not Config.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY not set in environment variables")
            
            self.model = GoogleGenerativeAIEmbeddings(
                model=Config.GOOGLE_EMBEDDING_MODEL,
                google_api_key=Config.GOOGLE_API_KEY
            )
            
            logger.info(f"Google embeddings initialized: {Config.GOOGLE_EMBEDDING_MODEL}")
            
        except ImportError:
            raise ImportError(
                "langchain-google-genai not installed. "
                "Install it with: pip install langchain-google-genai google-genai"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Google embeddings: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        try:
            if self.provider == "local":
                # sentence-transformers returns numpy arrays
                embeddings = self.model.encode(
                    texts,
                    batch_size=32,
                    show_progress_bar=len(texts) > 100,
                    convert_to_numpy=True
                )
                return embeddings.tolist()
            
            elif self.provider == "google":
                # LangChain Google embeddings
                return self.model.embed_documents(texts)
            
        except Exception as e:
            logger.error(f"Error generating document embeddings: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        try:
            if self.provider == "local":
                # sentence-transformers
                embedding = self.model.encode(
                    text,
                    convert_to_numpy=True
                )
                return embedding.tolist()
            
            elif self.provider == "google":
                # LangChain Google embeddings
                return self.model.embed_query(text)
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        if self.provider == "local":
            return self.model.get_sentence_embedding_dimension()
        elif self.provider == "google":
            return Config.GOOGLE_EMBEDDING_DIMENSION
        return 768  # default fallback


# Global singleton instance
_embedding_provider: Union[EmbeddingProvider, None] = None


def get_embedding_provider() -> EmbeddingProvider:
    """
    Get or create the global embedding provider instance.
    This ensures we only load the model once.
    """
    global _embedding_provider
    
    if _embedding_provider is None:
        _embedding_provider = EmbeddingProvider()
    
    return _embedding_provider


def reset_embedding_provider():
    """Reset the global embedding provider (useful for testing or config changes)."""
    global _embedding_provider
    _embedding_provider = None
