# Customer Enterprise Capstone 2 — Agentic RAG Starter

A non-Docker starter scaffold for an Enterprise Customer Support Assistant using:
- LangGraph multi-agent workflow
- Hybrid retrieval (FAISS semantic + BM25 keyword)
- FastAPI backend (`/query`, `/health`, `/feedback`)
- Streamlit chat UI
- Pytest + Ruff + GitHub Actions CI

## Important status
This is a **starter scaffold**, not a fully production-ready system. It includes synthetic data, retrieval, graph routing, API/UI, tests, and CI checks. Configure an approved LLM provider before expecting generated answers. If no API key is configured, the app uses a clearly labelled extractive fallback based on retrieved documents so you can test the pipeline without credentials.

## 1. Setup (Windows PowerShell, VS Code)

Open this folder in VS Code. In terminal:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If installation fails on Python 3.13 because a dependency has no compatible wheel, use an IT-approved Python 3.11 or 3.12 environment. Do not bypass company device restrictions.

## 2. Generate synthetic support corpus

```powershell
python scripts\generate_dataset.py
```

This creates `data/raw/support_faqs.csv`, `data/raw/policies.jsonl`, and `data/raw/evaluation_questions.csv`. The data is synthetic and is not any real company's policy.

## 3. Build the index

Configure `GEMINI_API_KEY` as described in section 6 before building. This command sends the synthetic support corpus to Gemini for embeddings. Rebuild any existing index after changing the embedding provider or model.

```powershell
python -m src.ingestion.build_index
```

## 4. Run the API

```powershell
uvicorn src.api.main:app --reload
```

Open `http://127.0.0.1:8000/docs`. Test `POST /query`.

## 5. Run the Streamlit UI (second terminal)

Activate `.venv` there too, then:

```powershell
streamlit run src/ui/main.py
```

The UI calls the API at `http://127.0.0.1:8000`.

## 6. Configure Gemini

Copy `.env.example` to `.env` and set `GEMINI_API_KEY` to your Google AI Studio API key. `GEMINI_MODEL` controls answer generation (defaults to `gemini-3.8-flash`); `GEMINI_EMBEDDING_MODEL` controls index and query embeddings (defaults to `gemini-embedding-001`). Never put secrets in source control. Without a key, answer generation falls back to retrieved evidence, but building the index requires Gemini access.

## 7. Tests and quality checks

```powershell
pytest -q
ruff check .
```

## 8. CI

GitHub Actions runs on pushes and pull requests: dependency install, Ruff, Pytest. Docker is intentionally not included per the current implementation choice. **Assignment note:** the supplied rubric screenshots mention Docker for Section 2 and image build/publish in Section 3; omitting Docker may cost rubric marks. Confirm with the assessor if the requirement is truly optional.

## Architecture
Question -> intent agent -> hybrid RAG tool -> evidence validator -> sentiment + escalation decision -> structured response.
The starter keeps the workflow bounded and easy to run; expand planner/executor, persistent memory, feedback-driven re-index/retrieval tuning, agent traces, and baseline-vs-agentic evaluation before final submission.

## Data privacy
Use synthetic/public data only. Do not place employer-confidential documents, internal policies, customer data, credentials, or tokens in this repository.
