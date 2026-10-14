from src.agents import llm


def test_get_llm_returns_none_without_gemini_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    assert llm.get_llm() is None


def test_get_llm_uses_gemini_configuration(monkeypatch):
    captured = {}

    def fake_chat_model(**kwargs):
        captured.update(kwargs)
        return object()

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test-model")
    monkeypatch.setattr(llm, "ChatGoogleGenerativeAI", fake_chat_model)

    result = llm.get_llm()

    assert result is not None
    assert captured == {
        "model": "gemini-test-model",
        "google_api_key": "test-key",
        "temperature": 0,
        "retries": 0,
    }


def test_get_embeddings_uses_gemini_configuration(monkeypatch):
    captured = {}

    def fake_embeddings(**kwargs):
        captured.update(kwargs)
        return object()

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_EMBEDDING_MODEL", "gemini-test-embedding")
    monkeypatch.setattr(llm, "GoogleGenerativeAIEmbeddings", fake_embeddings)

    result = llm.get_embeddings()

    assert result is not None
    assert captured == {
        "model": "gemini-test-embedding",
        "google_api_key": "test-key",
    }


def test_get_embeddings_requires_gemini_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    try:
        llm.get_embeddings()
    except RuntimeError as error:
        assert "GEMINI_API_KEY" in str(error)
    else:
        raise AssertionError("Expected get_embeddings to require GEMINI_API_KEY")