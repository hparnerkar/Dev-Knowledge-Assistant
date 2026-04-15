"""
ingest.py
POST /api/ingest  — triggers the ingestion pipeline for a given directory.
GET  /api/stats   — returns current vector store statistics.
DELETE /api/ingest — clears the vector store.
"""

import logging

from fastapi import APIRouter, HTTPException, status

from api.models import IngestRequest, IngestResponse, StatsResponse, ErrorResponse
from ingestion.pipeline import run_ingestion_pipeline
from ingestion.embedder import get_collection_stats, clear_collection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post(
    "",
    response_model=IngestResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest documents into the vector store",
    description=(
        "Loads all supported documents (.txt, .md, .pdf) from the specified directory, "
        "chunks them, embeds them via OpenAI, and stores them in ChromaDB. "
        "Returns timing and chunk statistics."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Directory not found or no supported files"},
        500: {"model": ErrorResponse, "description": "Embedding or storage failure"},
    },
)
async def ingest_documents(request: IngestRequest) -> IngestResponse:
    """
    Trigger the full ingestion pipeline:
    load → chunk → embed → store in ChromaDB.
    """
    logger.info(
        f"Ingest request: directory='{request.directory}' "
        f"clear={request.clear_existing}"
    )

    try:
        result = run_ingestion_pipeline(
            directory=request.directory,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            clear_existing=request.clear_existing,
        )
        return IngestResponse(**result)

    except FileNotFoundError as e:
        logger.warning(f"Directory not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ValueError as e:
        logger.warning(f"Ingestion validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}",
        )


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get vector store statistics",
    description="Returns the number of chunks currently stored in ChromaDB.",
)
async def get_stats() -> StatsResponse:
    """Returns current ChromaDB collection stats."""
    stats = get_collection_stats()
    return StatsResponse(**stats)


@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    summary="Clear the vector store",
    description="Deletes all embeddings from ChromaDB. Use with caution — this cannot be undone.",
)
async def clear_store() -> dict:
    """Wipes the ChromaDB collection clean."""
    try:
        result = clear_collection()
        logger.warning("Vector store cleared via API.")
        return result
    except Exception as e:
        logger.error(f"Clear failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear store: {str(e)}",
        )
