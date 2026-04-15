"""
prompts.py
Defines all prompt templates used in the RAG pipeline.

Design principles:
  - Ground answers strictly in provided context
  - Instruct the model to admit uncertainty rather than hallucinate
  - Always cite source document names
  - Return structured, developer-friendly responses
"""

from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Dev Knowledge Assistant, an expert AI assistant \
that answers developer questions strictly based on the provided context documents.

RULES YOU MUST FOLLOW:
1. Answer ONLY using the information in the context below.
2. If the context does not contain enough information to answer, say:
   "I don't have enough information in the knowledge base to answer this. \
   Try ingesting more relevant documents."
3. Never fabricate information, APIs, or code that is not in the context.
4. Always mention which source document(s) your answer is based on.
5. Format code examples with proper markdown code blocks.
6. Be concise but thorough. Developers value precision.

CONTEXT DOCUMENTS:
{context}
"""

# ── Human / User Turn ─────────────────────────────────────────────────────────
HUMAN_PROMPT = """Question: {question}

Please provide a clear, accurate answer based solely on the context documents above.
At the end, list the source document(s) you referenced."""

# ── Full Chat Prompt Template ─────────────────────────────────────────────────
RAG_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template(HUMAN_PROMPT),
])

# ── Condense Question Prompt (for multi-turn future use) ─────────────────────
CONDENSE_QUESTION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "Given a chat history and a follow-up question, rephrase the follow-up "
        "as a standalone question that contains all necessary context. "
        "Output ONLY the rephrased question, nothing else.",
    ),
    (
        "human",
        "Chat history:\n{chat_history}\n\nFollow-up question: {question}",
    ),
])


def format_context(docs) -> str:
    """
    Formats a list of retrieved Document chunks into a single context string
    to be injected into the system prompt.

    Each chunk is labelled with its source filename and chunk index
    so the model can cite them accurately.
    """
    sections = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "unknown")
        chunk_idx = doc.metadata.get("chunk_index", i)
        sections.append(
            f"[Source {i+1}: {source} | chunk {chunk_idx}]\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(sections)
