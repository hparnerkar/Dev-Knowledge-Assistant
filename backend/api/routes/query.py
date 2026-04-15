"""
query.py
POST /api/query — runs the RAG pipeline and returns an AI-generated answer
                  grounded in retrieved document chunks.
"""

import logging

from fastapi import APIRouter, HTTPException, status

from api.models import QueryRequest, QueryResponse, ErrorResponse
from rag.chain import run_rag_chain

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["Query"])


@router.post(
    "",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Query the knowledge base",
    description=(
        "Accepts a natural language question, retrieves the most relevant document "
        "chunks from ChromaDB via semantic search, and returns an AI-generated answer "
        "grounded in that context — along with source citations, token usage, and latency."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Empty vector store or invalid input"},
        500: {"model": ErrorResponse, "description": "LLM or retrieval failure"},
    },
)
async def query_knowledge_base(request: QueryRequest) -> QueryResponse:
    """
    Run the full RAG pipeline:
    question → retrieve chunks → build prompt → call GPT → return answer + sources.
    """
    logger.info(f"Query received: '{request.question[:80]}'")

    try:
        result = run_rag_chain(
            question=request.question,
            top_k=request.top_k,
            model=request.model,
        )
        return QueryResponse(**result)

    except ValueError as e:
        # Typically: vector store is empty
        logger.warning(f"Query validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Query failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}",
        )
