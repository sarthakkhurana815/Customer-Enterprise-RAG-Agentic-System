from __future__ import annotations

import csv
from datetime import UTC, datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException

from src.api.schemas import FeedbackRequest, QueryRequest
from src.graph.workflow import run_support_query

ROOT = Path(__file__).resolve().parents[2]
FEEDBACK_FILE = ROOT / "data" / "processed" / "feedback.csv"
app = FastAPI(title="Customer Support Agentic RAG", version="0.1.0",
              description="Synthetic customer-support knowledge assistant; starter scaffold.")

@app.get("/health")
def health():
    return {"status": "ok", "service": "customer-support-agentic-rag"}

@app.post("/query")
def query(request: QueryRequest):
    try:
        result = run_support_query(request.query, request.session_id or "anonymous")
        return {"session_id": request.session_id, **result}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Query failed: {exc}") from exc

@app.post("/feedback")
def feedback(request: FeedbackRequest):
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    exists = FEEDBACK_FILE.exists()
    with FEEDBACK_FILE.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "timestamp_utc", "session_id", "rating", "comment", "query"
        ])
        if not exists:
            writer.writeheader()
        writer.writerow({
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "session_id": request.session_id, "rating": request.rating,
            "comment": request.comment or "", "query": request.query or ""
        })
    return {"status": "saved", "message": "Feedback recorded for later evaluation."}
