import React, { useState, useRef, useEffect } from "react";

const API_URL = "http://127.0.0.1:8000";

const AGENT_AVATAR = "🧑‍💼";
const USER_AVATAR = "🧑";
const SYSTEM_AVATAR = "💡";

function App() {
  const [chatLog, setChatLog] = useState([]);
  const [message, setMessage] = useState("");
  const wsRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatLog]);

  // Connect WebSocket on mount
  useEffect(() => {
    connectWebSocket();
    // eslint-disable-next-line
  }, []);

  // Connect WebSocket
  const connectWebSocket = () => {
    if (wsRef.current) wsRef.current.close();
    const ws = new window.WebSocket(`ws://127.0.0.1:8000/ws/chat`);
    ws.onopen = () => {
      setChatLog((log) => [
        ...log,
        { sender: "system", content: "WebSocket connected." },
      ]);
    };
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setChatLog((log) => [
          ...log,
          {
            sender: data.agent || "agent",
            content: data.content,
            tool: data.tool,
            handoff: data.handoff,
          },
        ]);
      } catch {
        setChatLog((log) => [
          ...log,
          { sender: "system", content: event.data },
        ]);
      }
    };
    ws.onclose = () => {
      setChatLog((log) => [
        ...log,
        { sender: "system", content: "WebSocket closed." },
      ]);
    };
    ws.onerror = (e) => {
      setChatLog((log) => [
        ...log,
        { sender: "system", content: "WebSocket error." },
      ]);
    };
    wsRef.current = ws;
  };

  // Send chat message
  const handleSend = (e) => {
    e.preventDefault();
    if (!message.trim() || !wsRef.current || wsRef.current.readyState !== 1) return;
    wsRef.current.send(JSON.stringify({ content: message }));
    setChatLog((log) => [
      ...log,
      { sender: "you", content: message },
    ]);
    setMessage("");
  };

  // Chat bubble style helper
  const getBubbleStyle = (sender) => {
    if (sender === "you") {
      return {
        background: "linear-gradient(90deg,#e0e7ff 0,#c7d2fe 100%)",
        color: "#1e293b",
        alignSelf: "flex-end",
        borderRadius: "18px 18px 6px 18px",
        marginLeft: 48,
        boxShadow: "0 2px 8px #c7d2fe33"
      };
    } else if (sender === "system") {
      return {
        background: "#f1f5f9",
        color: "#64748b",
        alignSelf: "center",
        borderRadius: 14,
        fontStyle: "italic",
        fontSize: "0.97em",
        margin: "10px auto",
        maxWidth: "80%",
        boxShadow: "none"
      };
    } else {
      return {
        background: "linear-gradient(90deg,#f0fdfa 0,#e0f2fe 100%)",
        color: "#0f172a",
        border: "1px solid #bae6fd",
        alignSelf: "flex-start",
        borderRadius: "18px 18px 18px 6px",
        marginRight: 48,
        boxShadow: "0 2px 8px #bae6fd33"
      };
    }
  };

  // Avatar helper
  const getAvatar = (sender) => {
    if (sender === "you") return USER_AVATAR;
    if (sender === "system") return SYSTEM_AVATAR;
    return AGENT_AVATAR;
  };

  return (
    <div style={{ minHeight: "100vh", background: "#f8fafc", padding: "2rem 0", fontFamily: 'Inter, Segoe UI, Arial, sans-serif' }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
        ::selection { background: #c7d2fe; }
      `}</style>
      <div style={{
        maxWidth: 900,
        margin: "0 auto",
        background: "#fff",
        borderRadius: 16,
        boxShadow: "0 4px 32px rgba(30,41,59,0.10)",
        padding: 0,
        minHeight: 700,
        display: "flex",
        flexDirection: "column"
      }}>
        <div style={{
          background: "linear-gradient(90deg,#6366f1 0,#38bdf8 100%)",
          borderRadius: "16px 16px 0 0",
          padding: "28px 0 18px 0",
          textAlign: "center",
          color: "#fff",
          fontWeight: 600,
          fontSize: 28,
          letterSpacing: 0.5,
          boxShadow: "0 2px 8px #38bdf833"
        }}>
          Career Coach Chatbot
        </div>
        <div style={{ padding: 28, flex: 1, display: 'flex', flexDirection: 'column' }}>
          <div
            style={{
              border: "1px solid #e0e0e0",
              borderRadius: 10,
              padding: 16,
              minHeight: 400,
              background: "#f8fafc",
              marginBottom: 20,
              maxHeight: 600,
              overflowY: "auto",
              display: "flex",
              flexDirection: "column"
            }}
          >
            {chatLog.map((msg, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  flexDirection: msg.sender === "you" ? "row-reverse" : "row",
                  alignItems: "flex-end",
                  marginBottom: 12,
                  gap: 10
                }}
              >
                <div style={{ fontSize: 24, marginBottom: msg.sender === "system" ? 0 : 2, marginLeft: msg.sender === "you" ? 8 : 0, marginRight: msg.sender === "you" ? 0 : 8 }}>
                  {getAvatar(msg.sender)}
                </div>
                <div style={{
                  ...getBubbleStyle(msg.sender),
                  padding: "14px 20px",
                  maxWidth: 700,
                  wordBreak: "break-word",
                  fontSize: 16,
                  lineHeight: 1.7,
                  boxShadow: msg.sender === "you" ? "0 1px 8px #c7d2fe33" : msg.sender === "system" ? "none" : "0 1px 8px #bae6fd33"
                }}>
                  <span style={{ fontWeight: 500, fontSize: 13, marginRight: 4 }}>
                    {msg.sender === "you" ? "You" : msg.sender === "system" ? "System" : msg.sender}
                  </span>
                  <span style={{ fontWeight: 400, whiteSpace: 'pre-line', display: 'block' }}>{msg.content}</span>
                  {msg.tool && (
                    <div style={{ fontSize: "0.92em", color: "#555", marginTop: 4 }}>
                      <em>Tool used: {JSON.stringify(msg.tool)}</em>
                    </div>
                  )}
                  {msg.handoff && (
                    <div style={{ fontSize: "0.92em", color: "#007bff", marginTop: 4 }}>
                      <em>Handoff occurred</em>
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>
          <form onSubmit={handleSend} style={{ display: "flex", gap: 10, marginTop: "auto" }}>
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              style={{ flex: 1, padding: 12, borderRadius: 8, border: '1px solid #cbd5e1', fontSize: 16, background: '#f1f5f9' }}
            />
            <button
              type="submit"
              disabled={!message.trim()}
              style={{
                background: 'linear-gradient(90deg,#6366f1 0,#38bdf8 100%)',
                color: '#fff',
                border: 'none',
                borderRadius: 8,
                padding: '0 28px',
                fontWeight: 600,
                fontSize: 16,
                cursor: !message.trim() ? 'not-allowed' : 'pointer',
                opacity: !message.trim() ? 0.6 : 1,
                boxShadow: '0 2px 8px #38bdf833',
                transition: 'background 0.2s'
              }}
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App; 