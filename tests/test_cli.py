import pytest
from bielik.cli.send_chat import send_chat

class DummyResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("HTTP Error")

    def json(self):
        return self._data


def test_send_chat_rest(monkeypatch):
    """Test send_chat with mocked REST API response."""
    def fake_post(url, json, timeout):
        return DummyResponse({
            "choices": [
                {"message": {"content": "Hello from REST"}}
            ]
        })
    monkeypatch.setattr("requests.post", fake_post)

    messages = [{"role": "user", "content": "hi"}]
    reply = send_chat(messages, model="bielik")
    assert "REST" in reply or "Hello" in reply


def test_send_chat_rest_fail_then_fallback(monkeypatch):
    """Simulate REST failure, fallback to ollama lib."""
    monkeypatch.setattr("requests.post", lambda *a, **k: (_ for _ in ()).throw(Exception("REST fail")))

    # Fake ollama library
    class DummyOllama:
        def chat(self, model, messages):
            return {"message": {"content": "Hello from ollama lib"}}

    # Import the module to patch it
    from bielik.cli import send_chat as send_chat_module
    monkeypatch.setattr(send_chat_module, "HAVE_OLLAMA", True)
    monkeypatch.setattr(send_chat_module, "ollama", DummyOllama())

    messages = [{"role": "user", "content": "hi"}]
    reply = send_chat(messages, model="bielik")
    assert "ollama lib" in reply
