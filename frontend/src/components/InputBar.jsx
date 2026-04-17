/**
 * InputBar.jsx
 * Text input bar at the bottom of the chat UI.
 * Handles user question submission with loading state and keyboard shortcut.
 */

import { useState } from "react";

export default function InputBar({ onSubmit, loading, disabled }) {
  const [value, setValue] = useState("");

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (!trimmed || loading) return;
    onSubmit(trimmed);
    setValue("");
  };

  const handleKeyDown = (e) => {
    // Submit on Enter, new line on Shift+Enter
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div style={{
      display: "flex",
      alignItems: "flex-end",
      gap: "10px",
      padding: "16px 20px",
      borderTop: "1px solid #e2e8f0",
      background: "#fff",
    }}>
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={disabled ? "Please ingest documents first..." : "Ask a developer question... (Enter to send, Shift+Enter for new line)"}
        disabled={loading || disabled}
        rows={1}
        style={{
          flex: 1,
          resize: "none",
          border: "1.5px solid #e2e8f0",
          borderRadius: "10px",
          padding: "12px 14px",
          fontSize: "14px",
          fontFamily: "inherit",
          outline: "none",
          lineHeight: "1.5",
          transition: "border-color 0.2s",
          background: disabled ? "#f8fafc" : "#fff",
          color: "#1e293b",
          maxHeight: "120px",
          overflowY: "auto",
        }}
        onFocus={(e) => (e.target.style.borderColor = "#3b82f6")}
        onBlur={(e) => (e.target.style.borderColor = "#e2e8f0")}
      />

      <button
        onClick={handleSubmit}
        disabled={!value.trim() || loading || disabled}
        style={{
          background: !value.trim() || loading || disabled ? "#e2e8f0" : "#3b82f6",
          color: !value.trim() || loading || disabled ? "#94a3b8" : "#fff",
          border: "none",
          borderRadius: "10px",
          padding: "12px 18px",
          fontSize: "14px",
          fontWeight: "600",
          cursor: !value.trim() || loading || disabled ? "not-allowed" : "pointer",
          transition: "background 0.2s",
          whiteSpace: "nowrap",
          minWidth: "80px",
        }}
      >
        {loading ? (
          <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span className="spinner" />
            Thinking...
          </span>
        ) : "Send ↑"}
      </button>
    </div>
  );
}
