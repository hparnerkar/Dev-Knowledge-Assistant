/**
 * client.js
 * Axios-based API client for communicating with the FastAPI backend.
 * All backend calls go through this module — never call fetch() directly.
 */

import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 60000, // 60s — LLM calls can be slow
});

// ── Request interceptor — log outgoing requests in dev ────────────────────────
api.interceptors.request.use((config) => {
  if (process.env.NODE_ENV === "development") {
    console.log(`→ ${config.method?.toUpperCase()} ${config.url}`, config.data || "");
  }
  return config;
});

// ── Response interceptor — normalize errors ───────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.error ||
      error.message ||
      "An unexpected error occurred.";
    return Promise.reject(new Error(message));
  }
);

// ── Health ────────────────────────────────────────────────────────────────────
export const checkHealth = async () => {
  const { data } = await api.get("/health");
  return data;
};

// ── Query ─────────────────────────────────────────────────────────────────────
/**
 * Send a question to the RAG pipeline.
 * @param {string} question - The user's natural language question.
 * @param {number} [topK=5] - Number of chunks to retrieve.
 * @param {string} [model] - Optional model override.
 * @returns {Promise<QueryResponse>}
 */
export const queryKnowledgeBase = async (question, topK = 5, model = null) => {
  const payload = { question, top_k: topK };
  if (model) payload.model = model;
  const { data } = await api.post("/api/query", payload);
  return data;
};

// ── Ingest ────────────────────────────────────────────────────────────────────
/**
 * Trigger the ingestion pipeline for a directory.
 * @param {string} directory - Path to documents directory.
 * @param {boolean} clearExisting - Whether to wipe store first.
 * @returns {Promise<IngestResponse>}
 */
export const ingestDocuments = async (directory = "data/sample_docs", clearExisting = false) => {
  const { data } = await api.post("/api/ingest", {
    directory,
    clear_existing: clearExisting,
  });
  return data;
};

/**
 * Get current vector store statistics.
 * @returns {Promise<StatsResponse>}
 */
export const getStats = async () => {
  const { data } = await api.get("/api/ingest/stats");
  return data;
};

/**
 * Clear all embeddings from the vector store.
 * @returns {Promise<{status: string}>}
 */
export const clearStore = async () => {
  const { data } = await api.delete("/api/ingest");
  return data;
};
