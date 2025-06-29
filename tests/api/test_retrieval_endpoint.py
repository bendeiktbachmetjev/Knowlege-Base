from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_retrieval_endpoint():
    response = client.post("/retrieval", json={"query": "What are core values?", "k": 1})
    assert response.status_code == 200
    data = response.json()
    assert "chunks" in data
    assert isinstance(data["chunks"], list)
    assert len(data["chunks"]) > 0
    assert "text" in data["chunks"][0] 