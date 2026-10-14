"""Reusable RAG tool called by the agent graph."""
from __future__ import annotations

from typing import Any

from langchain_core.tools import tool

from src.retrieval.hybrid import HybridRetriever

_retriever: HybridRetriever | None = None

def get_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever

@tool
def search_support_knowledge(query: str) -> list[dict[str, Any]]:
    """Search approved support FAQs and policy documents; return evidence and source metadata."""
    return get_retriever().search(query, k=5)
