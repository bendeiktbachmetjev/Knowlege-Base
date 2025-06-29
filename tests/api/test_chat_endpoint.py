import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_bmi():
    response = client.post("/chat", json={"user_message": "Calculate BMI for 70kg and 175cm"})
    assert response.status_code == 200
    assert "22." in response.json()["response"]

def test_chat_quote():
    response = client.post("/chat", json={"user_message": "Give me a motivational quote"})
    assert response.status_code == 200
    assert "–" in response.json()["response"] or "-" in response.json()["response"]

def test_chat_retrieval():
    response = client.post("/chat", json={"user_message": "What are core values?"})
    assert response.status_code == 200
    assert "core values" in response.json()["response"].lower() or "courage" in response.json()["response"].lower() 