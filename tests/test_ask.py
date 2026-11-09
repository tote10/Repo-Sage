from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ask_question():
    payload = {"question": "Where is the password verified?"}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == payload["question"]
    assert "answer" in data
    assert "citations" in data
    assert isinstance(data["citations"], list)
    assert len(data["citations"]) > 0

def test_ask_question_with_k():
    payload = {"question": "How are posts created?", "k": 3}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["citations"]) <= 3

def test_ask_question_empty():
    payload = {"question": ""}
    response = client.post("/ask", json=payload)
    assert response.status_code == 422
