from google.api_core.exceptions import ResourceExhausted

from src.graph import workflow


def test_generate_uses_evidence_when_gemini_quota_is_exhausted(monkeypatch):
    class QuotaLimitedModel:
        def invoke(self, prompt):
            raise ResourceExhausted("quota exceeded")

    monkeypatch.setattr(workflow, "get_llm", lambda: QuotaLimitedModel())

    result = workflow._generate({
        "query": "How long does a refund take?",
        "evidence": [{"text": "Refunds take 5 to 7 business days.", "source": "refund_policy.txt"}],
    })

    assert "Gemini quota exceeded" in result["answer"]
    assert "5 to 7 business days" in result["answer"]
    assert result["sources"] == ["refund_policy.txt"]