import { useState, useEffect } from "react";
import "./App.css";

const STORAGE_KEY = "tsb_settings";

function loadSettings() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) return JSON.parse(saved);
  } catch {}
  return { jira_email: "", jira_token: "", jira_url: "", groq_key: "" };
}

function App() {
  const [settings, setSettings] = useState(loadSettings);
  const [showSettings, setShowSettings] = useState(false);
  const [ticketId, setTicketId] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [showResult, setShowResult] = useState(false);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  }, [settings]);

  const hasSettings = settings.jira_url && settings.groq_key;

  const handleSettingChange = (key, value) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  const handleGenerate = async () => {
    if (!ticketId.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    setShowResult(false);

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...settings,
          ticket_id: ticketId.trim().toUpperCase(),
        }),
      });
      const data = await res.json();
      if (!data.success) {
        setError(data.error || "Generation failed.");
      } else {
        setResult(data);
        setShowResult(true);
      }
    } catch (err) {
      setError("Cannot connect to backend. Make sure the server is running on port 5000.");
    }
    setLoading(false);
  };

  const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:5000" : "";

  const handleDownload = () => {
    if (result?.pdf_url) {
      window.open(`${API_BASE}${result.pdf_url}`, "_blank");
    }
  };

  return (
    <div className="App">
      <header className="header">
        <div className="container">
          <h1>Test Strategy Buddy</h1>
          <p className="subtitle">Generate professional test strategies from Jira tickets using AI</p>
        </div>
      </header>

      <main className="container">
        {/* Connection indicator */}
        <div className="card" style={{ padding: "12px 24px" }}>
          <span style={{ fontSize: "0.85rem" }}>
            <span className={`indicator ${hasSettings ? "indicator-green" : "indicator-gray"}`} />
            {hasSettings ? "Connected — Jira & GROQ configured" : "Not configured — open settings to connect"}
          </span>
          <button className="settings-toggle" onClick={() => setShowSettings(!showSettings)} style={{ float: "right" }}>
            {showSettings ? "Hide Settings" : "Settings"}
          </button>
        </div>

        {/* Settings */}
        {showSettings && (
          <div className="card">
            <h2>Settings</h2>
            <div className="form-group">
              <label>Jira URL</label>
              <input
                type="text"
                placeholder="https://your-domain.atlassian.net"
                value={settings.jira_url}
                onChange={(e) => handleSettingChange("jira_url", e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Jira Email</label>
              <input
                type="email"
                placeholder="you@email.com"
                value={settings.jira_email}
                onChange={(e) => handleSettingChange("jira_email", e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Jira API Token</label>
              <input
                type="password"
                placeholder="Your Jira API token"
                value={settings.jira_token}
                onChange={(e) => handleSettingChange("jira_token", e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>GROQ API Key</label>
              <input
                type="password"
                placeholder="gsk_..."
                value={settings.groq_key}
                onChange={(e) => handleSettingChange("groq_key", e.target.value)}
              />
            </div>
            <p className="save-hint">Settings are saved automatically to your browser.</p>
          </div>
        )}

        {/* Generator */}
        <div className="card">
          <h2>Generate Test Strategy</h2>
          <div className="ticket-row">
            <div className="form-group">
              <label>Jira Ticket ID</label>
              <input
                type="text"
                placeholder="e.g., VWO-48, SCRUM-42"
                value={ticketId}
                onChange={(e) => setTicketId(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
              />
            </div>
            <button
              className="btn btn-primary"
              onClick={handleGenerate}
              disabled={loading || !ticketId.trim() || !hasSettings}
            >
              {loading ? (
                <>
                  <span className="spinner" /> Generating...
                </>
              ) : (
                "Generate"
              )}
            </button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="alert alert-error">{error}</div>
        )}

        {/* Result */}
        {result && showResult && (
          <div className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
              <h2 style={{ margin: 0, border: "none", padding: 0 }}>
                {result.summary || "Test Strategy"}
              </h2>
              <span style={{ fontSize: "0.8rem", color: "#888" }}>
                {result.ticket_id}
              </span>
            </div>

            <div className="markdown-output">
              {result.markdown.split("\n").map((line, i) => {
                if (line.startsWith("### ")) return <h3 key={i}>{line.slice(4)}</h3>;
                if (line.startsWith("## ")) return <h2 key={i}>{line.slice(3)}</h2>;
                if (line.startsWith("# ")) return <h1 key={i}>{line.slice(2)}</h1>;
                if (line.startsWith("**") && line.includes("**", 2)) return <p key={i} className="bold-sub"><strong>{line.replace(/\*\*/g, "")}</strong></p>;
                if (line.startsWith("- ")) return <li key={i}>{line.slice(2)}</li>;
                if (/^\d+\./.test(line)) return <li key={i}>{line.replace(/^\d+\.\s*/, "")}</li>;
                if (line.trim() === "") return <br key={i} />;
                return <p key={i}>{line}</p>;
              })}
            </div>

            <div className="action-bar">
              <button className="btn btn-success" onClick={handleDownload}>
                Download PDF
              </button>
              <button className="btn btn-outline" onClick={() => setShowResult(false)}>
                Close
              </button>
            </div>
          </div>
        )}

        {/* Empty state */}
        {!result && !error && (
          <div className="card empty-state">
            <h3>Ready to go</h3>
            <p>Enter a Jira ticket ID above and click Generate to create your test strategy.</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
