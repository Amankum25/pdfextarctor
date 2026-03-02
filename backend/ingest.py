"""
Document ingestion module for the RAG system.
Handles loading, preprocessing, chunking, embedding generation, and FAISS indexing.
"""

import os
import pickle
import logging
from typing import List, Dict, Any, Tuple
from pathlib import Path

import faiss
import numpy as np
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config import Config
from embeddings import get_embedding_provider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_CACHED_PDFS = 5  # Rolling cache size


class DocumentIngester:
    """
    Handles document ingestion pipeline: loading -> chunking -> embedding -> indexing.
    """

    def __init__(self):
        """Initialize the document ingester with embeddings and text splitter."""
        # Use the unified embedding provider
        self.embedding_provider = get_embedding_provider()

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""],
        )

    # ------------------------------------------------------------------
    # Document loading
    # ------------------------------------------------------------------

    def load_document(self, file_path: str) -> List[Document]:
        """Load a document from file path."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > Config.MAX_FILE_SIZE_MB:
            raise ValueError(Config.ERROR_MESSAGES["file_too_large"])

        if file_path.suffix.lower() not in Config.SUPPORTED_EXTENSIONS:
            raise ValueError(Config.ERROR_MESSAGES["unsupported_format"])

        try:
            if file_path.suffix.lower() == ".pdf":
                loader = PyPDFLoader(str(file_path))
            elif file_path.suffix.lower() == ".txt":
                loader = TextLoader(str(file_path), encoding="utf-8")
            else:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")

            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from {file_path.name}")
            return documents

        except Exception as e:
            logger.error(f"Error loading document {file_path}: {e}")
            raise ValueError(Config.ERROR_MESSAGES["processing_error"])

    # ------------------------------------------------------------------
    # Chunking
    # ------------------------------------------------------------------

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into overlapping chunks with enriched metadata."""
        all_chunks = []

        for doc in documents:
            chunks = self.text_splitter.split_documents([doc])

            for chunk in chunks:
                meta = chunk.metadata.copy()
                meta.update(
                    {
                        "chunk_id": len(all_chunks),
                        "source_file": meta.get("source", "unknown"),
                        "document_type": self._get_document_type(meta.get("source", "")),
                        "page_number": meta.get("page", None),
                        "chunk_length": len(chunk.page_content),
                        "chunk_text": chunk.page_content,
                    }
                )
                chunk.metadata = meta
                all_chunks.append(chunk)

        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks

    def _get_document_type(self, source_path: str) -> str:
        if source_path.lower().endswith(".pdf"):
            return "pdf"
        elif source_path.lower().endswith(".txt"):
            return "notes"
        return "unknown"

    # ------------------------------------------------------------------
    # Embeddings and FAISS
    # ------------------------------------------------------------------

    def generate_embeddings(self, chunks: List[Document]) -> np.ndarray:
        """
        Generate normalised embeddings for document chunks.
        """
        texts = [chunk.page_content for chunk in chunks]
        try:
            embeddings_list = self.embedding_provider.embed_documents(texts)
            arr = np.array(embeddings_list, dtype=np.float32)
            faiss.normalize_L2(arr)
            logger.info(f"Generated embeddings for {len(chunks)} chunks, shape={arr.shape}")
            return arr
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    def create_faiss_index(self, embeddings: np.ndarray) -> faiss.IndexFlatIP:
        """
        Create a FAISS inner-product index from already-normalised embeddings.
        BGE vectors are pre-normalised, so inner-product == cosine similarity.
        """
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)
        logger.info(f"Created FAISS index with {index.ntotal} vectors (dim={dimension})")
        return index

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_index(self, index: faiss.IndexFlatIP, metadata: List[Dict[str, Any]]) -> None:
        """Save FAISS index and metadata to disk."""
        try:
            faiss_path = Config.get_file_path(Config.FAISS_INDEX_FILE)
            faiss.write_index(index, faiss_path)
            metadata_path = Config.get_file_path(Config.FAISS_METADATA_FILE)
            with open(metadata_path, "wb") as f:
                pickle.dump(metadata, f)
            logger.info(f"Saved index ({index.ntotal} vectors) to {Config.FAISS_INDEX_PATH}")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            raise

    def load_index(self) -> Tuple[faiss.IndexFlatIP, List[Dict[str, Any]]]:
        """Load FAISS index and metadata from disk."""
        faiss_path = Config.get_file_path(Config.FAISS_INDEX_FILE)
        metadata_path = Config.get_file_path(Config.FAISS_METADATA_FILE)

        if not os.path.exists(faiss_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError(Config.ERROR_MESSAGES["no_index"])

        try:
            index = faiss.read_index(faiss_path)
            with open(metadata_path, "rb") as f:
                metadata = pickle.load(f)
            logger.info(f"Loaded index with {index.ntotal} vectors (dim={index.d})")
            return index, metadata
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            raise

    # ------------------------------------------------------------------
    # Ingestion pipelines
    # ------------------------------------------------------------------

    def ingest_documents(self, file_paths: List[str]) -> None:
        """
        Full fresh ingestion: overwrite the existing index with new documents.
        """
        all_documents = []
        for file_path in file_paths:
            try:
                all_documents.extend(self.load_document(file_path))
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")

        if not all_documents:
            raise ValueError("No documents were successfully loaded")

        all_chunks = self.chunk_documents(all_documents)
        if not all_chunks:
            raise ValueError("No chunks were created from documents")

        embeddings = self.generate_embeddings(all_chunks)
        index = self.create_faiss_index(embeddings)
        metadata = [chunk.metadata for chunk in all_chunks]
        self.save_index(index, metadata)

        logger.info(
            f"Ingested {len(all_documents)} documents → {len(all_chunks)} chunks"
        )

    def add_documents_to_existing_index(self, file_paths: List[str]) -> None:
        """
        Append new documents to the existing FAISS index (rolling 5-PDF cache).
        Falls back to fresh ingestion if no index exists yet.
        """
        try:
            existing_index, existing_metadata = self.load_index()
        except FileNotFoundError:
            logger.info("No existing index found — creating fresh index")
            self.ingest_documents(file_paths)
            return

        # Load and chunk new documents
        new_documents = []
        for file_path in file_paths:
            try:
                new_documents.extend(self.load_document(file_path))
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")

        if not new_documents:
            logger.warning("No new documents loaded — index unchanged")
            return

        new_chunks = self.chunk_documents(new_documents)
        new_metadata = [chunk.metadata for chunk in new_chunks]

        # Build combined metadata list
        combined_metadata = existing_metadata + new_metadata

        # Identify unique source files in arrival order (oldest → newest)
        unique_files: List[str] = []
        for m in combined_metadata:
            src = m.get("source", "unknown")
            if src not in unique_files:
                unique_files.append(src)

        if len(unique_files) > MAX_CACHED_PDFS:
            # Keep only the most-recent MAX_CACHED_PDFS sources
            files_to_keep = set(unique_files[-MAX_CACHED_PDFS:])
            logger.info(f"Cache limit hit — keeping {MAX_CACHED_PDFS} most recent: {files_to_keep}")

            # Filter metadata to retained sources only
            kept_metadata = [m for m in combined_metadata if m.get("source", "unknown") in files_to_keep]

            # We can only rebuild if source files are accessible on disk
            sources_on_disk = [f for f in files_to_keep if os.path.exists(f)]
            if sources_on_disk:
                logger.info("Rebuilding index from cached files on disk")
                self.ingest_documents(sources_on_disk)
            else:
                # Source files are gone (temp files cleaned up); build from kept metadata
                # Re-embed the kept chunks using stored chunk_text
                logger.warning("Source files not on disk — re-embedding from stored text chunks")
                texts = [m.get("chunk_text", "") for m in kept_metadata]
                embedding_list = self.embeddings.embed_documents(texts)
                kept_embeddings = np.array(embedding_list, dtype=np.float32)
                new_index = faiss.IndexFlatIP(kept_embeddings.shape[1])
                new_index.add(kept_embeddings)
                self.save_index(new_index, kept_metadata)
            return

        # Under the cache limit: append new vectors to existing index
        new_embeddings = self.generate_embeddings(new_chunks)
        # BGE already normalises, so just add directly
        existing_index.add(new_embeddings)
        self.save_index(existing_index, combined_metadata)

        logger.info(
            f"Appended {len(new_chunks)} chunks — index now has "
            f"{existing_index.ntotal} vectors from {len(unique_files)} source(s)"
        )