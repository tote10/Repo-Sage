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
    assert "sources" in data
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0
    first_source = data["sources"][0]
    assert "file" in first_source
    assert "confidence" in data
    assert isinstance(data["confidence"], (float, int))

def test_parse_structured_response_valid_json():
    from rag.ask import parse_structured_response
    sample_json = '{"answer": "Password check logic in auth.", "sources": [{"file": "auth.py", "lines": "10-20"}], "confidence": 0.9}'
    res = parse_structured_response(sample_json)
    assert res.answer == "Password check logic in auth."
    assert len(res.sources) == 1
    assert res.sources[0].file == "auth.py"
    assert res.sources[0].lines == "10-20"
    assert res.confidence == 0.9

def test_parse_structured_response_code_block():
    from rag.ask import parse_structured_response
    sample_text = '```json\n{"answer": "Here is the answer.", "sources": [{"file": "sample.py", "lines": "1-5"}], "confidence": 0.8}\n```'
    res = parse_structured_response(sample_text)
    assert res.answer == "Here is the answer."
    assert len(res.sources) == 1
    assert res.sources[0].file == "sample.py"
    assert res.confidence == 0.8

def test_parse_structured_response_fallback_prose():
    from rag.ask import parse_structured_response
    sample_text = "The password is checked in login.\nSOURCES:\n- auth/login.py:40-55"
    res = parse_structured_response(sample_text)
    assert "The password is checked in login." in res.answer
    assert len(res.sources) == 1
    assert res.sources[0].file == "auth/login.py"
    assert res.sources[0].lines == "40-55"

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
    assert data["status"] == "success"
    assert data["chunks_indexed"] > 0

def test_index_repo_invalid():
    payload = {"repo_path": "non_existent_folder_xyz"}
    response = client.post("/index", json=payload)
    assert response.status_code == 400
