from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

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

def test_index_repo_valid():
    payload = {"repo_path": "sample_repo", "force_refresh": True}
    response = client.post("/index", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "indexed"
    assert data["chunks_count"] > 0

def test_index_repo_invalid():
    payload = {"repo_path": "non_existent_folder_xyz"}
    response = client.post("/index", json=payload)
    assert response.status_code == 400
