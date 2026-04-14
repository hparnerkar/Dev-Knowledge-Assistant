"""
chunker.py
Splits LangChain Documents into smaller overlapping chunks
suitable for embedding and retrieval.
"""

import logging
from typing import List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from config import get_settings

logger = logging.getLogger(__name__)


def chunk_documents(
    documents: List[Document],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> List[Document]:
    """
    Splits a list of Documents into overlapping chunks.

    Uses RecursiveCharacterTextSplitter which tries to split on
    natural boundaries: paragraphs → sentences → words → characters.

    Args:
        documents:     List of LangChain Document objects to split.
        chunk_size:    Max tokens per chunk (defaults to settings value).
        chunk_overlap: Overlap between chunks (defaults to settings value).

    Returns:
        List of chunked Document objects, each with enriched metadata
        including chunk index and total chunk count per source.
    """
    settings = get_settings()
    _chunk_size = chunk_size or settings.chunk_size
    _chunk_overlap = chunk_overlap or settings.chunk_overlap

    logger.info(
        f"Chunking {len(documents)} document(s) "
        f"[size={_chunk_size}, overlap={_chunk_overlap}]"
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=_chunk_size,
        chunk_overlap=_chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],  # natural split order
    )

    all_chunks: List[Document] = []

    for doc in documents:
        source = doc.metadata.get("source", "unknown")
        raw_chunks = splitter.split_documents([doc])

        # Tag each chunk with its index for traceability
        for i, chunk in enumerate(raw_chunks):
            chunk.metadata.update({
                "chunk_index": i,
                "chunk_total": len(raw_chunks),
                "chunk_id": f"{source}::chunk_{i}",
            })
            all_chunks.append(chunk)

        logger.info(f"  {source} → {len(raw_chunks)} chunk(s)")

    logger.info(f"Total chunks produced: {len(all_chunks)}")
    return all_chunks


def get_chunk_stats(chunks: List[Document]) -> dict:
    """
    Returns summary statistics for a list of chunks.
    Useful for debugging ingestion quality.
    """
    if not chunks:
        return {}

    sizes = [len(c.page_content) for c in chunks]
    sources = set(c.metadata.get("source", "unknown") for c in chunks)

    return {
        "total_chunks": len(chunks),
        "unique_sources": len(sources),
        "sources": list(sources),
        "avg_chunk_size": round(sum(sizes) / len(sizes)),
        "min_chunk_size": min(sizes),
        "max_chunk_size": max(sizes),
    }
