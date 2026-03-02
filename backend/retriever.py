"""
Retrieval module for the RAG system.
Handles FAISS similarity search and retrieval logic with metadata filtering.
"""

import logging
from typing import List, Dict, Any, Optional

import faiss
import numpy as np

from config import Config
from embeddings import get_embedding_provider
from ingest import DocumentIngester

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentRetriever:
    """
    Handles document retrieval using FAISS similarity search.
    """

    def __init__(self):
        """Initialize the retriever with the same embeddings provider as the ingester."""
        self.embedding_provider = get_embedding_provider()
        self.ingester = DocumentIngester()
        self.index = None
        self.metadata: List[Dict] = []
        self._load_index()

    # ------------------------------------------------------------------
    # Index management
    # ------------------------------------------------------------------

    def _load_index(self) -> None:
        """Load/reload the FAISS index and metadata from disk."""
        try:
            self.index, self.metadata = self.ingester.load_index()
            logger.info(
                f"Loaded retrieval index: {len(self.metadata)} chunks, dim={self.index.d}"
            )
        except FileNotFoundError:
            logger.warning("No index found. Please upload documents first.")
            self.index = None
            self.metadata = []

    def reload_index(self) -> None:
        """Reload the index from disk (called after new documents are uploaded)."""
        self._load_index()

    def is_index_available(self) -> bool:
        return self.index is not None and len(self.metadata) > 0

    # ------------------------------------------------------------------
    # Query embedding
    # ------------------------------------------------------------------

    def embed_query(self, query: str) -> np.ndarray:
        """
        Convert query text to a normalised embedding vector.
        """
        try:
            query_embedding = self.embedding_provider.embed_query(query)
            query_vector = np.array([query_embedding], dtype=np.float32)
            faiss.normalize_L2(query_vector)
            return query_vector
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise

    # ------------------------------------------------------------------
    # Similarity search
    # ------------------------------------------------------------------

    def retrieve_similar_chunks(
        self,
        query: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        filter_by_source: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-k most similar document chunks for a query.

        Args:
            query: User query text
            top_k: Number of chunks to return (default: Config.TOP_K_RETRIEVAL)
            similarity_threshold: Minimum cosine similarity (None = Config default).
                                   Pass 0.0 to retrieve everything regardless of score.
            filter_by_source: Optional source file name filter
        """
        if not self.is_index_available():
            raise ValueError(Config.ERROR_MESSAGES["no_index"])

        top_k = top_k or Config.TOP_K_RETRIEVAL
        # Correct None-safe default — 0.0 is a valid explicit threshold
        threshold = Config.SIMILARITY_THRESHOLD if similarity_threshold is None else similarity_threshold

        query_vector = self.embed_query(query)

        # Search wider than top_k to have room for filtering
        search_k = max(top_k * 3, min(50, len(self.metadata)))
        scores, indices = self.index.search(query_vector, search_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue  # FAISS returns -1 for empty slots
            if score < threshold:
                continue

            meta = self.metadata[idx].copy()
            if filter_by_source and filter_by_source.lower() not in meta.get("source_file", "").lower():
                continue

            results.append(
                {
                    "content": meta.get("chunk_text", ""),  # chunk_text is the correct key
                    "source_file": meta.get("source_file", "unknown"),
                    "page_number": meta.get("page_number", None),
                    "document_type": meta.get("document_type", "unknown"),
                    "similarity_score": float(score),
                    "chunk_id": meta.get("chunk_id", idx),
                    "metadata": meta,
                }
            )

            if len(results) >= top_k:
                break

        if scores[0].size > 0:
            logger.info(
                f"Retrieved {len(results)}/{search_k} chunks "
                f"(threshold={threshold:.3f}, max_score={scores[0].max():.3f})"
            )

        return results

    # ------------------------------------------------------------------
    # Context building
    # ------------------------------------------------------------------

    def get_retrieval_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        include_metadata: bool = True,
        chunks: Optional[List[Dict]] = None,
    ) -> str:
        """
        Build a formatted context string for the RAG prompt.
        Pass pre-retrieved `chunks` to avoid a second FAISS query.
        """
        retrieved = chunks if chunks is not None else self.retrieve_similar_chunks(query, top_k)

        if not retrieved:
            return ""

        parts = []
        for i, chunk in enumerate(retrieved, 1):
            content = chunk["content"]
            if include_metadata:
                src = f"Source: {chunk['source_file']}"
                if chunk["page_number"] is not None:
                    src += f" (Page {chunk['page_number']})"
                parts.append(f"[Document {i}]\n{src}\nContent: {content}\n")
            else:
                parts.append(f"[Document {i}]\n{content}\n")

        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Source attribution
    # ------------------------------------------------------------------

    def get_source_attribution(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """Format a list of source attributions from retrieved chunks."""
        source_map: Dict[str, set] = {}
        for chunk in chunks:
            src = chunk["source_file"]
            page = chunk["page_number"]
            source_map.setdefault(src, set())
            if page is not None:
                source_map[src].add(page)

        attributions = []
        for src, pages in source_map.items():
            if pages:
                page_str = ", ".join(map(str, sorted(pages)))
                attributions.append(f"{src} (Pages: {page_str})")
            else:
                attributions.append(src)
        return attributions

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_index_statistics(self) -> Dict[str, Any]:
        """Return statistics about the current index."""
        if not self.is_index_available():
            return {"total_chunks": 0, "total_sources": 0, "index_size": 0, "available": False}

        unique_sources: set = set()
        doc_types: Dict[str, int] = {}
        for m in self.metadata:
            unique_sources.add(m.get("source_file", "unknown"))
            dt = m.get("document_type", "unknown")
            doc_types[dt] = doc_types.get(dt, 0) + 1

        return {
            "total_chunks": len(self.metadata),
            "total_sources": len(unique_sources),
            "source_files": sorted(unique_sources),
            "document_types": doc_types,
            "index_size": self.index.ntotal,
            "available": True,
        }

    # ------------------------------------------------------------------
    # Hybrid search
    # ------------------------------------------------------------------

    def search_with_hybrid_approach(
        self,
        query: str,
        semantic_weight: float = 0.7,
        top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Hybrid semantic + keyword search."""
        top_k = top_k or Config.TOP_K_RETRIEVAL
        semantic_results = self.retrieve_similar_chunks(query, top_k * 2, similarity_threshold=0.0)

        query_keywords = set(query.lower().split())
        for r in semantic_results:
            content_words = set(r["content"].lower().split())
            kw_score = len(query_keywords & content_words) / max(len(query_keywords), 1)
            r["hybrid_score"] = semantic_weight * r["similarity_score"] + (1 - semantic_weight) * kw_score

        return sorted(semantic_results, key=lambda x: x["hybrid_score"], reverse=True)[:top_k]