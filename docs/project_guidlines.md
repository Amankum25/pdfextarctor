You are assisting in building a production-quality Retrieval-Augmented Generation (RAG) system.

PROJECT OVERVIEW:
Build a Unified Document Question Answering system that allows users to upload and query multiple
PDF documents and text notes (.txt). The system must perform semantic search across all uploaded
documents and generate answers strictly grounded in the retrieved document content, with clear
source attribution.

CORE FUNCTIONALITY:
- Support ingestion of multiple PDF and TXT documents
- Perform semantic similarity search using vector embeddings
- Generate answers using Retrieval-Augmented Generation (RAG)
- Return answers with source document name and page number (if available)
- Clearly indicate when an answer is not present in the provided documents

CORE REQUIREMENTS:
1. Use Python as the primary programming language.
2. Follow a modular architecture with clear separation of concerns.
3. Do NOT fine-tune or train any models. Use RAG only.
4. Use FAISS as the vector database for storing and searching embeddings.
5. Use LangChain for document loading, chunking, retrieval, and LLM orchestration.
6. Support both PDF and TXT document ingestion.
7. Attach metadata to every document chunk:
   - source file name
   - page number (for PDFs)
   - document type (pdf or notes)
8. Split documents into overlapping chunks to preserve semantic context.
9. On each user query:
   - Convert the query into an embedding
   - Retrieve the top-k most relevant chunks from FAISS
   - Pass ONLY the retrieved chunks to the LLM as context
10. The LLM must:
    - Answer strictly using the provided context
    - Avoid hallucinations and external knowledge
    - Explicitly state when the answer is not available in the documents
11. LLM access via Google Gemini API is required.
12. Internet usage is permitted ONLY for LLM or embedding API calls, not for retrieving knowledge.

ARCHITECTURE:
- ingest.py: document loading, preprocessing, chunking, embedding generation, and FAISS indexing
- retriever.py: FAISS similarity search and retrieval logic
- qa_engine.py: RAG pipeline, prompt construction, and response formatting
- app.py: Streamlit-based user interface for file upload and question answering
- config.py: centralized configuration (chunk size, overlap, model names, top-k values)

CODING GUIDELINES:
- Write clean, readable, and well-documented code.
- Avoid hardcoded values; use configuration variables instead.
- Handle errors gracefully (invalid files, empty documents, missing index).
- Do not mix UI logic with backend logic.
- Keep functions small, modular, and testable.
- Prefer clarity and maintainability over clever or compact code.

NON-GOALS (DO NOT IMPLEMENT):
- No web browsing, search engines, or external data retrieval
- No scraping or fetching online content for answering questions
- No agent frameworks or autonomous tools
- No databases other than FAISS
- No unnecessary abstractions or over-engineering

OUTPUT EXPECTATIONS:
- Provide clear, concise answers grounded in retrieved document content
- Include source document name and page number when applicable
- If insufficient context is available, respond clearly that the answer cannot be found

STYLE AND INTENT:
- Think and code like a backend Software Development Engineer (SDE).
- Prioritize correctness, robustness, and system clarity.
- Avoid tutorial-style shortcuts or demo-only implementations.
- Assume this project will be evaluated in a software engineering interview.
