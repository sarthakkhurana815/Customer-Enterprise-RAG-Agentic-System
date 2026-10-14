"""Hybrid semantic + BM25 retrieval."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from src.agents.llm import get_embeddings

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "data" / "processed" / "faiss_index"
CHUNKS = ROOT / "data" / "processed" / "chunks.json"

class HybridRetriever:
    def __init__(self) -> None:
        if not CHUNKS.exists() or not INDEX.exists():
            raise FileNotFoundError("Index missing. Run `python -m src.ingestion.build_index`.")
        raw = json.loads(CHUNKS.read_text(encoding="utf-8"))
        self.docs = [Document(page_content=x["page_content"], metadata=x["metadata"]) for x in raw]
        self.bm25 = BM25Okapi([d.page_content.lower().split() for d in self.docs])
        embeddings = get_embeddings()
        self.vectorstore = FAISS.load_local(str(INDEX), embeddings, allow_dangerous_deserialization=True)

    def search(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        semantic = self.vectorstore.similarity_search_with_score(query, k=min(k, len(self.docs)))
        sem_scores = {d.page_content: 1.0 / (1.0 + float(score)) for d, score in semantic}
        bm_scores = self.bm25.get_scores(query.lower().split())
        bm_order = sorted(range(len(self.docs)), key=lambda i: float(bm_scores[i]), reverse=True)[:k]
        combined: dict[str, tuple[Document, float]] = {}
        for d in self.docs:
            score = sem_scores.get(d.page_content, 0.0)
            if score:
                combined[d.page_content] = (d, score)
        max_bm = max(bm_scores) if len(bm_scores) else 0.0
        for i in bm_order:
            d = self.docs[i]
            lexical = float(bm_scores[i]) / max_bm if max_bm > 0 else 0.0
            prior = combined.get(d.page_content, (d, 0.0))[1]
            combined[d.page_content] = (d, prior + lexical)
        ranked = sorted(combined.values(), key=lambda x: x[1], reverse=True)[:k]
        return [{"text": d.page_content, "source": d.metadata.get("source", "unknown"),
                 "category": d.metadata.get("category", "general"),
                 "doc_id": d.metadata.get("doc_id", "unknown"), "score": round(score, 4)}
                for d, score in ranked]
