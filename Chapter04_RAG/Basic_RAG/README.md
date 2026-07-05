# Basic RAG Explorer

A complete end-to-end **Retrieval-Augmented Generation (RAG)** demo application. Ingests PDF documents into a local vector store and lets you ask natural-language questions answered using retrieved context.

---

## Architecture

```
User (Browser) ←→ React Frontend (Vite, port 5174)
                         │
                   proxy /api
                         ↓
                  FastAPI Backend (uvicorn, port 8000)
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
    PyPDFLoader    ChromaDB (local)   Groq API
    (PDF parsing)  (vector store)     (LLM inference)
          │              ↑
          ↓              │
    RecursiveText    Nomic Embeddings
    Splitter         (text → vectors)
    (chunking)
```

## Pipeline

### Ingestion (`POST /api/ingest`)

1. **PDF Loading** — Finds `.pdf` files in `data/data/`
2. **Text Extraction** — Parses PDF pages via `PyPDFLoader`
3. **Chunking** — Splits text with `RecursiveCharacterTextSplitter` (chunk_size=1000, overlap=200)
4. **Embedding** — Generates vector embeddings via **Nomic Embed Text v1.5**
5. **Storage** — Persists vectors locally in ChromaDB (`db/`)

### Query (`POST /api/query`)

1. **Query Embedding** — Embeds the user's question
2. **Vector Search** — Retrieves top-4 most similar chunks from ChromaDB
3. **Answer Generation** — Uses **Groq** (`openai/gpt-oss-120b`) with a prompt template injecting the retrieved context

## Project Structure

```
Basic_RAG/
├── backend/
│   ├── app.py               # FastAPI server
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # API keys (not tracked)
│   └── .env.example         # Environment template
├── frontend/
│   ├── index.html           # Vite entry point
│   ├── package.json         # Node dependencies (React 18)
│   ├── vite.config.js       # Vite config with /api proxy
│   └── src/
│       ├── main.jsx         # React mount point
│       ├── App.jsx          # Main UI component
│       └── style.css        # Dark-theme styles
├── data/
│   └── data/                # Place PDF files here
├── db/                      # ChromaDB vector store (auto-created)
└── README.md
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- API keys for [Groq](https://console.groq.com) and [Nomic](https://atlas.nomic.ai)

### 1. Backend

```bash
cd backend
python -m pip install -r requirements.txt
```

Create `backend/.env`:

```env
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=openai/gpt-oss-120b
NOMIC_API_KEY=nk_your_key_here
```

### 2. Frontend

```bash
cd frontend
npm install
```

### 3. Run

Terminal 1 — Backend:

```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 — Frontend:

```bash
cd frontend
npm run dev
```

Open the URL shown by Vite (usually `http://localhost:5174`).

## Usage

1. Click **Ingest & Index Documents** to process PDFs from `data/data/`
2. Once ingestion completes (you'll see chunk count), type a question in the input
3. Hit submit — the UI shows the answer and the top 4 retrieved chunks

## API Endpoints

| Method | Path           | Description                                      |
|--------|----------------|--------------------------------------------------|
| GET    | `/api/status`  | Ingestion status, chunk count, doc count         |
| POST   | `/api/ingest`  | Ingest PDFs, returns pipeline steps + timing     |
| POST   | `/api/query`   | `{question}` → answer, chunks, pipeline steps    |

## Notes

- Place PDFs in `data/data/` — the app loads all PDFs found there
- ChromaDB persists to `db/` — re-ingestion is only needed for new docs
- If you add a new PDF, restart the backend and ingest again
- The UI shows real-time pipeline step timing with icons and a progress spinner
