"""
Q&A Engine module for the RAG system.
Handles RAG pipeline, prompt construction, and response formatting with LLM integration.
"""

import logging
import re
import json
import hashlib
from typing import Dict, Any, List, Optional

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from config import Config
from retriever import DocumentRetriever

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QAEngine:
    """
    Orchestrates the complete RAG pipeline for question answering.
    """

    def __init__(self):
        """Initialize the QA engine with retriever and LLM."""
        self.retriever = DocumentRetriever()

        # Initialize ChatGroq for Llama 3 on Groq
        self.llm = ChatGroq(
            model=Config.LLM_MODEL_NAME,
            temperature=Config.LLM_TEMPERATURE,
            max_tokens=Config.LLM_MAX_TOKENS,
            groq_api_key=Config.GROQ_API_KEY
        )

        logger.info("QA Engine initialized successfully (Groq/Llama 3)")

        # Try Redis; gracefully disable if unavailable
        try:
            import redis
            self.redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                decode_responses=True,
                socket_timeout=2
            )
            self.redis_client.ping()
            logger.info(f"Connected to Redis cache at {Config.REDIS_HOST}:{Config.REDIS_PORT}")
        except Exception as e:
            logger.warning(f"Redis not available. Caching disabled. Error: {e}")
            self.redis_client = None

    # ------------------------------------------------------------------
    # Readiness helpers
    # ------------------------------------------------------------------

    def is_ready(self) -> bool:
        return (
            self.retriever.is_index_available()
            and bool(Config.GROQ_API_KEY)
            and Config.validate_config()
        )

    def get_readiness_status(self) -> Dict[str, Any]:
        return {
            'index_available': self.retriever.is_index_available(),
            'api_key_configured': bool(Config.GROQ_API_KEY) and bool(Config.GOOGLE_API_KEY),
            'config_valid': Config.validate_config(),
            'index_stats': self.retriever.get_index_statistics(),
            'ready': self.is_ready()
        }

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    def _construct_prompt(self, query: str, context: str, is_summary: bool = False) -> List[Dict[str, str]]:
        """
        Build the system + user messages for the LLM.
        Uses a summary-friendly prompt when is_summary=True.
        """
        if is_summary:
            system_content = (
                "You are a professional document analyst. Summarize the provided text into a "
                "clear, structured overview using bullet points and bold headers. "
                "Focus on the purpose, key clauses, exclusions, and financial terms. "
                "Do NOT refuse or say you cannot find information — always synthesize what is given."
            )
            user_content = (
                f"Please provide a comprehensive summary of the following document content.\n\n"
                f"DOCUMENT TEXT:\n{context}\n\nSUMMARY:"
            )
        else:
            system_content = (
                'You are an Expert Insurance Policy Auditor and Consumer Advocate. '
                'Your goal is to help customers fully understand their insurance policy, '
                'specifically identifying hidden clauses, exclusions, and financial limits.\n\n'
                'RULES:\n'
                '1. Answer ONLY from the provided context.\n'
                '2. Use emoji icons (⚠️ 💰 ⏳ ✅) to highlight risks.\n'
                '3. If you cannot find specific details, say exactly: '
                '"I cannot find specific details on [topic] in the available text."\n'
                '4. Always cite the page or section when available.'
            )
            user_content = (
                f"Context from document:\n{context}\n\n"
                f"Customer Question: {query}\n\n"
                f"Answer:"
            )

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]

    # ------------------------------------------------------------------
    # Response formatting
    # ------------------------------------------------------------------

    def _format_response(
        self,
        llm_response: str,
        retrieved_chunks: List[Dict[str, Any]],
        query: str
    ) -> Dict[str, Any]:
        """Format the complete response with metadata."""
        sources = self.retriever.get_source_attribution(retrieved_chunks)

        if retrieved_chunks:
            avg_similarity = sum(c['similarity_score'] for c in retrieved_chunks) / len(retrieved_chunks)
            confidence = min(avg_similarity, 1.0)
        else:
            confidence = 0.0

        # Extract plain string
        answer_text = llm_response
        if hasattr(answer_text, 'content'):
            answer_text = answer_text.content
        answer_text = str(answer_text).strip()

        if not answer_text:
            answer_text = "Error: Answer could not be generated. Please try again."

        has_answer = not any(
            phrase in answer_text.lower()
            for phrase in ['cannot find', 'not found', 'not available', 'not provided', 'not mentioned']
        )

        return {
            'answer': answer_text,
            'sources': sources,
            'confidence_score': round(confidence, 3),
            'retrieved_chunks_count': len(retrieved_chunks),
            'query': query,
            'has_answer': has_answer,
            'chunk_details': [
                {
                    'source': c['source_file'],
                    'page': c['page_number'],
                    'similarity': round(c['similarity_score'], 3),
                    'content_preview': c['content'][:200] + '...' if len(c['content']) > 200 else c['content']
                }
                for c in retrieved_chunks
            ]
        }

    # ------------------------------------------------------------------
    # FAQ question generation
    # ------------------------------------------------------------------

    def generate_questions(self, num_questions: int = 5) -> List[str]:
        """Generate relevant document-analysis questions from the indexed content."""
        try:
            # Deliberately use a very low threshold so we always get chunks
            sample_chunks = self.retriever.retrieve_similar_chunks(
                "key topics main points important sections overview",
                top_k=20,
                similarity_threshold=0.0
            )

            if not sample_chunks:
                logger.warning("No chunks found for question generation.")
                return []

            context_text = "\n\n".join([c['content'] for c in sample_chunks])

            prompt = (
                f"Based on the following document content, generate {num_questions} specific, "
                f"insightful questions a reader should ask to understand the document fully.\n\n"
                f"DOCUMENT CONTENT:\n{context_text[:6000]}\n\n"
                f"Generate ONLY the questions, one per line, without numbering:\nQUESTIONS:"
            )

            response = self.llm.invoke([HumanMessage(content=prompt)])
            lines = response.content.strip().split('\n')

            cleaned = []
            for line in lines:
                q = re.sub(r'^[\d\-\*\.]+\s*', '', line.strip())
                if len(q) > 10:
                    cleaned.append(q)

            return cleaned[:num_questions]

        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return []

    # ------------------------------------------------------------------
    # Main answer_question method
    # ------------------------------------------------------------------

    def answer_question(
        self,
        query: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        include_chunk_details: bool = False,
        use_hybrid_search: bool = False
    ) -> Dict[str, Any]:
        """Answer a question using the RAG pipeline."""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if not self.is_ready():
            status = self.get_readiness_status()
            if not status['index_available']:
                raise ValueError(Config.ERROR_MESSAGES["no_index"])
            elif not status['api_key_configured']:
                raise ValueError(Config.ERROR_MESSAGES["no_api_key"])
            else:
                raise ValueError("QA system is not properly configured")

        query = query.strip()
        top_k = top_k or Config.TOP_K_RETRIEVAL

        # Detect summary request
        is_summary = any(kw in query.lower() for kw in ["summary", "summarize", "overview", "brief", "describe"])

        # For summaries: force threshold to 0.0; for others use passed or default
        if is_summary:
            actual_threshold = 0.0
            search_query = "introduction overview purpose main topics key points"
            actual_top_k = max(top_k, 15)  # Grab more chunks for a rich summary
        else:
            # None means use default; 0.0 means retrieve everything as-is
            actual_threshold = similarity_threshold  # None is handled correctly in retriever
            search_query = query
            actual_top_k = top_k

        try:
            if use_hybrid_search:
                retrieved_chunks = self.retriever.search_with_hybrid_approach(search_query, top_k=actual_top_k)
            else:
                retrieved_chunks = self.retriever.retrieve_similar_chunks(
                    search_query,
                    top_k=actual_top_k,
                    similarity_threshold=actual_threshold
                )

            if not retrieved_chunks:
                return {
                    'answer': Config.ERROR_MESSAGES["no_results"],
                    'sources': [],
                    'confidence_score': 0.0,
                    'retrieved_chunks_count': 0,
                    'query': query,
                    'has_answer': False,
                    'chunk_details': []
                }

            context = self.retriever.get_retrieval_context(
                query, top_k=len(retrieved_chunks), chunks=retrieved_chunks
            )

            messages = self._construct_prompt(query, context, is_summary=is_summary)

            langchain_messages = [
                SystemMessage(content=messages[0]["content"]),
                HumanMessage(content=messages[1]["content"])
            ]

            llm_response = self.llm.invoke(langchain_messages)

            response = self._format_response(llm_response.content, retrieved_chunks, query)

            if not include_chunk_details:
                response.pop('chunk_details', None)

            logger.info(f"Successfully answered query: {query[:60]}...")
            return response

        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise ValueError(f"Error processing question: {e}")

    # ------------------------------------------------------------------
    # Explain answer (debug)
    # ------------------------------------------------------------------

    def explain_answer(self, query: str) -> Dict[str, Any]:
        """Explain the source of an answer (debugging aid)."""
        try:
            result = self.answer_question(query, include_chunk_details=True)
            result['explanation'] = {
                'query_analysis': f"Analyzed query: '{query}'",
                'retrieval_process': f"Retrieved {result['retrieved_chunks_count']} relevant chunks",
                'sources_used': result['sources'],
                'chunk_relevance': result.get('chunk_details', []),
            }
            return result
        except Exception as e:
            logger.error(f"Error explaining answer: {e}")
            raise

    def reload_retriever(self) -> None:
        """Reload the retriever index (useful after adding new documents)."""
        self.retriever.reload_index()
        logger.info("Retriever index reloaded")