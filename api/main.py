"""
api/main.py — FastAPI server for agent-wiki-mvp

Endpoints:
    POST /ingest          — ingest raw text (optionally auto-pipeline)
    POST /ingest/pipeline — ingest + full auto-pipeline (Claude Haiku)
    GET  /search          — keyword search across all entities
    GET  /principles      — list all principles
    GET  /patterns        — list all patterns
    GET  /sessions        — list all sessions
    GET  /export/graph    — serve graph.json
    GET  /health          — health check

Run:
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow scripts imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import ingest as ing
import query as qry
from utils import load_all, exports_dir, patterns_dir, principles_dir, sessions_dir, read_json


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Agent Wiki MVP",
    description=(
        "Structured memory and retrieval system for AI-human collaboration. "
        "Converts free-form human notes into queryable Principles and Patterns."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ───────────────────────────────────────────────────────────────────
class IngestRequest(BaseModel):
    text: str
    source: str = "manual"
    language: str | None = None
    project: str | None = None


class IngestResponse(BaseModel):
    raw_id: str
    message: str


class SearchResponse(BaseModel):
    query: str
    results: list[dict]


# ── Background pipeline runner ────────────────────────────────────────────────
def _run_pipeline_bg(raw_id: str) -> None:
    """Run in background after ingest."""
    try:
        import pipeline as pip
        pip.run_pipeline(raw_id)
    except Exception as e:
        print(f"[api] Pipeline error for {raw_id}: {e}")


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "model": "claude-haiku-3-5-20241022"}


@app.post("/ingest", response_model=IngestResponse)
def ingest_only(req: IngestRequest):
    """Ingest raw text and return raw_id. Does NOT run pipeline."""
    raw_text = req.text.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="text must not be empty")
    raw_id = ing.ingest(
        raw_text=raw_text,
        source=req.source,
        language=req.language,
        project_guess=req.project,
    )
    return IngestResponse(
        raw_id=raw_id,
        message=f"Ingested. Run POST /ingest/pipeline with raw_id='{raw_id}' to process.",
    )


@app.post("/ingest/pipeline", response_model=IngestResponse)
def ingest_and_pipeline(req: IngestRequest, background_tasks: BackgroundTasks):
    """Ingest raw text and automatically run full pipeline in background."""
    raw_text = req.text.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="text must not be empty")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY not configured")

    raw_id = ing.ingest(
        raw_text=raw_text,
        source=req.source,
        language=req.language,
        project_guess=req.project,
    )
    background_tasks.add_task(_run_pipeline_bg, raw_id)
    return IngestResponse(
        raw_id=raw_id,
        message=f"Ingested. Pipeline running in background for '{raw_id}'.",
    )


@app.get("/search", response_model=SearchResponse)
def search(
    q: str,
    type: str | None = None,
    filter: str | None = None,
    top: int = 5,
):
    """
    Search the wiki. Priority: Principle > Pattern > Session.

    - **q**: natural language query (Korean or English)
    - **type**: optional — `principle`, `pattern`, or `session`
    - **filter**: optional field filter, e.g. `phase=debugging` or `type=failure`
    - **top**: number of results (default 5)
    """
    if not q.strip():
        raise HTTPException(status_code=400, detail="q must not be empty")
    results = qry.retrieve(query=q, entity_type=type, field_filter=filter, top_k=top)
    return SearchResponse(query=q, results=results)


@app.get("/principles")
def list_principles(status: str | None = None):
    """List all principles, optionally filtered by status (draft/stable/deprecated)."""
    data = load_all(principles_dir())
    if status:
        data = [p for p in data if p.get("status") == status]
    return {"count": len(data), "principles": data}


@app.get("/principles/{principle_id}")
def get_principle(principle_id: str):
    p = next((p for p in load_all(principles_dir()) if p.get("principle_id") == principle_id), None)
    if not p:
        raise HTTPException(status_code=404, detail=f"Principle not found: {principle_id}")
    return p


@app.get("/patterns")
def list_patterns(type: str | None = None):
    """List all patterns, optionally filtered by type."""
    data = load_all(patterns_dir())
    if type:
        data = [p for p in data if p.get("type") == type]
    return {"count": len(data), "patterns": data}


@app.get("/patterns/{pattern_id}")
def get_pattern(pattern_id: str):
    p = next((p for p in load_all(patterns_dir()) if p.get("pattern_id") == pattern_id), None)
    if not p:
        raise HTTPException(status_code=404, detail=f"Pattern not found: {pattern_id}")
    return p


@app.get("/sessions")
def list_sessions(phase: str | None = None, outcome_type: str | None = None):
    """List all sessions, optionally filtered by phase or outcome_type."""
    data = load_all(sessions_dir())
    if phase:
        data = [s for s in data if s.get("phase") == phase]
    if outcome_type:
        data = [s for s in data if s.get("outcome_type") == outcome_type]
    return {"count": len(data), "sessions": data}


@app.get("/sessions/{session_id}")
def get_session(session_id: str):
    s = next((s for s in load_all(sessions_dir()) if s.get("session_id") == session_id), None)
    if not s:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    return s


@app.get("/export/graph")
def get_graph():
    """Serve the entity relationship graph."""
    graph_path = exports_dir() / "graph.json"
    if not graph_path.exists():
        raise HTTPException(status_code=404, detail="graph.json not found. Run export first.")
    return read_json(graph_path)
