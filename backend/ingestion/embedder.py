"""
embedder.py
Converts document chunks into vector embeddings using OpenAI
and persists them in a ChromaDB collection.
"""

import logging
from typing import List

import chromadb
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from config import get_settings

logger = logging.getLogger(__name__)


def get_embedding_function() -> OpenAIEmbeddings:
    """
    Returns a configured OpenAI embeddings instance.
    Uses text-embedding-ada-002 by default (1536 dimensions).
    """
    settings = get_settings()
    return OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        openai_api_key=settings.openai_api_key,
    )


def get_vector_store() -> Chroma:
    """
    Returns (or creates) the ChromaDB vector store.
    Persists embeddings to disk at the configured path.
    """
    settings = get_settings()
    return Chroma(
        collection_name=settings.chroma_collection_name,
        embedding_function=get_embedding_function(),
        persist_directory=settings.chroma_persist_dir,
    )


def embed_and_store(chunks: List[Document]) -> dict:
    """
    Embeds a list of document chunks and upserts them into ChromaDB.

    Each chunk is embedded via OpenAI and stored with its metadata
    (source filename, chunk index, etc.) for retrieval-time citation.

    Args:
        chunks: List of chunked LangChain Document objects.

    Returns:
        Summary dict with counts and collection info.

    Raises:
        ValueError: If chunks list is empty.
        Exception:  Propagates OpenAI / ChromaDB errors with context.
    """
    if not chunks:
        raise ValueError("No chunks provided for embedding.")

    settings = get_settings()
    logger.info(
        f"Embedding {len(chunks)} chunk(s) into ChromaDB "
        f"collection '{settings.chroma_collection_name}'"
    )

    try:
        embeddings = get_embedding_function()

        # Chroma.from_documents handles batching internally
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=settings.chroma_collection_name,
            persist_directory=settings.chroma_persist_dir,
        )

        # Persist to disk
        vector_store.persist()

        # Count documents in the collection
        client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        collection = client.get_collection(settings.chroma_collection_name)
        total_in_store = collection.count()

        unique_sources = list({
            c.metadata.get("source", "unknown") for c in chunks
        })

        logger.info(
            f"✓ Embedded {len(chunks)} chunks. "
            f"Total in store: {total_in_store}"
        )

        return {
            "chunks_embedded": len(chunks),
            "total_in_store": total_in_store,
            "sources_ingested": unique_sources,
            "collection": settings.chroma_collection_name,
            "persist_dir": settings.chroma_persist_dir,
        }

    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise


def clear_collection() -> dict:
    """
    Deletes and recreates the ChromaDB collection.
    Use with caution — this removes ALL stored embeddings.
    """
    settings = get_settings()
    logger.warning(
        f"Clearing ChromaDB collection: {settings.chroma_collection_name}"
    )

    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)

    try:
        client.delete_collection(settings.chroma_collection_name)
        logger.info("Collection deleted.")
    except Exception:
        logger.info("Collection did not exist — nothing to delete.")

    client.create_collection(settings.chroma_collection_name)
    logger.info("Fresh collection created.")

    return {
        "status": "cleared",
        "collection": settings.chroma_collection_name,
    }


def get_collection_stats() -> dict:
    """
    Returns stats about the current ChromaDB collection.
    """
    settings = get_settings()
    try:
        client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        collection = client.get_collection(settings.chroma_collection_name)
        return {
            "collection": settings.chroma_collection_name,
            "total_chunks": collection.count(),
            "persist_dir": settings.chroma_persist_dir,
        }
    except Exception as e:
        return {
            "collection": settings.chroma_collection_name,
            "total_chunks": 0,
            "error": str(e),
        }
