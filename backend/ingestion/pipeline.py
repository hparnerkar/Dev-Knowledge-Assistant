"""
pipeline.py
Orchestrates the full ingestion flow:
    load → chunk → embed → store
"""

import logging
import time
from typing import Optional

from ingestion.loader import load_documents
from ingestion.chunker import chunk_documents, get_chunk_stats
from ingestion.embedder import embed_and_store, get_collection_stats

logger = logging.getLogger(__name__)


def run_ingestion_pipeline(
    directory: str,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
    clear_existing: bool = False,
) -> dict:
    """
    Runs the full ingestion pipeline end-to-end.

    Steps:
        1. Load all supported documents from the given directory
        2. Split documents into overlapping chunks
        3. Embed chunks via OpenAI and store in ChromaDB

    Args:
        directory:      Path to folder containing source documents.
        chunk_size:     Optional override for chunk size.
        chunk_overlap:  Optional override for chunk overlap.
        clear_existing: If True, wipe the vector store before ingesting.

    Returns:
        Summary dict with timing, chunk stats, and store stats.
    """
    start = time.time()
    logger.info(f"=== Starting Ingestion Pipeline: {directory} ===")

    # Optionally clear the store first
    if clear_existing:
        from ingestion.embedder import clear_collection
        clear_collection()

    # Step 1: Load
    t1 = time.time()
    documents = load_documents(directory)
    load_time = round(time.time() - t1, 2)

    # Step 2: Chunk
    t2 = time.time()
    chunks = chunk_documents(documents, chunk_size, chunk_overlap)
    chunk_stats = get_chunk_stats(chunks)
    chunk_time = round(time.time() - t2, 2)

    # Step 3: Embed & Store
    t3 = time.time()
    store_result = embed_and_store(chunks)
    embed_time = round(time.time() - t3, 2)

    total_time = round(time.time() - start, 2)

    result = {
        "status": "success",
        "directory": directory,
        "timing": {
            "load_seconds": load_time,
            "chunk_seconds": chunk_time,
            "embed_seconds": embed_time,
            "total_seconds": total_time,
        },
        "documents_loaded": len(documents),
        "chunk_stats": chunk_stats,
        "store": store_result,
    }

    logger.info(f"=== Ingestion Complete in {total_time}s ===")
    return result
