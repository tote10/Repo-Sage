from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ask_question():
    payload = {"question": "What is the capital of France?"}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    assert response.json() == {"question": "WHAT IS THE CAPITAL OF FRANCE?"}
def test_ask_question_empty():
    payload = {"question": ""}
    response = client.post("/ask", json=payload)
    assert response.status_code == 422  # Unprocessable Entity due to validation error