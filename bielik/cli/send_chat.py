#!/usr/bin/env python3
"""
Bielik CLI Chat Communication - Handles message sending to local HF models.

This module provides the communication layer between the CLI and local
HuggingFace models using llama-cpp-python.
"""

from typing import List, Dict, Optional

from ..config import get_config, get_logger
from ..hf_models import get_model_manager, LocalLlamaRunner, HAS_LLAMA_CPP


class ChatCommunicator:
    """Handles communication with local HuggingFace models."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(__name__)
        self.model_manager = get_model_manager()
        self._model_cache = {}  # Cache for loaded models: {model_path: LocalLlamaRunner}
        
    def send_chat(self, messages: List[Dict], model: str = None, use_local: bool = True) -> str:
        """
        Send chat messages to local HF model.
        
        Args:
            messages: List of message dictionaries
            model: Model name to use
            use_local: Always True for local-only mode
            
        Returns:
            Assistant's response content
        """
        if model is None:
            model = self.config.BIELIK_MODEL
        
        # Check if llama-cpp-python is available
        if not HAS_LLAMA_CPP:
            return "[LOCAL MODEL ERROR] llama-cpp-python not installed. Install with: conda install -c conda-forge llama-cpp-python"
        
        # Check if model is downloaded
        if not self.model_manager.is_model_downloaded(model):
            return f"[LOCAL MODEL ERROR] Model {model} not downloaded. Use :download {model}"
        
        try:
            # Get model path
            model_path = self.model_manager.get_model_path(model)
            if not model_path:
                return f"[LOCAL MODEL ERROR] Model {model} path not found"
            
            # Check if model is already loaded in cache
            if model_path in self._model_cache:
                self.logger.debug(f"Using cached model: {model}")
                runner = self._model_cache[model_path]
            else:
                # Initialize local runner and cache it
                self.logger.info(f"Loading model into cache: {model}")
                runner = LocalLlamaRunner(model_path)
                self._model_cache[model_path] = runner
            
            response = runner.chat(messages)
            self.logger.info(f"Local HF model response received for {model}")
            return response
            
        except Exception as e:
            self.logger.error(f"Local HF model failed for {model}: {e}")
            return f"[LOCAL MODEL ERROR] {e}"
    
    def clear_model_cache(self, model: str = None):
        """
        Clear model cache to free memory.
        
        Args:
            model: Specific model to clear, or None to clear all
        """
        if model is None:
            # Clear all cached models
            self.logger.info("Clearing all cached models")
            self._model_cache.clear()
        else:
            # Clear specific model
            model_path = self.model_manager.get_model_path(model)
            if model_path and model_path in self._model_cache:
                self.logger.info(f"Clearing cached model: {model}")
                del self._model_cache[model_path]


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
