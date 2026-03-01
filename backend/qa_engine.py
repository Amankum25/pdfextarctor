"""
Q&A Engine module for the RAG system.
Handles RAG pipeline, prompt construction, and response formatting with LLM integration.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

import redis
import json
import hashlib
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
        
        # Initialize Redis client for caching
        try:
            self.redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                decode_responses=True,
                socket_timeout=2
            )
            self.redis_client.ping()
            logger.info(f"Connected to Redis cache at {Config.REDIS_HOST}:{Config.REDIS_PORT}")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis cache at {Config.REDIS_HOST}:{Config.REDIS_PORT}. Caching disabled. Error: {e}")
            self.redis_client = None
    
    def is_ready(self) -> bool:
        """
        Check if the QA engine is ready to answer questions.
        
        Returns:
            bool: True if retriever has index and LLM is configured
        """
        return (
            self.retriever.is_index_available() and 
            Config.GROQ_API_KEY and 
            Config.validate_config()
        )
    
    def get_readiness_status(self) -> Dict[str, Any]:
        """
        Get detailed readiness status for debugging.
        
        Returns:
            Dict[str, Any]: Status information
        """
        return {
            'index_available': self.retriever.is_index_available(),
            'api_key_configured': bool(Config.GOOGLE_API_KEY),
            'config_valid': Config.validate_config(),
            'index_stats': self.retriever.get_index_statistics(),
            'ready': self.is_ready()
        }
    
    def _construct_prompt(self, query: str, context: str) -> List[Dict[str, str]]:
        """
        Construct enhanced prompt for Insurance Policy Analysis.
        
        Args:
            query (str): User's question
            context (str): Retrieved document context
            
        Returns:
            List[Dict[str, str]]: Formatted messages for the LLM
        """
        system_message = {
            "role": "system",
            "content": """You are an Expert Insurance Policy Auditor and Consumer Advocate. Your goal is to help customers fully understand their insurance policy, specifically identifying "hidden clauses", exclusions, and financial limits that could negatively impact them.

ROLE & OBJECTIVE:
1. **Demystify Jargon**: Explain complex insurance terms in simple, plain English.
2. **Highlight Risks**: Aggressively look for and highlight VALID risk factors (exclusions, waiting periods, sub-limits).
3. **Be Objective**: Do not sell the policy. Analyze it critically.

ANSWER STRUCTURE (Strictly Follow):
1. **Direct Answer**: Clear, jargon-free answer to the user's question.
2. **Critical Analysis / "Hidden Clauses"**:
   - ⚠️ **Exclusions**: What is explicitly NOT covered related to this topic?
   - ⏳ **Waiting Periods**: Are there time delays before coverage starts?
   - 💰 **Financial Limits**: Are there sub-limits, co-pays, or deductibles?
3. **Key Conditions**: What must the customer do to ensure a successful claim? (e.g., pre-authorization, timeline to report).
4. **Example Scenario**: A brief "Real-world" example of how this applies.

FORMATTING:
- Use **Bold** for critical warnings.
- Use Emoji icons (⚠️, 💰, ⏳, ✅) to make risks visual.
- Create tables for limits/co-pays if data is available.

CONTEXT GUIDELINES:
- Use ONLY the provided document context.
- If a specific clause is not found, state: "I cannot find specific details on [topic] in the available text."
- Always cite the section or page number."""
        }
        
        user_message = {
            "role": "user", 
            "content": f"""analyzing this insurance policy context:
{context}

User Question: {query}

Please decode this for the customer. Reveal any hidden clauses, specific exclusions, or conditions they should be worried about regarding this topic."""
        }
        
        return [system_message, user_message]

    # ... (skipping _format_response as it stays mostly the same logic, just text) ...

    def generate_questions(self, num_questions: int = 5) -> List[str]:
        """
        Generate relevant insurance-analysis questions.
        """
        try:
            # 1. Broad Sampling
            sample_chunks = self.retriever.retrieve_similar_chunks(
                "exclusions limitations waiting period co-payment deductible claim process definitions not covered", 
                top_k=20,
                similarity_threshold=0.2
            )
            
            if not sample_chunks:
                logger.warning("No chunks found for question generation.")
                return []

            context_text = "\n\n".join([chunk['content'] for chunk in sample_chunks])
            
            # 2. Prompting for Insurance Risk Questions
            prompt = f"""Analyze the following insurance policy text and generate critical questions that a smart customer SHOULD ask to uncover hidden risks.
            
            CONTEXT:
            {context_text[:8000]}
            
            INSTRUCTIONS:
            1. Generate {num_questions * 2} questions focusing on:
               - **Exclusions** (What is not covered?)
               - **Financials** (What are the sub-limits, room rent limits, copays?)
               - **Claims** (What risks rejection?)
               - **Waiting Periods** (Pre-existing diseases?)
            2. Return ONLY the questions, one per line.
            
            QUESTIONS:"""

            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            
            # 3. Parsing (Reuse existing logic)
            questions_text = response.content.strip()
            questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
            
            import re
            cleaned_questions = []
            for q in questions:
                clean_q = re.sub(r'^[\d\-\*\.]+\s*', '', q)
                if len(clean_q) > 10:
                    cleaned_questions.append(clean_q)
            
            return cleaned_questions[:num_questions]
            
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return []
    
    def _format_response(
        self, 
        llm_response: str, 
        retrieved_chunks: List[Dict[str, Any]],
        query: str
    ) -> Dict[str, Any]:
        """
        Format the complete response with metadata.
        
        Args:
            llm_response (str): LLM generated response
            retrieved_chunks (List[Dict[str, Any]]): Retrieved document chunks
            query (str): Original user query
            
        Returns:
            Dict[str, Any]: Formatted response with metadata
        """
        # Extract source attributions
        sources = self.retriever.get_source_attribution(retrieved_chunks)
        
        # Calculate confidence based on similarity scores
        if retrieved_chunks:
            avg_similarity = sum(chunk['similarity_score'] for chunk in retrieved_chunks) / len(retrieved_chunks)
            confidence = min(avg_similarity, 1.0)
        else:
            confidence = 0.0
        
        # Handle llm_response properly
        answer_text = llm_response
        
        # 1. Extract content if it's an object
        if hasattr(answer_text, 'content'):
            answer_text = answer_text.content
            
        # 2. Ensure string format
        answer_text = str(answer_text).strip()
        
        # 3. Clean up if it's a stringified list/dict (Gemini sometimes output structured data)
        import ast
        try:
            # Only attempt to parse if it looks like a structure
            if (answer_text.startswith('{') or answer_text.startswith('[')):
                parsed = ast.literal_eval(answer_text)
                
                if isinstance(parsed, dict) and 'text' in parsed:
                     # Case: {'type': 'text', 'text': 'Actual answer'}
                    answer_text = parsed['text']
                elif isinstance(parsed, list):
                    # Case: [{'type': 'text', 'text': 'Part 1'}, ...]
                    parts = []
                    for item in parsed:
                        if isinstance(item, dict) and 'text' in item:
                            parts.append(item['text'])
                        elif isinstance(item, str):
                            parts.append(item)
                    if parts:
                        answer_text = "\n".join(parts)
        except Exception as e:
            # If parsing fails, just use the original text
            logger.warning(f"Failed to parse structured answer, using raw text: {e}")
            pass
            
        # 4. Final safety check - if empty, something is wrong
        if not answer_text:
            logger.error("Answer text is empty after processing!")
            answer_text = "Error: Detailed answer could not be generated. Please try again."
        
        return {
            'answer': answer_text,
            'sources': sources,
            'confidence_score': round(confidence, 3),
            'retrieved_chunks_count': len(retrieved_chunks),
            'query': query,
            'has_answer': not any(phrase in answer_text.lower() for phrase in [
                'cannot find', 'not found', 'not available', 'not provided', 'not mentioned'
            ]),
            'chunk_details': [
                {
                    'source': chunk['source_file'],
                    'page': chunk['page_number'],
                    'similarity': round(chunk['similarity_score'], 3),
                    'content_preview': chunk['content'][:200] + '...' if len(chunk['content']) > 200 else chunk['content']
                }
                for chunk in retrieved_chunks
            ]
        }
    
    def answer_question(
        self, 
        query: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        include_chunk_details: bool = False,
        use_hybrid_search: bool = False
    ) -> Dict[str, Any]:
        """
        Answer a question using the RAG pipeline.
        
        Args:
            query (str): User's question
            top_k (Optional[int]): Number of chunks to retrieve
            similarity_threshold (Optional[float]): Minimum similarity score for retrieval
            include_chunk_details (bool): Whether to include detailed chunk information
            use_hybrid_search (bool): Whether to use hybrid (semantic + keyword) search
            
        Returns:
            Dict[str, Any]: Complete answer with metadata and sources
            
        Raises:
            ValueError: If system is not ready or query is empty
        """
        # Validate inputs
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
        
        # Check Redis Cache
        cache_key = None
        if hasattr(self, 'redis_client') and self.redis_client:
            params_str = f"{query}_{top_k}_{similarity_threshold}_{use_hybrid_search}"
            cache_key = f"QA_CACHE:{hashlib.md5(params_str.encode()).hexdigest()}"
            try:
                cached_res = self.redis_client.get(cache_key)
                if cached_res:
                    logger.info(f"Cache HIT for query: {query[:50]}...")
                    cached_data = json.loads(cached_res)
                    if not include_chunk_details:
                        cached_data.pop('chunk_details', None)
                    return cached_data
            except Exception as e:
                logger.warning(f"Redis cache read error: {str(e)}")
        
        try:
            # Step 1: Retrieve relevant chunks
            if use_hybrid_search:
                retrieved_chunks = self.retriever.search_with_hybrid_approach(query, top_k=top_k)
            else:
                retrieved_chunks = self.retriever.retrieve_similar_chunks(
                    query, 
                    top_k=top_k, 
                    similarity_threshold=similarity_threshold
                )
            
            # Step 2: Handle case with no relevant chunks
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
            
            # Step 3: Construct context for LLM
            context = self.retriever.get_retrieval_context(query, top_k=len(retrieved_chunks))
            
            # Step 4: Generate response using LLM
            messages = self._construct_prompt(query, context)
            
            # Convert to LangChain message format
            langchain_messages = [
                SystemMessage(content=messages[0]["content"]),
                HumanMessage(content=messages[1]["content"])
            ]
            
            llm_response = self.llm.invoke(langchain_messages)
            
            # Step 5: Format and return response
            response = self._format_response(llm_response.content, retrieved_chunks, query)
            
            # Cache the response before altering it
            if hasattr(self, 'redis_client') and self.redis_client and cache_key:
                try:
                    self.redis_client.setex(cache_key, 86400, json.dumps(response)) # Cache for 24 hours
                except Exception as e:
                    logger.warning(f"Redis cache write error: {str(e)}")
            
            # Add chunk details if requested
            if not include_chunk_details:
                response.pop('chunk_details', None)
            
            logger.info(f"Successfully answered query: {query[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            raise ValueError(f"Error processing question: {str(e)}")
    
    def batch_answer_questions(self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        Answer multiple questions in batch.
        
        Args:
            queries (List[str]): List of questions to answer
            
        Returns:
            List[Dict[str, Any]]: List of answers with metadata
        """
        results = []
        
        for i, query in enumerate(queries):
            try:
                result = self.answer_question(query)
                result['batch_index'] = i
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error answering batch query {i}: {str(e)}")
                results.append({
                    'answer': f"Error processing question: {str(e)}",
                    'sources': [],
                    'confidence_score': 0.0,
                    'retrieved_chunks_count': 0,
                    'query': query,
                    'has_answer': False,
                    'batch_index': i,
                    'error': True
                })
        
        return results
    
    def generate_questions(self, num_questions: int = 5) -> List[str]:
        """
        Generate relevant insurance-analysis questions.
        
        Args:
            num_questions (int): Number of questions to generate
            
        Returns:
            List[str]: List of generated questions
        """
        try:
            # 1. Broad Sampling
            sample_chunks = self.retriever.retrieve_similar_chunks(
                "exclusions limitations waiting period co-payment deductible claim process definitions not covered", 
                top_k=20,  # Increased from 8 to 20 to get maximum context coverage
                similarity_threshold=0.2 # Lower threshold to capture peripheral topics
            )
            
            if not sample_chunks:
                logger.warning("No chunks found for question generation.")
                return []

            # Combine content for the prompt
            context_text = "\n\n".join([chunk['content'] for chunk in sample_chunks])
            
            # 2. Prompting for Insurance Questions
            prompt = f"""Analyze the following insurance policy text and generate critical questions that a smart customer SHOULD ask to uncover hidden risks.
            
            CONTEXT:
            {context_text[:8000]}  # Increased context limit
            
            INSTRUCTIONS:
            1. Generate {num_questions * 2} questions focusing on:
               - **Exclusions** (What is not covered?)
               - **Financials** (What are the sub-limits, room rent limits, copays?)
               - **Claims** (What risks rejection?)
               - **Waiting Periods** (Pre-existing diseases?)
            2. Return ONLY the questions, one per line.
            
            QUESTIONS:"""

            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            
            # 3. Parsing
            questions_text = response.content.strip()
            questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
            
            # Clean up (remove bullets or numbers if LLM disobeyed)
            import re
            cleaned_questions = []
            for q in questions:
                clean_q = re.sub(r'^[\d\-\*\.]+\s*', '', q)
                if len(clean_q) > 10: # Filter out garbage
                    cleaned_questions.append(clean_q)
            
            return cleaned_questions[:num_questions]
            
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return []
    
    def explain_answer(self, query: str) -> Dict[str, Any]:
        """
        Provide detailed explanation of how the answer was derived.
        
        Args:
            query (str): User's question
            
        Returns:
            Dict[str, Any]: Detailed explanation with retrieval process
        """
        try:
            # Get the regular answer first
            result = self.answer_question(query, include_chunk_details=True)
            
            # Add explanation details
            explanation = {
                'query_analysis': f"Analyzed query: '{query}'",
                'retrieval_process': f"Retrieved {result['retrieved_chunks_count']} relevant chunks",
                'sources_used': result['sources'],
                'confidence_explanation': self._get_confidence_explanation(result['confidence_score']),
                'chunk_relevance': result.get('chunk_details', []),
                'answer_grounding': 'Answer is based solely on the retrieved document content'
            }
            
            result['explanation'] = explanation
            return result
            
        except Exception as e:
            logger.error(f"Error explaining answer: {str(e)}")
            raise
    
    def _get_confidence_explanation(self, score: float) -> str:
        """
        Provide human-readable explanation of confidence score.
        
        Args:
            score (float): Confidence score between 0 and 1
            
        Returns:
            str: Human-readable confidence explanation
        """
        if score >= 0.8:
            return "High confidence - retrieved chunks are highly relevant to the query"
        elif score >= 0.6:
            return "Medium confidence - retrieved chunks contain relevant information"
        elif score >= 0.4:
            return "Low confidence - retrieved chunks may contain some relevant information"
        else:
            return "Very low confidence - limited relevant information found in documents"
    
    def reload_retriever(self) -> None:
        """Reload the retriever index (useful after adding new documents)."""
        self.retriever.reload_index()
        logger.info("Retriever index reloaded")