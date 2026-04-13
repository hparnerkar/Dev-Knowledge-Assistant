# Dev Knowledge Assistant — Architecture

## Overview

Dev Knowledge Assistant is a full-stack Retrieval-Augmented Generation (RAG) application that allows developers to query a custom knowledge base built from their own documents. Instead of relying solely on an LLM's training data, every answer is grounded in retrieved context from the vector store — reducing hallucinations and providing source citations.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│                                                                 │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │              React Frontend (Port 3000)                  │  │
│   │   ChatWindow │ InputBar │ SourceCard │ TokenUsage        │  │
│   └──────────────────────┬───────────────────────────────────┘  │
└──────────────────────────┼──────────────────────────────────────┘
                           │  HTTP (REST / JSON)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER                                │
│                                                                 │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │              FastAPI Backend (Port 8000)                  │  │
│   │                                                          │  │
│   │   POST /api/query   ──►  RAG Pipeline                    │  │
│   │   POST /api/ingest  ──►  Ingestion Pipeline              │  │
│   │   GET  /health      ──►  Health Check                    │  │
│   └───────────┬──────────────────────┬───────────────────────┘  │
└───────────────┼──────────────────────┼──────────────────────────┘
                │                      │
    ┌───────────▼──────────┐  ┌────────▼──────────────────────┐
    │   RETRIEVAL LAYER    │  │      INGESTION LAYER          │
    │                      │  │                               │
    │  ChromaDB            │  │  1. Load docs (.txt/.pdf/.md) │
    │  (Vector Store)      │  │  2. Chunk (LangChain splitter)│
    │                      │  │  3. Embed (OpenAI ada-002)    │
    │  similarity_search() │  │  4. Store in ChromaDB         │
    └───────────┬──────────┘  └───────────────────────────────┘
                │
    ┌───────────▼──────────────────────────────────────────────┐
    │                   GENERATION LAYER                        │
    │                                                          │
    │   LangChain RAG Chain                                    │
    │                                                          │
    │   Retrieved Chunks + User Question                       │
    │              │                                           │
    │              ▼                                           │
    │   System Prompt + Context Window                         │
    │              │                                           │
    │              ▼                                           │
    │   OpenAI GPT-3.5/4  ──► Answer + Token Usage            │
    └──────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Ingestion Pipeline (`backend/ingestion/`)

Responsible for processing raw documents into searchable vector embeddings.

| Module | Responsibility |
|--------|---------------|
| `loader.py` | Reads `.txt`, `.pdf`, `.md` files from a directory using LangChain document loaders |
| `chunker.py` | Splits documents into overlapping chunks using `RecursiveCharacterTextSplitter` |
| `embedder.py` | Converts chunks to embeddings via OpenAI `text-embedding-ada-002`, persists in ChromaDB |

**Chunking strategy:**
- `chunk_size = 500` tokens
- `chunk_overlap = 50` tokens (ensures context continuity across chunk boundaries)

---

### 2. RAG Pipeline (`backend/rag/`)

Handles the query → retrieve → generate flow.

| Module | Responsibility |
|--------|---------------|
| `retriever.py` | Performs cosine similarity search in ChromaDB, returns top-K chunks |
| `chain.py` | Assembles the LangChain RAG chain: retriever + prompt + LLM |
| `prompts.py` | Defines the system prompt, context injection template, and few-shot examples |

**Prompt design principles:**
- Instruct the model to answer ONLY from provided context
- If context is insufficient, say so rather than hallucinate
- Always cite the source document name

---

### 3. API Layer (`backend/api/`)

FastAPI routers exposing the ingestion and query functionality.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ingest` | POST | Triggers ingestion pipeline for a given directory |
| `/api/query` | POST | Runs the RAG pipeline and returns answer + sources |
| `/health` | GET | Returns service health status |

---

### 4. Frontend (`frontend/src/`)

React single-page application for interacting with the knowledge base.

| Component | Description |
|-----------|-------------|
| `ChatWindow.jsx` | Scrollable message thread (user + assistant turns) |
| `InputBar.jsx` | Text input with send button and loading state |
| `SourceCard.jsx` | Expandable card showing retrieved source chunk + metadata |
| `App.jsx` | Root component managing chat state |

---

## Data Flow: Query Request

```
1. User types question in InputBar
2. Frontend POSTs to /api/query with { question, top_k }
3. FastAPI receives request, validates with Pydantic
4. Retriever queries ChromaDB → returns top_k chunks
5. Chunks + question injected into LangChain prompt
6. LangChain chain calls OpenAI GPT
7. Response returned: { answer, sources, model, tokens_used, latency_ms }
8. Frontend renders answer in ChatWindow + sources in SourceCards
```

---

## Data Flow: Ingestion Request

```
1. User provides a directory path (or uploads files via UI)
2. Frontend POSTs to /api/ingest
3. Loader reads all supported files from directory
4. Chunker splits each document into overlapping chunks
5. Embedder calls OpenAI embeddings API for each chunk
6. Embeddings + metadata stored in ChromaDB (persisted to disk)
7. Success response returned with document + chunk counts
```

---

## Design Decisions

### Why ChromaDB?
- Runs locally with zero external dependencies or accounts
- Persists to disk — survives restarts
- Easy swap to Pinecone/Weaviate via LangChain's VectorStore interface

### Why LangChain?
- Abstracts the retriever-prompt-LLM chain into composable building blocks
- Makes it easy to swap models (GPT-3.5 → GPT-4 → open-source) without changing app logic
- Built-in tracing support via LangSmith

### Why FastAPI?
- Async-first — handles concurrent LLM calls efficiently
- Auto-generated OpenAPI docs at `/docs`
- Pydantic integration for clean request/response validation

---

## Future Enhancements

- [ ] Streaming responses (WebSocket / SSE)
- [ ] LangSmith tracing for observability
- [ ] Multi-collection support (separate knowledge bases)
- [ ] File upload via UI (drag-and-drop)
- [ ] Conversation memory (multi-turn context)
- [ ] Reranking with Cohere or cross-encoder models
- [ ] Auth layer (JWT)
