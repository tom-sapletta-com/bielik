import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from bielik.server import app as app_module, query_ollama

# Create a test app with the same routes as the main app
app = FastAPI()
app.include_router(app_module.router)

# Create a fixture for the test client
@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_chat_endpoint(client, monkeypatch):
    def fake_query(messages, model="bielik"):
        return "Hello from server"

    monkeypatch.setattr("bielik.server.query_ollama", fake_query)

    response = client.post("/chat", json={"messages": [{"role": "user", "content": "hi"}]})
    assert response.status_code == 200
    assert "Hello" in response.json()["reply"]

def test_websocket(client, monkeypatch):
    def fake_query(messages, model="bielik"):
        return "Hello via WS"

    monkeypatch.setattr("bielik.server.query_ollama", fake_query)

    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("hi")
        data = websocket.receive_text()
        assert "WS" in data
