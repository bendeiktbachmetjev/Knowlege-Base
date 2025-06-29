import logging
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from app.knowledge_base.vector_store import load_vector_store

# Configure logger for retrieval operations
logger = logging.getLogger("retrieval")
logger.setLevel(logging.INFO)

class RetrievedChunk(BaseModel):
    text: str
    source: str
    page: Optional[int] = None
    score: Optional[float] = None

class RetrievalResult(BaseModel):
    original_query: str
    translated_query: str
    chunks: List[RetrievedChunk]
    not_found: bool = False

class AdvancedRetriever:
    def __init__(self, k: int = 2):
        self.k = k
        self.vector_store = load_vector_store()

    def translate_query(self, query: str) -> str:
        # Simple normalization, can be extended
        return query.strip().lower()

    def validate_query(self, query: str) -> str:
        if not isinstance(query, str):
            logger.error("Query must be a string.")
            raise ValueError("Query must be a string.")
        if not query.strip():
            logger.error("Query is empty.")
            raise ValueError("Query is empty.")
        if len(query) > 1024:
            logger.error("Query is too long.")
            raise ValueError("Query is too long (max 1024 chars).")
        return query

    def clean_text(self, text: str) -> str:
        # Replace tabs with spaces and collapse multiple spaces
        return ' '.join(text.replace('\t', ' ').split())

    def retrieve(self, query: str, k: Optional[int] = None) -> RetrievalResult:
        try:
            self.validate_query(query)
            translated_query = self.translate_query(query)
            top_k = k if k is not None else self.k
            # FAISS similarity_search returns list of Document
            results = self.vector_store.similarity_search_with_score(translated_query, k=top_k)
            chunks = []
            for doc, score in results:
                source = doc.metadata.get("source", "unknown")
                page = doc.metadata.get("page")
                chunks.append(RetrievedChunk(
                    text=self.clean_text(doc.page_content),
                    source=source,
                    page=page,
                    score=score
                ))
            not_found = len(chunks) == 0
            logger.info(f"Retrieval query: '{query}' | Translated: '{translated_query}' | Results: {len(chunks)}")
            return RetrievalResult(
                original_query=query,
                translated_query=translated_query,
                chunks=chunks,
                not_found=not_found
            )
        except Exception as e:
            logger.error(f"Retrieval error: {e}", exc_info=True)
            return RetrievalResult(
                original_query=query,
                translated_query=query,
                chunks=[],
                not_found=True
            ) 