from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_query_schema_rejects_too_short_query():
    response = client.post("/query", json={"query": "x"})
    assert response.status_code == 422

def test_feedback_endpoint(tmp_path, monkeypatch):
    import src.api.main as api_main
    monkeypatch.setattr(api_main, "FEEDBACK_FILE", tmp_path / "feedback.csv")
    response = client.post("/feedback", json={
        "session_id": "test-session", "rating": 5, "comment": "Helpful", "query": "Where is my order?"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "saved"
