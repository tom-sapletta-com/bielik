#!/usr/bin/env python3
"""
bielik CLI - interactive chat shell using Ollama.
Tries REST API first, falls back to `ollama` library if available.
"""

import os
import sys
import requests

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("BIELIK_MODEL", "bielik")
CHAT_ENDPOINT = OLLAMA_HOST.rstrip("/") + "/v1/chat/completions"

# try to import official ollama client
try:
    import ollama
    HAVE_OLLAMA = True
except ImportError:
    HAVE_OLLAMA = False


def send_chat(messages, model=DEFAULT_MODEL):
    """Send chat messages to Ollama via REST API or ollama lib fallback."""
    payload = {"model": model, "messages": messages, "stream": False}

    # try REST first
    try:
        resp = requests.post(CHAT_ENDPOINT, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        choice = data.get("choices", [{}])[0]
        msg = choice.get("message", {}).get("content")
        if msg:
            return msg
    except Exception as e:
        print(f"[REST API failed: {e}]")

    # fallback: official ollama library
    if HAVE_OLLAMA:
        try:
            response = ollama.chat(model=model, messages=messages)
            return response["message"]["content"]
        except Exception as e:
            return f"[OLLAMA LIB ERROR] {e}"

    return "[ERROR] No working Ollama integration (REST and lib failed)."


def main():
    print("Bielik interactive shell — Ollama client")
    print("Type ':exit' to quit.")
    messages = [{"role": "system", "content": "You are Bielik, a helpful assistant."}]
    try:
        while True:
            try:
                user = input("You: ")
            except EOFError:
                print("\nBye.")
                break
            if not user.strip():
                continue
            if user.strip() in (":exit", ":quit"):
                print("Exiting.")
                break
            messages.append({"role": "user", "content": user})
            print("Bielik is thinking...")
            resp = send_chat(messages)
            print("Bielik:", resp)
            messages.append({"role": "assistant", "content": resp})
    except KeyboardInterrupt:
        print("\nInterrupted. Bye.")
        sys.exit(0)


if __name__ == "__main__":
    main()
