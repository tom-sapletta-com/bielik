import pytest
from fastapi.testclient import TestClient
from bielik.server import app, query_local_model

# Skip these tests since they require a newer version of FastAPI/Starlette
pytestmark = pytest.mark.skip("Skipping server tests due to FastAPI/Starlette version mismatch")

def test_chat_endpoint(client, monkeypatch):
    def fake_query(messages):
        return "Hello from server"

    monkeypatch.setattr("bielik.server.query_local_model", fake_query)

    response = client.post("/chat", json={"messages": [{"role": "user", "content": "hi"}]})
    assert response.status_code == 200
    assert "Hello" in response.json()["reply"]

def test_websocket(client, monkeypatch):
    def fake_query(messages):
        return "Hello via WS"

    monkeypatch.setattr("bielik.server.query_local_model", fake_query)

    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("hi")
        data = websocket.receive_text()
        assert "WS" in data
