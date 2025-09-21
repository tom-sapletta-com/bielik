#!/usr/bin/env python3
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
import os
import requests
import json

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
CHAT_ENDPOINT = OLLAMA_HOST.rstrip("/") + "/v1/chat/completions"
DEFAULT_MODEL = os.environ.get("BIELIK_MODEL", "SpeakLeash/bielik-7b-instruct-v0.1-gguf")

try:
    import ollama
    HAVE_OLLAMA = True
except ImportError:
    HAVE_OLLAMA = False

app = FastAPI(title="bielik server")


def query_ollama(messages, model=DEFAULT_MODEL):
    body = {"model": model, "messages": messages, "stream": False}
    try:
        r = requests.post(CHAT_ENDPOINT, json=body, timeout=30)
        r.raise_for_status()
        data = r.json()
        choice = data.get("choices", [{}])[0]
        return choice.get("message", {}).get("content", "")
    except Exception as e:
        if HAVE_OLLAMA:
            try:
                response = ollama.chat(model=model, messages=messages)
                return response["message"]["content"]
            except Exception as e2:
                return f"[OLLAMA LIB ERROR] {e2}"
        return f"[REST ERROR] {e}"


@app.post("/chat")
async def chat_endpoint(req: Request):
    payload = await req.json()
    model = payload.get("model", DEFAULT_MODEL)
    messages = payload.get("messages")
    if not messages:
        return JSONResponse({"error": "messages required"}, status_code=400)
    resp = query_ollama(messages, model=model)
    return {"reply": resp}


@app.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    messages = [{"role": "system", "content": "You are Bielik (WebSocket mode)."}]
    try:
        while True:
            data = await websocket.receive_text()
            try:
                obj = json.loads(data)
                if isinstance(obj, dict) and "content" in obj:
                    user_text = obj["content"]
                else:
                    user_text = str(obj)
            except Exception:
                user_text = data
            messages.append({"role": "user", "content": user_text})
            reply = query_ollama(messages)
            await websocket.send_text(reply)
            messages.append({"role": "assistant", "content": reply})
    except WebSocketDisconnect:
        return
