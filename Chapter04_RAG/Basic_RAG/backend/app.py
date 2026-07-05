import os
import glob
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_nomic import NomicEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

app = FastAPI(title="RAG Explorer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
PERSIST_DIR = BASE_DIR / "db"
DATA_DIR = BASE_DIR / "data" / "data"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    chunks: list[dict]
    pipeline_steps: list[dict]

class StatusResponse(BaseModel):
    ingested: bool
    chunk_count: int = 0
    document_count: int = 0

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _vectorstore(embedding=None):
    if embedding is None:
        embedding = NomicEmbeddings(model="nomic-embed-text-v1.5")
    return Chroma(
        persist_directory=str(PERSIST_DIR),
        embedding_function=embedding,
    )

def _count_chunks(store=None):
    if store is None:
        store = _vectorstore()
    try:
        return store._collection.count()
    except Exception:
        return 0

# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

@app.get("/api/status", response_model=StatusResponse)
def get_status():
    cc = _count_chunks()
    return StatusResponse(ingested=cc > 0, chunk_count=cc, document_count=1 if cc > 0 else 0)

# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------

@app.post("/api/ingest")
def ingest():
    steps = []
    total_start = time.time()

    # Step 1: PDF Loading
    t0 = time.time()
    pdf_files = list(glob.glob(str(DATA_DIR / "*.pdf")))
    if not pdf_files:
        raise HTTPException(400, "No PDF files found in data/data/")
    steps.append({
        "step": "PDF Loading",
        "detail": f"Found {len(pdf_files)} PDF file(s): {[Path(f).name for f in pdf_files]}",
        "duration_ms": round((time.time() - t0) * 1000),
        "status": "done",
    })

    # Step 2: Text Extraction
    t0 = time.time()
    docs = []
    for fp in pdf_files:
        loader = PyPDFLoader(fp)
        docs.extend(loader.load())
    steps.append({
        "step": "Text Extraction",
        "detail": f"Extracted {len(docs)} page(s) from PDF",
        "duration_ms": round((time.time() - t0) * 1000),
        "status": "done",
    })

    # Step 3: Chunking
    t0 = time.time()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    steps.append({
        "step": "Chunking",
        "detail": f"Split into {len(chunks)} chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})",
        "duration_ms": round((time.time() - t0) * 1000),
        "status": "done",
    })

    # Step 4: Embedding
    t0 = time.time()
    embedding = NomicEmbeddings(model="nomic-embed-text-v1.5")
    steps.append({
        "step": "Embedding",
        "detail": "Generated embeddings using Nomic Embed Text v1.5",
        "duration_ms": round((time.time() - t0) * 1000),
        "status": "done",
    })

    # Step 5: ChromaDB Storage
    t0 = time.time()
    Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=str(PERSIST_DIR),
    )
    steps.append({
        "step": "ChromaDB Storage",
        "detail": f"Stored {len(chunks)} embeddings in local ChromaDB at db/",
        "duration_ms": round((time.time() - t0) * 1000),
        "status": "done",
    })

    total_time = round((time.time() - total_start) * 1000)

    return {
        "message": f"Ingested {len(chunks)} chunks from {len(pdf_files)} document(s).",
        "chunk_count": len(chunks),
        "total_duration_ms": total_time,
        "pipeline_steps": steps,
    }

# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

PROMPT_TEMPLATE = """You are a helpful assistant. Use the retrieved context below to answer the user's question.

Context:
{context}

Question: {question}

Answer concisely based only on the context provided. If the context doesn't contain enough information, say so."""

@app.post("/api/query", response_model=QueryResponse)
def query(body: QueryRequest):
    steps = []
    total_start = time.time()

    # Step 1: Query Embedding
    t0 = time.time()
    embedding = NomicEmbeddings(model="nomic-embed-text-v1.5")
    steps.append({
        "step": "Query Embedding",
        "detail": "Embedded question using Nomic Embed Text v1.5",
        "duration_ms": round((time.time() - t0) * 1000),
        "status": "done",
    })

    # Step 2: ChromaDB Retrieval
    t0 = time.time()
    store = Chroma(
        persist_directory=str(PERSIST_DIR),
        embedding_function=embedding,
    )
    retriever = store.as_retriever(search_kwargs={"k": 4})
    retrieved = retriever.invoke(body.question)
    steps.append({
        "step": "Vector Search",
        "detail": f"Retrieved top {len(retrieved)} relevant chunks from ChromaDB",
        "duration_ms": round((time.time() - t0) * 1000),
        "status": "done",
    })

    context = "\n\n".join(d.page_content for d in retrieved)
    chunks = [
        {
            "content": d.page_content,
            "source": d.metadata.get("source", ""),
            "page": d.metadata.get("page", None),
        }
        for d in retrieved
    ]

    # Step 3: LLM Answer Generation
    t0 = time.time()
    model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    llm = ChatGroq(model=model_name, temperature=0)
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    chain = (
        RunnablePassthrough.assign(context=lambda x: context)
        | prompt
        | llm
        | StrOutputParser()
    )
    answer = chain.invoke({"question": body.question, "context": context})
    steps.append({
        "step": "LLM Answer Generation",
        "detail": f"Generated answer using Groq / {model_name}",
        "duration_ms": round((time.time() - t0) * 1000),
        "status": "done",
    })

    total_time = round((time.time() - total_start) * 1000)
    steps.append({
        "step": "Total",
        "detail": f"Completed in {total_time}ms",
        "duration_ms": total_time,
        "status": "done",
    })

    return QueryResponse(answer=answer, chunks=chunks, pipeline_steps=steps)
