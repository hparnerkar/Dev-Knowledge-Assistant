"""
retriever.py
Handles semantic similarity search against the ChromaDB vector store.
Returns the top-K most relevant document chunks for a given query.
"""

import logging
from typing import List, Optional

from langchain.schema import Document
from langchain_community.vectorstores import Chroma

from config import get_settings
from ingestion.embedder import get_embedding_function, get_collection_stats

logger = logging.getLogger(__name__)


def get_retriever(top_k: Optional[int] = None):
    """
    Returns a LangChain retriever backed by ChromaDB.

    Args:
        top_k: Number of chunks to retrieve per query.
               Defaults to settings.top_k_results.

    Returns:
        A LangChain VectorStoreRetriever instance.
    """
    settings = get_settings()
    k = top_k or settings.top_k_results

    vector_store = Chroma(
        collection_name=settings.chroma_collection_name,
        embedding_function=get_embedding_function(),
        persist_directory=settings.chroma_persist_dir,
    )

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )


def retrieve_chunks(
    query: str,
    top_k: Optional[int] = None,
) -> List[Document]:
    """
    Performs a semantic similarity search for the given query.

    Args:
        query:  The user's natural language question.
        top_k:  Number of chunks to retrieve.

    Returns:
        List of the most relevant Document chunks, sorted by relevance.

    Raises:
        ValueError: If the vector store is empty.
    """
    settings = get_settings()
    k = top_k or settings.top_k_results

    # Guard: ensure the store has documents
    stats = get_collection_stats()
    total = stats.get("total_chunks", 0)
    if total == 0:
        raise ValueError(
            "Vector store is empty. Please run the ingestion pipeline first "
            "via POST /api/ingest before querying."
        )

    logger.info(f"Retrieving top-{k} chunks for query: '{query[:80]}...'")

    vector_store = Chroma(
        collection_name=settings.chroma_collection_name,
        embedding_function=get_embedding_function(),
        persist_directory=settings.chroma_persist_dir,
    )

    results = vector_store.similarity_search(query, k=k)

    logger.info(f"Retrieved {len(results)} chunk(s) from {total} total in store")
    for i, doc in enumerate(results):
        src = doc.metadata.get("source", "unknown")
        chunk_idx = doc.metadata.get("chunk_index", "?")
        logger.debug(f"  [{i+1}] {src} chunk {chunk_idx} — {len(doc.page_content)} chars")

    return results


def retrieve_with_scores(
    query: str,
    top_k: Optional[int] = None,
) -> List[tuple[Document, float]]:
    """
    Same as retrieve_chunks but also returns similarity scores.
    Scores are cosine similarity values between 0 and 1 (higher = more relevant).

    Returns:
        List of (Document, score) tuples sorted by descending score.
    """
    settings = get_settings()
    k = top_k or settings.top_k_results

    vector_store = Chroma(
        collection_name=settings.chroma_collection_name,
        embedding_function=get_embedding_function(),
        persist_directory=settings.chroma_persist_dir,
    )

    results = vector_store.similarity_search_with_score(query, k=k)
    results.sort(key=lambda x: x[1], reverse=True)

    logger.info(
        f"Top scores: {[round(score, 3) for _, score in results]}"
    )
    return results
