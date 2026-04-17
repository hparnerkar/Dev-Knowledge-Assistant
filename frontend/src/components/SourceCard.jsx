/**
 * SourceCard.jsx
 * Displays a single retrieved document chunk as a collapsible citation card.
 * Shows source filename, similarity score, chunk index, and content preview.
 */

import { useState } from "react";

const scoreColor = (score) => {
  if (score >= 0.85) return "#22c55e"; // green
  if (score >= 0.70) return "#f59e0b"; // amber
  return "#ef4444";                    // red
};

const scoreLabel = (score) => {
  if (score >= 0.85) return "High";
  if (score >= 0.70) return "Medium";
  return "Low";
};

export default function SourceCard({ source, index }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div style={{
      border: "1px solid #e2e8f0",
      borderLeft: `4px solid ${scoreColor(source.similarity_score)}`,
      borderRadius: "8px",
      marginBottom: "8px",
      background: "#f8fafc",
      overflow: "hidden",
    }}>
      {/* Header row */}
      <div
        onClick={() => setExpanded(!expanded)}
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "10px 14px",
          cursor: "pointer",
          userSelect: "none",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          {/* Source number badge */}
          <span style={{
            background: "#3b82f6",
            color: "#fff",
            borderRadius: "50%",
            width: "22px",
            height: "22px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "11px",
            fontWeight: "700",
            flexShrink: 0,
          }}>
            {index + 1}
          </span>

          {/* Filename */}
          <span style={{ fontSize: "13px", fontWeight: "600", color: "#1e293b" }}>
            📄 {source.source}
          </span>

          {/* Chunk index */}
          <span style={{ fontSize: "11px", color: "#94a3b8" }}>
            chunk #{source.chunk_index}
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          {/* Similarity score badge */}
          <span style={{
            fontSize: "11px",
            fontWeight: "600",
            color: scoreColor(source.similarity_score),
            background: `${scoreColor(source.similarity_score)}18`,
            padding: "2px 8px",
            borderRadius: "999px",
          }}>
            {scoreLabel(source.similarity_score)} · {(source.similarity_score * 100).toFixed(1)}%
          </span>

          {/* Expand chevron */}
          <span style={{
            fontSize: "12px",
            color: "#94a3b8",
            transform: expanded ? "rotate(180deg)" : "rotate(0deg)",
            transition: "transform 0.2s",
          }}>
            ▼
          </span>
        </div>
      </div>

      {/* Expandable content */}
      {expanded && (
        <div style={{
          padding: "10px 14px 14px",
          borderTop: "1px solid #e2e8f0",
        }}>
          <p style={{
            fontSize: "12px",
            color: "#64748b",
            margin: "0 0 6px",
            fontWeight: "600",
            textTransform: "uppercase",
            letterSpacing: "0.05em",
          }}>
            Content Preview
          </p>
          <pre style={{
            fontSize: "12px",
            color: "#334155",
            background: "#f1f5f9",
            padding: "10px",
            borderRadius: "6px",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            margin: 0,
            lineHeight: "1.6",
            fontFamily: "'Fira Code', 'Courier New', monospace",
          }}>
            {source.content}
          </pre>
          <p style={{ fontSize: "11px", color: "#94a3b8", margin: "6px 0 0" }}>
            ID: {source.chunk_id}
          </p>
        </div>
      )}
    </div>
  );
}
