/**
 * ChatWindow.jsx
 * Scrollable message thread showing user questions and AI answers.
 * Renders markdown in AI responses, with source cards below each answer.
 */

import { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneLight } from "react-syntax-highlighter/dist/esm/styles/prism";
import SourceCard from "./SourceCard";

const UserBubble = ({ text }) => (
  <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "20px" }}>
    <div style={{
      background: "#3b82f6",
      color: "#fff",
      borderRadius: "16px 16px 4px 16px",
      padding: "12px 16px",
      maxWidth: "70%",
      fontSize: "14px",
      lineHeight: "1.6",
      boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
    }}>
      {text}
    </div>
  </div>
);

const AssistantBubble = ({ message }) => (
  <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: "24px" }}>
    <div style={{ maxWidth: "85%", width: "100%" }}>

      {/* Avatar + Answer */}
      <div style={{ display: "flex", gap: "10px", alignItems: "flex-start" }}>
        <div style={{
          width: "32px", height: "32px", borderRadius: "50%",
          background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
          display: "flex", alignItems: "center", justifyContent: "center",
          color: "#fff", fontSize: "14px", flexShrink: 0, marginTop: "2px",
        }}>
          🧠
        </div>

        <div style={{
          background: "#fff",
          border: "1px solid #e2e8f0",
          borderRadius: "4px 16px 16px 16px",
          padding: "14px 16px",
          fontSize: "14px",
          lineHeight: "1.7",
          color: "#1e293b",
          boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
          flex: 1,
        }}>
          <ReactMarkdown
            components={{
              code({ inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || "");
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={oneLight}
                    language={match[1]}
                    PreTag="div"
                    {...props}
                  >
                    {String(children).replace(/\n$/, "")}
                  </SyntaxHighlighter>
                ) : (
                  <code style={{
                    background: "#f1f5f9",
                    padding: "2px 6px",
                    borderRadius: "4px",
                    fontSize: "13px",
                    fontFamily: "'Fira Code', monospace",
                  }} {...props}>
                    {children}
                  </code>
                );
              },
              p: ({ children }) => (
                <p style={{ margin: "0 0 10px" }}>{children}</p>
              ),
            }}
          >
            {message.answer}
          </ReactMarkdown>
        </div>
      </div>

      {/* Meta: model, tokens, latency */}
      <div style={{
        display: "flex", gap: "12px", marginLeft: "42px",
        marginTop: "6px", flexWrap: "wrap",
      }}>
        {[
          { label: "🤖", value: message.model },
          { label: "🔤", value: `${message.tokens_used} tokens` },
          { label: "⚡", value: `${message.latency_ms}ms` },
        ].map(({ label, value }) => (
          <span key={value} style={{
            fontSize: "11px", color: "#94a3b8",
            background: "#f8fafc", padding: "2px 8px",
            borderRadius: "999px", border: "1px solid #e2e8f0",
          }}>
            {label} {value}
          </span>
        ))}
      </div>

      {/* Source cards */}
      {message.sources?.length > 0 && (
        <div style={{ marginLeft: "42px", marginTop: "12px" }}>
          <p style={{
            fontSize: "11px", color: "#94a3b8", margin: "0 0 8px",
            fontWeight: "600", textTransform: "uppercase", letterSpacing: "0.05em",
          }}>
            📚 {message.sources.length} Source{message.sources.length > 1 ? "s" : ""} Retrieved
          </p>
          {message.sources.map((source, i) => (
            <SourceCard key={source.chunk_id || i} source={source} index={i} />
          ))}
        </div>
      )}
    </div>
  </div>
);

const ThinkingBubble = () => (
  <div style={{ display: "flex", gap: "10px", alignItems: "center", marginBottom: "20px" }}>
    <div style={{
      width: "32px", height: "32px", borderRadius: "50%",
      background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
      display: "flex", alignItems: "center", justifyContent: "center",
      color: "#fff", fontSize: "14px",
    }}>
      🧠
    </div>
    <div style={{
      background: "#fff", border: "1px solid #e2e8f0",
      borderRadius: "4px 16px 16px 16px",
      padding: "14px 18px", display: "flex", gap: "6px", alignItems: "center",
    }}>
      {[0, 1, 2].map((i) => (
        <div key={i} style={{
          width: "8px", height: "8px", borderRadius: "50%",
          background: "#94a3b8",
          animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite`,
        }} />
      ))}
    </div>
  </div>
);

const EmptyState = () => (
  <div style={{
    display: "flex", flexDirection: "column", alignItems: "center",
    justifyContent: "center", height: "100%", color: "#94a3b8", gap: "12px",
  }}>
    <div style={{ fontSize: "48px" }}>🧠</div>
    <p style={{ fontSize: "16px", fontWeight: "600", color: "#475569", margin: 0 }}>
      Dev Knowledge Assistant
    </p>
    <p style={{ fontSize: "13px", margin: 0, textAlign: "center", maxWidth: "320px" }}>
      Ask any developer question. Answers are grounded in your ingested documents
      with source citations shown below each response.
    </p>
    <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", justifyContent: "center", marginTop: "8px" }}>
      {[
        "How do I reverse a linked list?",
        "What is Kafka consumer lag?",
        "Difference between PUT and PATCH?",
      ].map((q) => (
        <span key={q} style={{
          fontSize: "12px", background: "#f1f5f9",
          border: "1px solid #e2e8f0", borderRadius: "999px",
          padding: "4px 12px", color: "#475569",
        }}>
          {q}
        </span>
      ))}
    </div>
  </div>
);

export default function ChatWindow({ messages, loading }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div style={{
      flex: 1, overflowY: "auto", padding: "24px 20px",
      display: "flex", flexDirection: "column",
    }}>
      {messages.length === 0 && !loading ? (
        <EmptyState />
      ) : (
        <>
          {messages.map((msg, i) =>
            msg.role === "user" ? (
              <UserBubble key={i} text={msg.text} />
            ) : (
              <AssistantBubble key={i} message={msg} />
            )
          )}
          {loading && <ThinkingBubble />}
        </>
      )}
      <div ref={bottomRef} />
    </div>
  );
}
