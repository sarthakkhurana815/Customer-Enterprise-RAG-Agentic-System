"""Bounded LangGraph support workflow with retrieval validation and escalation."""
from __future__ import annotations

from typing import Any, TypedDict

from google.api_core.exceptions import ResourceExhausted
from langgraph.graph import END, START, StateGraph

from src.agents.llm import get_llm
from src.tools.rag_tool import get_retriever


class SupportState(TypedDict, total=False):
    query: str
    session_id: str
    intent: str
    sentiment: str
    urgency: str
    evidence: list[dict[str, Any]]
    answer: str
    sources: list[str]
    confidence: float
    needs_escalation: bool
    trace: list[str]
    retry_count: int
    feedback: str

def _classify(state: SupportState) -> dict:
    q = state["query"].lower()
    if any(w in q for w in ["refund", "return", "cancel", "delivery", "order", "shipping"]):
        intent = "order_and_returns"
    elif any(w in q for w in ["password", "login", "account", "app", "technical", "error"]):
        intent = "technical_support"
    else:
        intent = "general_support"
    negative = any(w in q for w in ["angry", "furious", "terrible", "unacceptable", "complaint", "urgent", "!!!"])
    return {"intent": intent, "sentiment": "negative" if negative else "neutral",
            "urgency": "high" if negative else "normal",
            "trace": state.get("trace", []) + ["query_understanding_agent"]}

def _retrieve(state: SupportState) -> dict:
    evidence = get_retriever().search(state["query"], k=5)
    return {"evidence": evidence, "trace": state.get("trace", []) + ["rag_retrieval_agent"]}

def _validate(state: SupportState) -> dict:
    evidence = state.get("evidence", [])
    # Conservative heuristic: at least one retrieved passage must have a non-empty score and text.
    usable = [e for e in evidence if e.get("text", "").strip() and e.get("score", 0) > 0]
    confidence = min(0.95, 0.35 + 0.12 * len(usable)) if usable else 0.0
    return {"confidence": confidence, "trace": state.get("trace", []) + ["retrieval_validator"]}

def _generate(state: SupportState) -> dict:
    evidence = state.get("evidence", [])
    context = "\n\n".join(f"[{i+1}] {e['text']} (source: {e['source']})" for i, e in enumerate(evidence[:4]))
    llm = get_llm()
    if llm and context:
        prompt = (
            "You are a customer support assistant. Answer only from the evidence. "
            "If evidence does not answer the question, say so and recommend human support. "
            "Never invent company policy. Cite source filenames in the answer.\n\n"
            f"Question: {state['query']}\nEvidence:\n{context}"
        )
        try:
            response = llm.invoke(prompt)
            answer = str(response.content)
        except ResourceExhausted:
            answer = "Gemini quota exceeded; retrieved evidence for manual review:\n\n" + context
    elif context:
        # Extractive fallback is explicitly labelled, not presented as LLM generation.
        answer = "LLM not configured; retrieved evidence for manual review:\n\n" + context
    else:
        answer = "I could not find relevant evidence in the support knowledge base. Please contact human support."
    return {"answer": answer, "sources": list(dict.fromkeys(e["source"] for e in evidence)),
            "trace": state.get("trace", []) + ["answer_generation"]}

def _escalate(state: SupportState) -> dict:
    low_confidence = state.get("confidence", 0.0) < 0.45
    high_urgency = state.get("urgency") == "high"
    return {"needs_escalation": low_confidence or high_urgency,
            "trace": state.get("trace", []) + ["escalation_agent"]}

def _route(state: SupportState) -> str:
    if state.get("confidence", 0.0) < 0.45 and state.get("retry_count", 0) < 1:
        return "retry"
    return "generate"

def _rewrite_and_retry(state: SupportState) -> dict:
    # Deterministic query expansion. Retry is bounded to one extra retrieval.
    expanded = state["query"] + " policy FAQ support procedure"
    result = get_retriever().search(expanded, k=7)
    return {"query": expanded, "evidence": result, "retry_count": 1,
            "trace": state.get("trace", []) + ["feedback_retry_retrieval"]}

def build_graph():
    graph = StateGraph(SupportState)
    graph.add_node("classify", _classify)
    graph.add_node("retrieve", _retrieve)
    graph.add_node("validate", _validate)
    graph.add_node("retry", _rewrite_and_retry)
    graph.add_node("generate", _generate)
    graph.add_node("escalate", _escalate)
    graph.add_edge(START, "classify")
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", "validate")
    graph.add_conditional_edges("validate", _route, {"retry": "retry", "generate": "generate"})
    graph.add_edge("retry", "validate")
    graph.add_edge("generate", "escalate")
    graph.add_edge("escalate", END)
    return graph.compile()

_graph = None
def run_support_query(query: str, session_id: str = "default") -> dict:
    global _graph
    if _graph is None:
        _graph = build_graph()
    result = _graph.invoke({"query": query, "session_id": session_id, "trace": [], "retry_count": 0})
    return {k: result.get(k) for k in [
        "answer", "evidence", "sources", "confidence", "intent", "sentiment",
        "urgency", "needs_escalation", "trace", "retry_count"
    ]}
