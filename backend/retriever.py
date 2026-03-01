"""
Retrieval module for the RAG system.
Handles FAISS similarity search and retrieval logic with metadata filtering.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional

import faiss
import numpy as np
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import Config
from ingest import DocumentIngester

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentRetriever:
    """
    Handles document retrieval using FAISS similarity search.
    """
    
    def __init__(self):
        """Initialize the retriever with embeddings model."""
        self.embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=Config.GOOGLE_API_KEY,
            model=Config.EMBEDDING_MODEL_NAME
        )
        self.ingester = DocumentIngester()
        self.index = None
        self.metadata = []
        self._load_index()
    
    def _load_index(self) -> None:
        """Load the FAISS index and metadata."""
        try:
            self.index, self.metadata = self.ingester.load_index()
            logger.info(f"Loaded retrieval index with {len(self.metadata)} documents")
        except FileNotFoundError:
            logger.warning("No index found. Please ingest documents first.")
            self.index = None
            self.metadata = []
    
    def reload_index(self) -> None:
        """Reload the index (useful after new documents are added)."""
        self._load_index()
    
    def is_index_available(self) -> bool:
        """
        Check if index is available for retrieval.
        
        Returns:
            bool: True if index is loaded and ready
        """
        return self.index is not None and len(self.metadata) > 0
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Convert query text to embedding vector.
        
        Args:
            query (str): User query text
            
        Returns:
            np.ndarray: Query embedding vector
        """
        try:
            query_embedding = self.embeddings.embed_query(query)
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            # Normalize for cosine similarity
            faiss.normalize_L2(query_vector)
            
            return query_vector
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise
    
    def retrieve_similar_chunks(
        self, 
        query: str, 
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        filter_by_source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-k most similar document chunks for a query.
        
        Args:
            query (str): User query
            top_k (Optional[int]): Number of chunks to retrieve (default: Config.TOP_K_RETRIEVAL)
            similarity_threshold (Optional[float]): Minimum similarity score (default: Config.SIMILARITY_THRESHOLD)
            filter_by_source (Optional[str]): Filter results by source file name
            
        Returns:
            List[Dict[str, Any]]: List of retrieved chunks with metadata and scores
            
        Raises:
            ValueError: If no index is available
        """
        if not self.is_index_available():
            raise ValueError(Config.ERROR_MESSAGES["no_index"])
        
        # Use default values if not provided
        top_k = top_k or Config.TOP_K_RETRIEVAL
        similarity_threshold = similarity_threshold or Config.SIMILARITY_THRESHOLD
        
        # Generate query embedding
        query_vector = self.embed_query(query)
        
        # Perform similarity search
        # Search more than top_k to allow for filtering
        search_k = min(top_k * 3, len(self.metadata))
        scores, indices = self.index.search(query_vector, search_k)
        
        # Process results
        results = []
        all_scores = []
        for score, idx in zip(scores[0], indices[0]):
            all_scores.append(score)
            
            # Skip if similarity is too low
            if score < similarity_threshold:
                continue
            
            # Get chunk metadata
            chunk_metadata = self.metadata[idx].copy()
            
            # Apply source filtering if specified
            if filter_by_source and filter_by_source.lower() not in chunk_metadata.get('source_file', '').lower():
                continue
            
            # Create result object - get content from the chunk text, not metadata
            result = {
                'content': chunk_metadata.get('chunk_text', ''),  # Use chunk_text field
                'source_file': chunk_metadata.get('source_file', 'unknown'),
                'page_number': chunk_metadata.get('page_number', None),
                'document_type': chunk_metadata.get('document_type', 'unknown'),
                'similarity_score': float(score),
                'chunk_id': chunk_metadata.get('chunk_id', idx),
                'metadata': chunk_metadata
            }
            results.append(result)
            
            # Stop when we have enough results
            if len(results) >= top_k:
                break
        
        # Debug information
        if all_scores:
            max_score = max(all_scores)
            logger.info(f"Retrieved {len(results)} chunks for query. Max similarity: {max_score:.3f}, Threshold: {similarity_threshold}")
        else:
            logger.warning("No similarity results found")
        
        logger.info(f"Retrieved {len(results)} chunks for query (similarity >= {similarity_threshold})")
        return results
    
    def get_retrieval_context(
        self, 
        query: str, 
        top_k: Optional[int] = None,
        include_metadata: bool = True
    ) -> str:
        """
        Get formatted context string for RAG pipeline.
        
        Args:
            query (str): User query
            top_k (Optional[int]): Number of chunks to retrieve
            include_metadata (bool): Whether to include source information in context
            
        Returns:
            str: Formatted context string ready for LLM
        """
        retrieved_chunks = self.retrieve_similar_chunks(query, top_k)
        
        if not retrieved_chunks:
            return ""
        
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            content = chunk['content']
            
            if include_metadata:
                source_info = f"Source: {chunk['source_file']}"
                if chunk['page_number'] is not None:
                    source_info += f" (Page {chunk['page_number']})"
                
                context_part = f"[Document {i}]\n{source_info}\nContent: {content}\n"
            else:
                context_part = f"[Document {i}]\n{content}\n"
            
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def get_source_attribution(self, retrieved_chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Extract source attribution information from retrieved chunks.
        
        Args:
            retrieved_chunks (List[Dict[str, Any]]): List of retrieved chunks
            
        Returns:
            List[str]: List of source attributions
        """
        # Group pages by source file
        source_map = {}
        for chunk in retrieved_chunks:
            source = chunk['source_file']
            page = chunk['page_number']
            if source not in source_map:
                source_map[source] = set()
            if page is not None:
                source_map[source].add(page)
        
        # Format output
        attributions = []
        for source, pages in source_map.items():
            if pages:
                sorted_pages = sorted(list(pages))
                # Format page list nicely
                page_str = ", ".join(map(str, sorted_pages))
                attributions.append(f"{source} (Pages: {page_str})")
            else:
                attributions.append(source)
                
        return attributions
    
    def search_by_source(self, source_name: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve chunks from a specific source document.
        
        Args:
            source_name (str): Name of the source document
            top_k (int): Maximum number of chunks to return
            
        Returns:
            List[Dict[str, Any]]: List of chunks from the specified source
        """
        if not self.is_index_available():
            raise ValueError(Config.ERROR_MESSAGES["no_index"])
        
        matching_chunks = []
        
        for i, metadata in enumerate(self.metadata):
            source_file = metadata.get('source_file', '')
            
            if source_name.lower() in source_file.lower():
                chunk_data = {
                    'content': metadata.get('content', ''),
                    'source_file': source_file,
                    'page_number': metadata.get('page_number', None),
                    'document_type': metadata.get('document_type', 'unknown'),
                    'chunk_id': metadata.get('chunk_id', i),
                    'metadata': metadata
                }
                matching_chunks.append(chunk_data)
                
                if len(matching_chunks) >= top_k:
                    break
        
        logger.info(f"Found {len(matching_chunks)} chunks from source: {source_name}")
        return matching_chunks
    
    def get_index_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the current index.
        
        Returns:
            Dict[str, Any]: Index statistics
        """
        if not self.is_index_available():
            return {
                'total_chunks': 0,
                'total_sources': 0,
                'index_size': 0,
                'available': False
            }
        
        # Count unique sources
        unique_sources = set()
        document_types = {}
        
        for metadata in self.metadata:
            source_file = metadata.get('source_file', 'unknown')
            doc_type = metadata.get('document_type', 'unknown')
            
            unique_sources.add(source_file)
            document_types[doc_type] = document_types.get(doc_type, 0) + 1
        
        return {
            'total_chunks': len(self.metadata),
            'total_sources': len(unique_sources),
            'source_files': sorted(list(unique_sources)),
            'document_types': document_types,
            'index_size': self.index.ntotal if self.index else 0,
            'available': True
        }
    
    def search_with_hybrid_approach(
        self, 
        query: str, 
        semantic_weight: float = 0.7,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining semantic similarity with keyword matching.
        
        Args:
            query (str): User query
            semantic_weight (float): Weight for semantic search (0-1)
            top_k (Optional[int]): Number of results to return
            
        Returns:
            List[Dict[str, Any]]: Hybrid search results
        """
        top_k = top_k or Config.TOP_K_RETRIEVAL
        
        # Get semantic search results
        semantic_results = self.retrieve_similar_chunks(query, top_k * 2)
        
        # Simple keyword matching boost
        query_keywords = set(query.lower().split())
        
        # Score adjustment based on keyword overlap
        for result in semantic_results:
            content_words = set(result['content'].lower().split())
            keyword_overlap = len(query_keywords.intersection(content_words)) / max(len(query_keywords), 1)
            
            # Combine semantic and keyword scores
            original_score = result['similarity_score']
            keyword_score = keyword_overlap
            
            result['hybrid_score'] = (
                semantic_weight * original_score + 
                (1 - semantic_weight) * keyword_score
            )
        
        # Sort by hybrid score and return top-k
        sorted_results = sorted(semantic_results, key=lambda x: x['hybrid_score'], reverse=True)
        return sorted_results[:top_k]