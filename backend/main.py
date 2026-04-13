"""
main.py
FastAPI application entry point for the Dev Knowledge Assistant.
Registers routers, CORS middleware, and startup/shutdown lifecycle events.
"""

import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


# ── Lifespan (startup / shutdown) ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Dev Knowledge Assistant starting up...")
    logger.info(f"   Environment : {settings.app_env}")
    logger.info(f"   LLM Model   : {settings.openai_model}")
    logger.info(f"   Vector Store: {settings.chroma_persist_dir}")
    yield
    logger.info("🛑 Dev Knowledge Assistant shutting down...")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Dev Knowledge Assistant",
    description=(
        "An AI-powered developer knowledge base using RAG (Retrieval-Augmented Generation). "
        "Upload documents, ask questions, and get answers grounded in your own content."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # React dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────
# Imported here (after app creation) to avoid circular imports.
# Full route implementations arrive in Day 4.
# from api.routes import query, ingest
# app.include_router(query.router, prefix="/api")
# app.include_router(ingest.router, prefix="/api")


# ── Health Check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Liveness probe — returns service status and basic config info.
    Used by Docker health checks and monitoring tools.
    """
    return {
        "status": "healthy",
        "service": "dev-knowledge-assistant",
        "version": "0.1.0",
        "environment": settings.app_env,
        "model": settings.openai_model,
        "timestamp": time.time(),
    }


# ── Root ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Dev Knowledge Assistant API",
        "docs": "/docs",
        "health": "/health",
    }


# ── Dev runner ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "development",
        log_level="info",
    )
