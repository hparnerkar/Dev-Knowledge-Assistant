"""
chain.py
Assembles and runs the LangChain RAG chain.

Flow:
    user question
        → retrieve relevant chunks from ChromaDB
        → format chunks into context string
        → inject into RAG_PROMPT
        → call OpenAI GPT
        → return answer + sources + usage metadata
"""

import logging
import time
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.schema.output_parser import StrOutputParser

from config import get_settings
from rag.retriever import retrieve_chunks, retrieve_with_scores
from rag.prompts import RAG_PROMPT, format_context

logger = logging.getLogger(__name__)


def get_llm(model: Optional[str] = None) -> ChatOpenAI:
    """
    Returns a configured ChatOpenAI instance.

    Args:
        model: Optional model override (e.g. 'gpt-4'). 
               Defaults to settings.openai_model.
    """
    settings = get_settings()
    return ChatOpenAI(
        model=model or settings.openai_model,
        openai_api_key=settings.openai_api_key,
        temperature=0.2,       # low temp for factual, grounded answers
        max_tokens=1024,
    )


def run_rag_chain(
    question: str,
    top_k: Optional[int] = None,
    model: Optional[str] = None,
) -> dict:
    """
    Runs the full RAG pipeline for a given question.

    Steps:
        1. Retrieve top-K relevant chunks from ChromaDB
        2. Format chunks into a context block
        3. Build the prompt (system + human)
        4. Call OpenAI GPT and stream the response
        5. Return answer, sources, token usage, and latency

    Args:
        question: The user's natural language question.
        top_k:    Number of chunks to retrieve (default from settings).
        model:    LLM model override (e.g. 'gpt-4').

    Returns:
        dict with keys:
            - answer       (str)
            - sources      (list of source metadata dicts)
            - model        (str)
            - tokens_used  (int)
            - latency_ms   (int)

    Raises:
        ValueError: If the vector store is empty.
        Exception:  Propagates OpenAI API errors.
    """
    settings = get_settings()
    start = time.time()

    # ── Step 1: Retrieve ──────────────────────────────────────────────────────
    logger.info(f"RAG query: '{question[:80]}'")
    chunks_with_scores = retrieve_with_scores(question, top_k=top_k)
    chunks = [doc for doc, _ in chunks_with_scores]
    scores = [score for _, score in chunks_with_scores]

    # ── Step 2: Format context ────────────────────────────────────────────────
    context = format_context(chunks)

    # ── Step 3: Build prompt ──────────────────────────────────────────────────
    prompt_value = RAG_PROMPT.format_messages(
        context=context,
        question=question,
    )

    # ── Step 4: Call LLM ──────────────────────────────────────────────────────
    llm = get_llm(model)
    response = llm.invoke(prompt_value)

    latency_ms = int((time.time() - start) * 1000)
    answer = response.content
    tokens_used = response.response_metadata.get("token_usage", {}).get("total_tokens", 0)
    model_used = response.response_metadata.get("model_name", settings.openai_model)

    logger.info(
        f"Answer generated in {latency_ms}ms | "
        f"tokens={tokens_used} | model={model_used}"
    )

    # ── Step 5: Build sources list ────────────────────────────────────────────
    sources = []
    for doc, score in zip(chunks, scores):
        sources.append({
            "content": doc.page_content[:300],   # preview, not full chunk
            "source": doc.metadata.get("source", "unknown"),
            "chunk_index": doc.metadata.get("chunk_index", 0),
            "chunk_id": doc.metadata.get("chunk_id", ""),
            "similarity_score": round(score, 4),
        })

    return {
        "answer": answer,
        "sources": sources,
        "model": model_used,
        "tokens_used": tokens_used,
        "latency_ms": latency_ms,
    }


def build_lcel_chain(top_k: Optional[int] = None, model: Optional[str] = None):
    """
    Returns a composable LangChain Expression Language (LCEL) chain.
    Useful for chaining with other components or streaming.

    Usage:
        chain = build_lcel_chain()
        result = chain.invoke({"question": "How does Kafka work?"})
    """
    settings = get_settings()
    llm = get_llm(model)

    def retrieve_and_format(inputs: dict) -> dict:
        question = inputs["question"]
        chunks = retrieve_chunks(question, top_k=top_k or settings.top_k_results)
        return {
            "context": format_context(chunks),
            "question": question,
        }

    chain = (
        RunnableLambda(retrieve_and_format)
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )

    return chain
