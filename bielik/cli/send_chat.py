#!/usr/bin/env python3
"""
Bielik CLI Chat Communication - Handles message sending to models.

This module provides the communication layer between the CLI and various
model backends (Ollama REST API, Ollama library, local HF models).
"""

import requests
from typing import List, Dict, Optional

from ..config import get_config, get_logger
from ..hf_models import get_model_manager, LocalLlamaRunner, HAS_LLAMA_CPP

# Try to import ollama client
try:
    import ollama
    HAVE_OLLAMA = True
except ImportError:
    HAVE_OLLAMA = False


class ChatCommunicator:
    """Handles communication with different model backends."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(__name__)
        self.model_manager = get_model_manager()
        self.chat_endpoint = self.config.CHAT_ENDPOINT
        
    def send_chat(self, messages: List[Dict], model: str = None, use_local: bool = False) -> str:
        """
        Send chat messages to Ollama or local HF model.
        
        Args:
            messages: List of message dictionaries
            model: Model name to use
            use_local: Force use of local HF model
            
        Returns:
            Assistant's response content
        """
        if model is None:
            model = self.config.BIELIK_MODEL
        
        # Use local HF model if requested and available
        if use_local or model in self.model_manager.SPEAKLEASH_MODELS:
            if HAS_LLAMA_CPP and self.model_manager.is_model_downloaded(model):
                try:
                    # Get model path
                    model_path = self.model_manager.get_model_path(model)
                    if not model_path:
                        return f"[LOCAL MODEL ERROR] Model {model} not found locally"
                    
                    # Initialize local runner
                    runner = LocalLlamaRunner(model_path)
                    response = runner.chat(messages)
                    self.logger.info(f"Local HF model response received for {model}")
                    return response
                    
                except Exception as e:
                    self.logger.error(f"Local HF model failed for {model}: {e}")
                    if not use_local:  # Fall through to Ollama if not explicitly using local
                        self.logger.info("Falling back to Ollama...")
                    else:
                        return f"[LOCAL MODEL ERROR] {e}"
            elif use_local:
                if not HAS_LLAMA_CPP:
                    return "[LOCAL MODEL ERROR] llama-cpp-python not installed"
                elif not self.model_manager.is_model_downloaded(model):
                    return f"[LOCAL MODEL ERROR] Model {model} not downloaded. Use :download {model}"
        
        # Use Ollama (REST API first, then library fallback)
        return self._send_to_ollama(messages, model)
    
    def _send_to_ollama(self, messages: List[Dict], model: str) -> str:
        """Send messages to Ollama using REST API or library fallback."""
        payload = {"model": model, "messages": messages, "stream": False}

        # Try REST API first
        try:
            resp = requests.post(self.chat_endpoint, json=payload, timeout=self.config.REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            choice = data.get("choices", [{}])[0]
            msg = choice.get("message", {}).get("content")
            if msg:
                self.logger.debug(f"REST API successful for model {model}")
                return msg
        except Exception as e:
            self.logger.warning(f"REST API failed: {e}")

        # Fallback: official ollama library
        if HAVE_OLLAMA:
            try:
                response = ollama.chat(model=model, messages=messages)
                self.logger.debug(f"Ollama library successful for model {model}")
                return response["message"]["content"]
            except Exception as e:
                self.logger.error(f"Ollama library failed: {e}")
                return f"[OLLAMA LIB ERROR] {e}"

        return "[ERROR] No working Ollama integration (REST and lib failed)."


# Global communicator instance
_communicator = None


def get_chat_communicator() -> ChatCommunicator:
    """Get or create the global chat communicator instance."""
    global _communicator
    if _communicator is None:
        _communicator = ChatCommunicator()
    return _communicator


def send_chat(messages: List[Dict], model: str = None, use_local: bool = False) -> str:
    """
    Convenience function to send chat messages.
    
    Args:
        messages: List of message dictionaries
        model: Model name to use
        use_local: Force use of local HF model
        
    Returns:
        Assistant's response content
    """
    communicator = get_chat_communicator()
    return communicator.send_chat(messages, model, use_local)
