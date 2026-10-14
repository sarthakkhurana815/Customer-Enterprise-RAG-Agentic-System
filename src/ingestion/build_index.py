"""Build a local FAISS index and save chunks/metadata."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.agents.llm import get_embeddings

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

def load_documents() -> list[Document]:
    docs: list[Document] = []
    faq_path = RAW / "support_faqs.csv"
    if faq_path.exists():
        df = pd.read_csv(faq_path).fillna("")
        for _, row in df.iterrows():
            text = f"Question: {row['question']}\nAnswer: {row['answer']}\nCategory: {row['category']}"
            docs.append(Document(page_content=text, metadata={
                "source": str(row["source"]), "category": str(row["category"]),
                "doc_id": str(row["doc_id"]), "kind": "faq"
            }))
    policy_path = RAW / "policies.jsonl"
    if policy_path.exists():
        for line in policy_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                docs.append(Document(page_content=f"{row['title']}\n{row['content']}", metadata={
                    "source": row["source"], "category": row["category"],
                    "doc_id": row["doc_id"], "kind": "policy"
                }))
    if not docs:
        raise FileNotFoundError("No corpus found. Run: python scripts/generate_dataset.py")
    splitter = RecursiveCharacterTextSplitter(chunk_size=650, chunk_overlap=100)
    return splitter.split_documents(docs)

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    docs = load_documents()
    print(f"Loaded {len(docs)} chunks. Creating Gemini embeddings...")
    embeddings = get_embeddings()
    store = FAISS.from_documents(docs, embeddings)
    store.save_local(str(OUT / "faiss_index"))
    (OUT / "chunks.json").write_text(json.dumps([
        {"page_content": d.page_content, "metadata": d.metadata} for d in docs
    ], ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Index saved to {OUT / 'faiss_index'} and chunks.json")

if __name__ == "__main__":
    main()
