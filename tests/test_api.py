
from fastapi.testclient import TestClient

from app import main, rag

client = TestClient(main.app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ask_endpoint_with_fake_llm(monkeypatch):
    fake_chunks = [
        {
            "article_no": "21",
            "title": "Right to Life",
            "page": 37,
            "source": "Constitution of India",
            "text": "No person shall be deprived of life or personal liberty."
        }
    ]

    fake_llm_response = {
        "answer": "Article 21 protects life and personal liberty.",
        "confidence": "high",
        "follow_up": "Would you like an example?"
    }

    monkeypatch.setattr(
        rag,
        "semantic_search",
        lambda question, limit=4: fake_chunks
    )

    monkeypatch.setattr(
        rag,
        "ask_llm",
        lambda prompt: fake_llm_response
    )

    response = client.post(
        "/ask",
        json={"question": "Explain Article 21", "top_k": 4}
    )

    assert response.status_code == 200
    assert "Article 21" in response.json()["answer"]
    assert response.json()["confidence"] == "high"
    assert len(response.json()["sources"]) > 0


def test_ask_endpoint_rejects_empty_question():
    response = client.post(
        "/ask",
        json={"question": "   ", "top_k": 4}
    )

    assert response.status_code == 400
