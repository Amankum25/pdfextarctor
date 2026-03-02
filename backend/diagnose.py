"""
Diagnostic script to check FAISS index scores and retriever behavior.
Run from the root project directory: python backend/diagnose.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from config import Config
from ingest import DocumentIngester

def main():
    ingester = DocumentIngester()
    
    print("=== Loading FAISS index ===")
    try:
        index, metadata = ingester.load_index()
        print(f"Index total vectors: {index.ntotal}")
        print(f"Metadata entries: {len(metadata)}")
        print(f"Index dimension: {index.d}")
        print()
    except Exception as e:
        print(f"FAILED to load index: {e}")
        return

    print("=== Sample metadata (first 3 entries) ===")
    for i, m in enumerate(metadata[:3]):
        print(f"  [{i}] source_file={m.get('source_file','?')} page={m.get('page_number','?')} chunk_len={m.get('chunk_length','?')}")
        snippet = m.get('chunk_text','')[:100]
        print(f"       text preview: {snippet!r}")
    print()

    print("=== Generating test query embedding ===")
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    import numpy as np
    import faiss

    embeddings = GoogleGenerativeAIEmbeddings(
        model=Config.EMBEDDING_MODEL_NAME,
        google_api_key=Config.GOOGLE_API_KEY
    )

    query = "Give me a summary of this document"
    vec = embeddings.embed_query(query)
    query_vector = np.array([vec], dtype=np.float32)
    faiss.normalize_L2(query_vector)
    
    search_k = min(5, index.ntotal)
    scores, indices = index.search(query_vector, search_k)
    print(f"Top {search_k} FAISS scores: {scores[0].tolist()}")
    print(f"Top {search_k} FAISS indices: {indices[0].tolist()}")
    print()

    print("=== Checking if threshold=0.0 would return results ===")
    count_above_0 = sum(1 for s in scores[0] if s >= 0.0)
    count_above_03 = sum(1 for s in scores[0] if s >= 0.3)
    print(f"  Results with threshold >= 0.0:  {count_above_0}")
    print(f"  Results with threshold >= 0.3:  {count_above_03}")

if __name__ == "__main__":
    main()
