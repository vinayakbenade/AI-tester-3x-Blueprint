import { useState, useEffect } from "react";

const API = "/api";

const STEPS_ICONS = {
  "PDF Loading": "📄",
  "Text Extraction": "🔍",
  "Chunking": "✂️",
  "Embedding": "🧬",
  "ChromaDB Storage": "💾",
  "Query Embedding": "🧬",
  "Vector Search": "🎯",
  "LLM Answer Generation": "🤖",
};

function Logo() {
  return (
    <svg viewBox="0 0 40 40" className="logo">
      <circle cx="20" cy="20" r="18" fill="none" stroke="currentColor" strokeWidth="2.5" />
      <path d="M12 20 L28 20 M20 12 L20 28" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
      <circle cx="20" cy="20" r="6" fill="none" stroke="currentColor" strokeWidth="2" />
    </svg>
  );
}

function Spinner() {
  return <span className="spinner" />;
}

function PipelineSteps({ steps, running }) {
  if (!steps || (steps.length === 0 && !running)) return null;
  return (
    <div className="pipeline">
      {steps.map((s, i) => (
        <div key={i} className={`pipe-step ${s.status || "running"}`}>
          <span className="pipe-icon">{STEPS_ICONS[s.step] || "⚙️"}</span>
          <div className="pipe-body">
            <div className="pipe-header">
              <span className="pipe-name">{s.step}</span>
              {s.duration_ms != null && <span className="pipe-duration">{s.duration_ms}ms</span>}
              {!s.status && <Spinner />}
            </div>
            <div className="pipe-detail">{s.detail}</div>
          </div>
          {i < steps.length - 1 && <div className="pipe-arrow">↓</div>}
        </div>
      ))}
      {running && (
        <div className="pipe-step running">
          <span className="pipe-icon">⏳</span>
          <div className="pipe-body">
            <div className="pipe-header">
              <span className="pipe-name">Processing…</span>
              <Spinner />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ChunkSourceTag({ chunk }) {
  const src = chunk.source ? chunk.source.split("\\").pop().split("/").pop() : "";
  const page = chunk.page != null ? `p.${chunk.page + 1}` : "";
  return (
    <span className="chunk-meta">
      {src && <span className="chunk-file">{src}</span>}
      {page && <span className="chunk-page">{page}</span>}
    </span>
  );
}

function App() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState(null);
  const [status, setStatus] = useState({ ingested: false, chunk_count: 0 });
  const [result, setResult] = useState(null);
  const [pipelineSteps, setPipelineSteps] = useState([]);

  useEffect(() => {
    fetch(`${API}/status`)
      .then((r) => r.json())
      .then(setStatus)
      .catch(() => {});
  }, []);

  const handleIngest = async () => {
    setLoading(true);
    setMode("ingest");
    setPipelineSteps([]);
    setResult(null);
    try {
      const res = await fetch(`${API}/ingest`, { method: "POST" });
      const data = await res.json();
      setStatus({ ingested: true, chunk_count: data.chunk_count });
      setPipelineSteps(data.pipeline_steps || []);
    } catch (e) {
      alert("Ingestion failed: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setMode("query");
    setPipelineSteps([]);
    setResult(null);
    try {
      const res = await fetch(`${API}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setResult(data);
      setPipelineSteps(data.pipeline_steps || []);
    } catch (e) {
      alert("Query failed: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-row">
          <Logo />
          <div>
            <h1>RAG Explorer</h1>
            <p className="subtitle">
              End-to-end Retrieval-Augmented Generation pipeline
            </p>
          </div>
        </div>
        <div className="badge-row">
          <span className="badge badge-model">Groq · gpt-oss-120b</span>
          <span className="badge badge-embed">Nomic Embed Text v1.5</span>
          <span className="badge badge-db">ChromaDB</span>
        </div>
      </header>

      {/* ---- INGEST ---- */}
      <section className="card section-ingest">
        <div className="section-title">
          <span className="section-num">1</span>
          <h2>Ingest &amp; Index Documents</h2>
        </div>
        <p className="section-desc">
          {status.ingested
            ? `${status.chunk_count} chunks stored in ChromaDB`
            : "No data ingested yet — click below to start"}
        </p>
        <button className="btn btn-primary" onClick={handleIngest} disabled={loading}>
          {loading && mode === "ingest" ? "Ingesting…" : "Run Ingestion"}
        </button>
        {mode === "ingest" && <PipelineSteps steps={pipelineSteps} running={loading} />}
      </section>

      {/* ---- QUERY ---- */}
      <section className="card section-query">
        <div className="section-title">
          <span className="section-num">2</span>
          <h2>Ask a Question</h2>
        </div>
        <div className="query-row">
          <input
            className="input"
            placeholder='e.g. "What is VWO used for?"'
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleQuery()}
            disabled={!status.ingested || loading}
          />
          <button
            className="btn btn-secondary"
            onClick={handleQuery}
            disabled={!status.ingested || loading || !question.trim()}
          >
            {loading && mode === "query" ? "Searching…" : "Ask"}
          </button>
        </div>
        {mode === "query" && <PipelineSteps steps={pipelineSteps} running={loading} />}
      </section>

      {/* ---- ANSWER ---- */}
      {result && (
        <section className="card section-answer">
          <div className="section-title">
            <span className="section-num">3</span>
            <h2>Answer</h2>
          </div>
          <div className="answer-context-bar">
            <span className="context-label">Based on chunks</span>
            {result.chunks.map((_, i) => (
              <span key={i} className="chunk-ref-badge">#{i + 1}</span>
            ))}
          </div>
          <p className="answer-text">{result.answer}</p>
        </section>
      )}

      {/* ---- CHUNKS USED ---- */}
      {result && result.chunks && result.chunks.length > 0 && (
        <section className="card section-chunks">
          <div className="section-title">
            <span className="section-num">4</span>
            <h2>Top {result.chunks.length} Retrieved Chunks</h2>
          </div>
          <p className="section-desc">These chunks were injected into the LLM prompt as context</p>
          <div className="chunks">
            {result.chunks.map((chunk, i) => (
              <div key={i} className="chunk">
                <div className="chunk-head">
                  <span className="chunk-ref-badge chunk-ref-badge--solid">#{i + 1}</span>
                  <span className="chunk-used-label">Used as context</span>
                  <ChunkSourceTag chunk={chunk} />
                </div>
                <p>{chunk.content}</p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default App;
