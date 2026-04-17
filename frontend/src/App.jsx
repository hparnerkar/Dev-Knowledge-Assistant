/**
 * App.jsx
 * Root component — manages chat state and wires together
 * Sidebar, ChatWindow, and InputBar.
 */

import { useState, useEffect } from "react";
import ChatWindow from "./components/ChatWindow";
import InputBar from "./components/InputBar";
import Sidebar from "./components/Sidebar";
import { queryKnowledgeBase, checkHealth } from "./api/client";
import "./App.css";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState("checking"); // checking | healthy | down
  const [storeReady, setStoreReady] = useState(false);

  // ── Check backend health on mount ─────────────────────────────────────────
  useEffect(() => {
    checkHealth()
      .then(() => setBackendStatus("healthy"))
      .catch(() => setBackendStatus("down"));
  }, []);

  // ── Submit a question ──────────────────────────────────────────────────────
  const handleSubmit = async (question) => {
    // Add user message immediately
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setLoading(true);

    try {
      const result = await queryKnowledgeBase(question);
      setMessages((prev) => [...prev, { role: "assistant", ...result }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          answer: `⚠️ **Error:** ${err.message}`,
          sources: [],
          model: "—",
          tokens_used: 0,
          latency_ms: 0,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // ── Clear chat history ─────────────────────────────────────────────────────
  const handleClearChat = () => setMessages([]);

  return (
    <div style={{
      display: "flex", flexDirection: "column",
      height: "100vh", fontFamily: "'Inter', -apple-system, sans-serif",
      background: "#f8fafc",
    }}>

      {/* ── Top nav ── */}
      <header style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "0 20px", height: "56px",
        background: "#fff", borderBottom: "1px solid #e2e8f0",
        boxShadow: "0 1px 3px rgba(0,0,0,0.05)", flexShrink: 0,
        zIndex: 10,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span style={{ fontSize: "22px" }}>🧠</span>
          <div>
            <h1 style={{ margin: 0, fontSize: "15px", fontWeight: "700", color: "#1e293b" }}>
              Dev Knowledge Assistant
            </h1>
            <p style={{ margin: 0, fontSize: "11px", color: "#94a3b8" }}>
              RAG-powered · OpenAI GPT · ChromaDB
            </p>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          {/* Backend status dot */}
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <div style={{
              width: "8px", height: "8px", borderRadius: "50%",
              background:
                backendStatus === "healthy" ? "#22c55e" :
                backendStatus === "down" ? "#ef4444" : "#f59e0b",
            }} />
            <span style={{ fontSize: "12px", color: "#64748b" }}>
              {backendStatus === "healthy" ? "Backend Online" :
               backendStatus === "down" ? "Backend Offline" : "Connecting..."}
            </span>
          </div>

          {/* Clear chat */}
          {messages.length > 0 && (
            <button
              onClick={handleClearChat}
              style={{
                background: "transparent", border: "1.5px solid #e2e8f0",
                borderRadius: "8px", padding: "5px 12px",
                fontSize: "12px", color: "#64748b",
                cursor: "pointer", fontWeight: "500",
              }}
            >
              🗑 Clear Chat
            </button>
          )}
        </div>
      </header>

      {/* ── Main body ── */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        {/* Sidebar */}
        <Sidebar onIngestComplete={() => setStoreReady(true)} />

        {/* Chat area */}
        <div style={{
          display: "flex", flexDirection: "column", flex: 1, overflow: "hidden",
        }}>
          <ChatWindow messages={messages} loading={loading} />
          <InputBar
            onSubmit={handleSubmit}
            loading={loading}
            disabled={backendStatus === "down"}
          />
        </div>
      </div>
    </div>
  );
}
