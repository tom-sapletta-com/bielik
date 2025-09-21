import pytest
from fastapi.testclient import TestClient
from bielik.server import app, query_ollama

client = TestClient(app)


def test_chat_endpoint(monkeypatch):
    def fake_query(messages, model="bielik"):
        return "Hello from server"

    monkeypatch.setattr("bielik.server.query_ollama", fake_query)

    response = client.post("/chat", json={"messages": [{"role": "user", "content": "hi"}]})
    assert response.status_code == 200
    assert "Hello" in response.json()["reply"]


def test_websocket(monkeypatch):
    def fake_query(messages, model="bielik"):
        return "Hello via WS"

    monkeypatch.setattr("bielik.server.query_ollama", fake_query)

    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("hi")
        data = websocket.receive_text()
        assert "WS" in data
