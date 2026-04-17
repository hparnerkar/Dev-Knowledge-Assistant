/**
 * Sidebar.jsx
 * Left panel showing vector store stats and ingestion controls.
 */

import { useState } from "react";
import { ingestDocuments, getStats, clearStore } from "../api/client";

const StatRow = ({ label, value }) => (
  <div style={{
    display: "flex", justifyContent: "space-between",
    alignItems: "center", padding: "6px 0",
    borderBottom: "1px solid #f1f5f9",
  }}>
    <span style={{ fontSize: "12px", color: "#64748b" }}>{label}</span>
    <span style={{ fontSize: "12px", fontWeight: "600", color: "#1e293b" }}>{value}</span>
  </div>
);

export default function Sidebar({ onIngestComplete }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [directory, setDirectory] = useState("data/sample_docs");
  const [clearExisting, setClearExisting] = useState(false);

  const handleIngest = async () => {
    setLoading(true);
    setMessage("");
    try {
      const result = await ingestDocuments(directory, clearExisting);
      setMessage(`✅ Ingested ${result.documents_loaded} docs · ${result.chunk_stats.total_chunks} chunks · ${result.timing.total_seconds}s`);
      await handleGetStats();
      onIngestComplete?.();
    } catch (e) {
      setMessage(`❌ ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGetStats = async () => {
    try {
      const s = await getStats();
      setStats(s);
    } catch (e) {
      setMessage(`❌ ${e.message}`);
    }
  };

  const handleClear = async () => {
    if (!window.confirm("Clear all embeddings? This cannot be undone.")) return;
    setLoading(true);
    try {
      await clearStore();
      setStats(null);
      setMessage("🗑️ Vector store cleared.");
      onIngestComplete?.();
    } catch (e) {
      setMessage(`❌ ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      width: "260px", flexShrink: 0,
      background: "#f8fafc",
      borderRight: "1px solid #e2e8f0",
      display: "flex", flexDirection: "column",
      padding: "20px 16px", gap: "20px",
      overflowY: "auto",
    }}>
      {/* Title */}
      <div>
        <h2 style={{ margin: 0, fontSize: "15px", fontWeight: "700", color: "#1e293b" }}>
          🧠 Knowledge Base
        </h2>
        <p style={{ margin: "4px 0 0", fontSize: "11px", color: "#94a3b8" }}>
          Manage your document store
        </p>
      </div>

      {/* Ingest form */}
      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        <label style={{ fontSize: "12px", fontWeight: "600", color: "#475569" }}>
          Documents Directory
        </label>
        <input
          value={directory}
          onChange={(e) => setDirectory(e.target.value)}
          style={{
            fontSize: "12px", padding: "8px 10px",
            border: "1.5px solid #e2e8f0", borderRadius: "8px",
            fontFamily: "monospace", color: "#1e293b",
            outline: "none",
          }}
        />

        <label style={{
          display: "flex", alignItems: "center", gap: "8px",
          fontSize: "12px", color: "#475569", cursor: "pointer",
        }}>
          <input
            type="checkbox"
            checked={clearExisting}
            onChange={(e) => setClearExisting(e.target.checked)}
          />
          Clear existing before ingest
        </label>

        <button
          onClick={handleIngest}
          disabled={loading}
          style={{
            background: loading ? "#e2e8f0" : "#3b82f6",
            color: loading ? "#94a3b8" : "#fff",
            border: "none", borderRadius: "8px",
            padding: "9px", fontSize: "13px", fontWeight: "600",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "⏳ Ingesting..." : "⚡ Ingest Documents"}
        </button>

        <button
          onClick={handleGetStats}
          disabled={loading}
          style={{
            background: "transparent",
            color: "#3b82f6",
            border: "1.5px solid #3b82f6",
            borderRadius: "8px", padding: "7px",
            fontSize: "12px", fontWeight: "600",
            cursor: "pointer",
          }}
        >
          📊 Refresh Stats
        </button>
      </div>

      {/* Stats panel */}
      {stats && (
        <div style={{
          background: "#fff", border: "1px solid #e2e8f0",
          borderRadius: "10px", padding: "12px",
        }}>
          <p style={{ margin: "0 0 8px", fontSize: "12px", fontWeight: "700", color: "#475569" }}>
            Vector Store Stats
          </p>
          <StatRow label="Collection" value={stats.collection} />
          <StatRow label="Total Chunks" value={stats.total_chunks.toLocaleString()} />
          <StatRow label="Persist Dir" value={stats.persist_dir} />
        </div>
      )}

      {/* Status message */}
      {message && (
        <div style={{
          fontSize: "12px", color: "#475569",
          background: "#f1f5f9", borderRadius: "8px",
          padding: "10px", lineHeight: "1.5",
        }}>
          {message}
        </div>
      )}

      {/* Danger zone */}
      <div style={{ marginTop: "auto" }}>
        <button
          onClick={handleClear}
          disabled={loading}
          style={{
            width: "100%", background: "transparent",
            color: "#ef4444", border: "1.5px solid #ef4444",
            borderRadius: "8px", padding: "7px",
            fontSize: "12px", fontWeight: "600",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          🗑️ Clear Store
        </button>
      </div>
    </div>
  );
}
