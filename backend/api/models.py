"""
models.py
Pydantic request and response models for all API endpoints.
These models handle validation, serialization, and OpenAPI doc generation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# ── Ingest Models ─────────────────────────────────────────────────────────────

class IngestRequest(BaseModel):
    """Request body for POST /api/ingest"""
    directory: str = Field(
        default="data/sample_docs",
        description="Path to the directory containing documents to ingest.",
        examples=["data/sample_docs"],
    )
    chunk_size: Optional[int] = Field(
        default=None,
        ge=100,
        le=2000,
        description="Max characters per chunk. Defaults to env setting (500).",
    )
    chunk_overlap: Optional[int] = Field(
        default=None,
        ge=0,
        le=500,
        description="Overlap between chunks. Defaults to env setting (50).",
    )
    clear_existing: bool = Field(
        default=False,
        description="If true, clears the vector store before ingesting.",
    )

    @field_validator("directory")
    @classmethod
    def directory_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Directory path cannot be empty.")
        return v.strip()


class ChunkStats(BaseModel):
    total_chunks: int
    unique_sources: int
    sources: List[str]
    avg_chunk_size: int
    min_chunk_size: int
    max_chunk_size: int


class StoreResult(BaseModel):
    chunks_embedded: int
    total_in_store: int
    sources_ingested: List[str]
    collection: str
    persist_dir: str


class IngestTiming(BaseModel):
    load_seconds: float
    chunk_seconds: float
    embed_seconds: float
    total_seconds: float


class IngestResponse(BaseModel):
    """Response body for POST /api/ingest"""
    status: str
    directory: str
    documents_loaded: int
    timing: IngestTiming
    chunk_stats: ChunkStats
    store: StoreResult


# ── Query Models ──────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    """Request body for POST /api/query"""
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="The natural language question to ask the knowledge base.",
        examples=["How do I reverse a linked list in Python?"],
    )
    top_k: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
        description="Number of document chunks to retrieve. Defaults to env setting (5).",
    )
    model: Optional[str] = Field(
        default=None,
        description="OpenAI model override. E.g. 'gpt-4'. Defaults to env setting.",
        examples=["gpt-3.5-turbo", "gpt-4"],
    )

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Question cannot be blank.")
        return v.strip()


class SourceChunk(BaseModel):
    """A single retrieved document chunk shown as a citation."""
    content: str = Field(description="Preview of the retrieved chunk content.")
    source: str = Field(description="Source filename the chunk came from.")
    chunk_index: int = Field(description="Index of this chunk within its source document.")
    chunk_id: str = Field(description="Unique identifier for the chunk.")
    similarity_score: float = Field(description="Cosine similarity score (0–1).")


class QueryResponse(BaseModel):
    """Response body for POST /api/query"""
    answer: str = Field(description="The AI-generated answer grounded in retrieved context.")
    sources: List[SourceChunk] = Field(description="Retrieved document chunks used to generate the answer.")
    model: str = Field(description="The OpenAI model that generated the answer.")
    tokens_used: int = Field(description="Total tokens consumed (prompt + completion).")
    latency_ms: int = Field(description="End-to-end latency in milliseconds.")


# ── Health / Stats Models ─────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Response body for GET /health"""
    status: str
    service: str
    version: str
    environment: str
    model: str
    timestamp: float


class StatsResponse(BaseModel):
    """Response body for GET /api/stats"""
    collection: str
    total_chunks: int
    persist_dir: str
    error: Optional[str] = None


# ── Error Models ──────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    """Standard error response shape."""
    error: str
    detail: Optional[str] = None
    status_code: int
