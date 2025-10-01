#!/usr/bin/env python3
"""
Bielik FastAPI Server - Provides REST and WebSocket API for local HuggingFace models.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
import os
import json
from typing import List, Dict

from .config import get_config, get_logger
from .hf_models import LocalLlamaRunner

config = get_config()
logger = get_logger(__name__)

app = FastAPI(title="Bielik Server - Local HuggingFace Models")

# Model configuration
DEFAULT_MODEL_PATH = os.environ.get("HF_MODEL_PATH", "")
DEFAULT_MODEL = os.environ.get("BIELIK_MODEL", "SpeakLeash/bielik-7b-instruct-v0.1-gguf")

# Global model instance (lazy loaded)
_model_instance = None


def get_model():
    """Get or initialize the model instance."""
    global _model_instance
    
    if _model_instance is None:
        if not DEFAULT_MODEL_PATH:
            raise RuntimeError("HF_MODEL_PATH environment variable not set")
        
        try:
            _model_instance = LocalLlamaRunner(DEFAULT_MODEL_PATH)
            logger.info(f"Model loaded: {DEFAULT_MODEL_PATH}")
        except ImportError:
            raise RuntimeError("llama-cpp-python not installed. Install with: conda install -c conda-forge llama-cpp-python")
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")
    
    return _model_instance


def query_local_model(messages: List[Dict[str, str]]) -> str:
    """
    Query local HuggingFace model.
    
    Args:
        messages: List of conversation messages
        
    Returns:
        Model response text
    """
    try:
        model = get_model()
        response = model.chat(messages)
        return response
        
    except Exception as e:
        logger.error(f"Model query failed: {e}")
        return f"[ERROR] {str(e)}"


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "service": "Bielik Server",
        "version": "0.1",
        "model": DEFAULT_MODEL,
        "model_path": DEFAULT_MODEL_PATH,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        model = get_model()
        return {
            "status": "healthy",
            "model_loaded": model is not None,
            "model_path": DEFAULT_MODEL_PATH
        }
    except Exception as e:
        return JSONResponse(
            {"status": "unhealthy", "error": str(e)},
            status_code=503
        )


@app.post("/chat")
async def chat_endpoint(req: Request):
    """
    Chat endpoint for single-turn conversations.
    
    Request body:
        {
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "optional-model-name"
        }
    """
    try:
        payload = await req.json()
        messages = payload.get("messages")
        
        if not messages:
            return JSONResponse({"error": "messages required"}, status_code=400)
        
        response = query_local_model(messages)
        return {"reply": response}
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for persistent chat connections.
    
    Clients send JSON: {"content": "message text"}
    Server responds with plain text replies.
    """
    await websocket.accept()
    messages = [{"role": "system", "content": "You are Bielik, a helpful Polish AI assistant. Respond in Polish unless asked otherwise."}]
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # Parse incoming message
            try:
                obj = json.loads(data)
                if isinstance(obj, dict) and "content" in obj:
                    user_text = obj["content"]
                else:
                    user_text = str(obj)
            except Exception:
                user_text = data
            
            # Add to conversation history
            messages.append({"role": "user", "content": user_text})
            
            # Get model response
            reply = query_local_model(messages)
            
            # Send response
            await websocket.send_text(reply)
            
            # Add to conversation history
            messages.append({"role": "assistant", "content": reply})
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
