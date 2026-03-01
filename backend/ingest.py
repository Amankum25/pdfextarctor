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
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentIngester:
    """
    Handles document ingestion pipeline: loading -> chunking -> embedding -> indexing.
    """
    
    def __init__(self):
        """Initialize the document ingester with embeddings and text splitter."""
        self.embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=Config.GOOGLE_API_KEY,
            model=Config.EMBEDDING_MODEL_NAME
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self.index = None
        self.documents_metadata = []
    
    def load_document(self, file_path: str) -> List[Document]:
        """
        Load a document from file path.
        
        Args:
            file_path (str): Path to the document file
            
        Returns:
            List[Document]: List of loaded document objects
            
        Raises:
            ValueError: If file format is unsupported or file is too large
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)
        
        # Validate file existence
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Validate file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > Config.MAX_FILE_SIZE_MB:
            raise ValueError(Config.ERROR_MESSAGES["file_too_large"])
        
        # Validate file extension
        if file_path.suffix.lower() not in Config.SUPPORTED_EXTENSIONS:
            raise ValueError(Config.ERROR_MESSAGES["unsupported_format"])
        
        try:
            if file_path.suffix.lower() == '.pdf':
                loader = PyPDFLoader(str(file_path))
            elif file_path.suffix.lower() == '.txt':
                loader = TextLoader(str(file_path), encoding='utf-8')
            else:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")
            
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from {file_path.name}")
            
            return documents
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            raise ValueError(Config.ERROR_MESSAGES["processing_error"])
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into overlapping chunks.
        
        Args:
            documents (List[Document]): List of documents to chunk
            
        Returns:
            List[Document]: List of document chunks with preserved metadata
        """
        all_chunks = []
        
        for doc in documents:
            # Split the document into chunks
            chunks = self.text_splitter.split_documents([doc])
            
            # Enhance metadata for each chunk
            for chunk in chunks:
                # Preserve original metadata and add chunk-specific info
                enhanced_metadata = chunk.metadata.copy()
                enhanced_metadata.update({
                    'chunk_id': len(all_chunks),
                    'source_file': enhanced_metadata.get('source', 'unknown'),
                    'document_type': self._get_document_type(enhanced_metadata.get('source', '')),
                    'page_number': enhanced_metadata.get('page', None),
                    'chunk_length': len(chunk.page_content),
                    'chunk_text': chunk.page_content  # Add the actual content
                })
                chunk.metadata = enhanced_metadata
                all_chunks.append(chunk)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks
    
    def _get_document_type(self, source_path: str) -> str:
        """
        Determine document type from file path.
        
        Args:
            source_path (str): Path to the source file
            
        Returns:
            str: Document type ('pdf' or 'notes')
        """
        if source_path.lower().endswith('.pdf'):
            return 'pdf'
        elif source_path.lower().endswith('.txt'):
            return 'notes'
        else:
            return 'unknown'
    
    def generate_embeddings(self, chunks: List[Document]) -> np.ndarray:
        """
        Generate embeddings for document chunks.
        
        Args:
            chunks (List[Document]): List of document chunks
            
        Returns:
            np.ndarray: Array of embeddings
        """
        texts = [chunk.page_content for chunk in chunks]
        
        try:
            embeddings_list = self.embeddings.embed_documents(texts)
            embeddings_array = np.array(embeddings_list, dtype=np.float32)
            
            logger.info(f"Generated embeddings for {len(chunks)} chunks")
            return embeddings_array
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def create_faiss_index(self, embeddings: np.ndarray) -> faiss.IndexFlatIP:
        """
        Create FAISS index from embeddings.
        
        Args:
            embeddings (np.ndarray): Array of embeddings
            
        Returns:
            faiss.IndexFlatIP: FAISS index for similarity search
        """
        dimension = embeddings.shape[1]
        
        # Use Inner Product index (good for normalized embeddings)
        index = faiss.IndexFlatIP(dimension)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add embeddings to index
        index.add(embeddings)
        
        logger.info(f"Created FAISS index with {index.ntotal} vectors")
        return index
    
    def save_index(self, index: faiss.IndexFlatIP, metadata: List[Dict[str, Any]]) -> None:
        """
        Save FAISS index and metadata to disk.
        
        Args:
            index (faiss.IndexFlatIP): FAISS index to save
            metadata (List[Dict[str, Any]]): Metadata for each document chunk
        """
        try:
            # Save FAISS index
            faiss_path = Config.get_file_path(Config.FAISS_INDEX_FILE)
            faiss.write_index(index, faiss_path)
            
            # Save metadata
            metadata_path = Config.get_file_path(Config.FAISS_METADATA_FILE)
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info(f"Saved index and metadata to {Config.FAISS_INDEX_PATH}")
            
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            raise
    
    def load_index(self) -> Tuple[faiss.IndexFlatIP, List[Dict[str, Any]]]:
        """
        Load FAISS index and metadata from disk.
        
        Returns:
            Tuple[faiss.IndexFlatIP, List[Dict[str, Any]]]: Loaded index and metadata
            
        Raises:
            FileNotFoundError: If index files don't exist
        """
        faiss_path = Config.get_file_path(Config.FAISS_INDEX_FILE)
        metadata_path = Config.get_file_path(Config.FAISS_METADATA_FILE)
        
        if not os.path.exists(faiss_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError(Config.ERROR_MESSAGES["no_index"])
        
        try:
            # Load FAISS index
            index = faiss.read_index(faiss_path)
            
            # Load metadata
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            
            logger.info(f"Loaded index with {index.ntotal} vectors")
            return index, metadata
            
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            raise
    
    def ingest_documents(self, file_paths: List[str]) -> None:
        """
        Full ingestion pipeline: load -> chunk -> embed -> index -> save.
        
        Args:
            file_paths (List[str]): List of file paths to ingest
        """
        all_documents = []
        all_chunks = []
        
        # Load all documents
        for file_path in file_paths:
            try:
                documents = self.load_document(file_path)
                all_documents.extend(documents)
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {str(e)}")
                continue
        
        if not all_documents:
            raise ValueError("No documents were successfully loaded")
        
        # Chunk all documents
        all_chunks = self.chunk_documents(all_documents)
        
        if not all_chunks:
            raise ValueError("No chunks were created from documents")
        
        # Generate embeddings
        embeddings = self.generate_embeddings(all_chunks)
        
        # Create FAISS index
        index = self.create_faiss_index(embeddings)
        
        # Prepare metadata
        metadata = [chunk.metadata for chunk in all_chunks]
        
        # Save index and metadata
        self.save_index(index, metadata)
        
        logger.info(f"Successfully ingested {len(all_documents)} documents into {len(all_chunks)} chunks")
    
    def add_documents_to_existing_index(self, file_paths: List[str]) -> None:
        """
        Add new documents to existing index.
        
        Args:
            file_paths (List[str]): List of file paths to add
        """
        try:
            # Load existing index and metadata
            existing_index, existing_metadata = self.load_index()
            
            # Process new documents
            new_documents = []
            for file_path in file_paths:
                try:
                    documents = self.load_document(file_path)
                    new_documents.extend(documents)
                except Exception as e:
                    logger.error(f"Failed to load {file_path}: {str(e)}")
                    continue
            
            if not new_documents:
                logger.warning("No new documents were successfully loaded")
                return
            
            # Chunk new documents
            new_chunks = self.chunk_documents(new_documents)
            
            # Generate embeddings for new chunks
            new_embeddings = self.generate_embeddings(new_chunks)
            
            # Normalize new embeddings
            faiss.normalize_L2(new_embeddings)
            
            # Add to existing index
            existing_index.add(new_embeddings)
            
            # Combine metadata
            new_metadata = [chunk.metadata for chunk in new_chunks]
            combined_metadata = existing_metadata + new_metadata
            
            # Save updated index
            self.save_index(existing_index, combined_metadata)
            
            logger.info(f"Added {len(new_documents)} documents ({len(new_chunks)} chunks) to existing index")
            
        except FileNotFoundError:
            # No existing index, create new one
            logger.info("No existing index found, creating new index")
            self.ingest_documents(file_paths)