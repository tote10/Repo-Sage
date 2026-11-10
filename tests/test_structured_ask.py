from fastapi.testclient import TestClient
from app.main import app
from rag.agent_turn import run_agent_round_trip, StructuredAnswer

client = TestClient(app)


def test_agent_round_trip_direct():
    res = run_agent_round_trip("show me auth.py", repo_path="./sample_repo")
    assert isinstance(res, StructuredAnswer)
    assert res.answer
    assert res.confidence > 0
    assert len(res.sources) >= 1
    assert res.sources[0].file == "auth.py"
    assert len(res.tool_calls) >= 1


def test_ask_endpoint_with_tools():
    response = client.post("/ask", json={
        "question": "show me auth.py",
        "repo_path": "./sample_repo",
        "use_tools": True
    })
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "confidence" in data
    assert "tool_calls" in data
    assert len(data["sources"]) >= 1
    assert len(data["tool_calls"]) >= 1


def test_ask_endpoint_default_returns_sources_and_confidence():
    response = client.post("/ask", json={
        "question": "how is password hashed?",
        "repo_path": "./sample_repo"
    })
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "confidence" in data
    assert len(data["citations"]) >= 1
