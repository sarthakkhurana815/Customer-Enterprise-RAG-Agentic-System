"""LLM helper with a safe no-key fallback for initial local smoke tests."""
from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()

def get_llm():
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        return None
    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        google_api_key=key,
        temperature=0,
        retries=0,
    )


def get_embeddings():
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GEMINI_API_KEY is required to build or load the Gemini vector index.")
    return GoogleGenerativeAIEmbeddings(
        model=os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"),
        google_api_key=key,
    )
