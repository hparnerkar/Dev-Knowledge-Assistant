# 🧠 Dev Knowledge Assistant

A full-stack AI-powered developer knowledge base using **Retrieval-Augmented Generation (RAG)**. Ask questions, get answers grounded in your own documents — with source citations shown in the UI.

![Stack](https://img.shields.io/badge/Python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green) ![LangChain](https://img.shields.io/badge/LangChain-0.1-orange) ![React](https://img.shields.io/badge/React-18-61DAFB) ![ChromaDB](https://img.shields.io/badge/ChromaDB-latest-purple)

---

## 🏗️ Architecture

```
User Query
    │
    ▼
React Frontend  ──────►  FastAPI Backend
                              │
                    ┌─────────┴──────────┐
                    │                    │
              ChromaDB              OpenAI GPT
           (Vector Store)         (LLM Response)
                    │                    │
              Retrieve Top-K       Generate Answer
              Relevant Chunks      with Context
                    └─────────┬──────────┘
                              │
                         Final Answer
                       + Source Citations
```

---

## 🚀 Features

- 📄 **Document Ingestion** — Load `.txt`, `.pdf`, `.md` files into a vector store
- 🔍 **Semantic Search** — ChromaDB similarity search over embedded chunks
- 🤖 **RAG Pipeline** — LangChain chain combining retrieval + GPT generation
- 💬 **Chat UI** — React frontend with message history and source cards
- 📊 **Observability** — Token usage, model info, and latency displayed per query
- 🐳 **Docker Support** — One command to spin up the full stack

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Tailwind CSS, Axios |
| Backend | Python 3.11, FastAPI, Uvicorn |
| AI / LLM | OpenAI GPT-3.5/4, LangChain |
| Vector DB | ChromaDB (local) |
| Embeddings | OpenAI text-embedding-ada-002 |
| DevOps | Docker, Docker Compose |

---

## ⚡ Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/hparnerkar/Dev-Knowledge-Assistant.git
cd Dev-Knowledge-Assistant
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run with Docker (recommended)
```bash
docker-compose up --build
```

### 4. Or run locally

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

### 5. Ingest sample documents
```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory": "data/sample_docs"}'
```

### 6. Open the app
Visit `http://localhost:3000` and start asking questions!

---

## 📁 Project Structure

```
Dev-Knowledge-Assistant/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings & environment variables
│   ├── requirements.txt     # Python dependencies
│   ├── api/
│   │   ├── routes/
│   │   │   ├── query.py     # POST /api/query
│   │   │   └── ingest.py    # POST /api/ingest
│   │   └── models.py        # Pydantic request/response models
│   ├── ingestion/
│   │   ├── loader.py        # Document loaders
│   │   ├── chunker.py       # Text splitting
│   │   └── embedder.py      # Embedding + ChromaDB storage
│   └── rag/
│       ├── retriever.py     # ChromaDB similarity search
│       ├── chain.py         # LangChain RAG chain
│       └── prompts.py       # System prompts & templates
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── ChatWindow.jsx
│       │   ├── InputBar.jsx
│       │   └── SourceCard.jsx
│       ├── api/client.js
│       └── App.jsx
├── data/
│   └── sample_docs/         # Drop your .txt/.md/.pdf files here
├── docs/
│   └── architecture.md      # Detailed architecture documentation
├── .env.example
├── .gitignore
└── docker-compose.yml
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/ingest` | Ingest documents into vector store |
| POST | `/api/query` | Query the RAG pipeline |

### Example Query Request
```json
POST /api/query
{
  "question": "How do I reverse a linked list in Python?",
  "top_k": 5
}
```

### Example Query Response
```json
{
  "answer": "To reverse a linked list in Python...",
  "sources": [
    {
      "content": "...",
      "metadata": { "source": "python-data-structures.txt", "chunk": 3 }
    }
  ],
  "model": "gpt-3.5-turbo",
  "tokens_used": 412,
  "latency_ms": 1240
}
```

---

## 🗂️ Daily Development Log

| Day | Focus | Status |
|-----|-------|--------|
| Day 1 | Project scaffold, FastAPI base, README | ✅ Done |
| Day 2 | Document ingestion pipeline (loader, chunker, embedder) | ✅ Done |
| Day 3 | RAG pipeline (retriever, LangChain chain, prompts) | ✅ Done |
| Day 4 | REST API endpoints + Pydantic models | ⏳ Planned |
| Day 5 | React frontend — chat UI + source cards | ⏳ Planned |
| Day 6 | Polish — error handling, observability, prompt tuning | ⏳ Planned |
| Day 7 | Docker, final README, demo | ⏳ Planned |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
