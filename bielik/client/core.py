#!/usr/bin/env python3
"""
Bielik Client Core - Main BielikClient class with core functionality.

This module provides the main BielikClient class with basic chat functionality,
conversation management, and system integration. All content has been
converted to English as requested.
"""

import os
import requests
from typing import List, Dict, Optional, Union, Any
from pathlib import Path

from .model_manager import ClientModelManager
from .utils import ClientUtils
from ..config import get_config, get_logger


class BielikClient:
    """
    Python client for interacting with Bielik AI assistant.
    Supports both Ollama integration and direct Hugging Face model execution.
    
    This class provides a programmatic interface to:
    - Check system configuration
    - Automatically setup missing components
    - Download and manage SpeakLeash models from Hugging Face
    - Send chat messages using Ollama or local models
    - Manage conversation history
    """
    
    def __init__(
        self, 
        model: str = None, 
        host: str = None,
        auto_setup: bool = True,
        use_local: bool = False,
        local_model_kwargs: Dict = None
    ):
        """
        Initialize Bielik client.
        
        Args:
            model: Model name to use (Ollama model or HF model name)
            host: Ollama server host (default from config)
            auto_setup: Whether to automatically setup missing components
            use_local: Use local HF models instead of Ollama
            local_model_kwargs: Additional parameters for local model initialization
        """
        self.config = get_config()
        self.logger = get_logger(__name__)
        
        self.model = model or self.config.BIELIK_MODEL
        self.host = host or self.config.OLLAMA_HOST
        self.chat_endpoint = self.host.rstrip("/") + "/v1/chat/completions"
        self.use_local = use_local
        self.local_model_kwargs = local_model_kwargs or {}
        
        # Initialize components
        self.model_manager = ClientModelManager()
        self.utils = ClientUtils()
        
        # Local model runner (initialized when needed)
        self.local_runner = None
        
        # Try to import ollama client
        try:
            import ollama
            self.ollama_client = ollama
            self.have_ollama = True
        except ImportError:
            self.ollama_client = None
            self.have_ollama = False
        
        # Initialize conversation history
        self.messages = []
        self.system_prompt = "You are Bielik, a helpful Polish AI assistant. Respond in Polish unless asked otherwise."
        self.reset_conversation()
        
        # Auto-setup if requested
        if auto_setup:
            self.ensure_setup()
    
    def reset_conversation(self):
        """Reset conversation history with system prompt."""
        self.messages = [{"role": "system", "content": self.system_prompt}]
        self.logger.debug("Conversation history reset")
    
    def set_system_prompt(self, prompt: str):
        """Set a new system prompt and reset conversation."""
        self.system_prompt = prompt
        self.reset_conversation()
        self.logger.info("System prompt updated")
    
    def ensure_setup(self) -> bool:
        """
        Ensure system is properly configured for operation.
        
        Returns:
            True if setup is complete, False otherwise
        """
        setup_needed = False
        
        # Check if using local model
        if self.use_local or self.model in self.model_manager.get_available_hf_models():
            if not self.model_manager.is_hf_model_downloaded(self.model):
                self.logger.info(f"Auto-downloading HF model: {self.model}")
                if self.model_manager.download_hf_model(self.model):
                    setup_needed = True
                else:
                    self.logger.error(f"Failed to download HF model: {self.model}")
                    return False
        else:
            # Check Ollama setup
            if not self.utils.is_ollama_running():
                if self.utils.is_ollama_installed():
                    self.logger.info("Ollama installed but not running")
                    if not self.utils.start_ollama_server():
                        self.logger.error("Failed to start Ollama server")
                        return False
                    setup_needed = True
                else:
                    self.logger.error("Ollama not installed")
                    return False
            
            # Check if model is available in Ollama
            if not self.utils.is_model_available(self.model):
                self.logger.info(f"Auto-pulling Ollama model: {self.model}")
                if not self.utils.pull_ollama_model(self.model):
                    self.logger.error(f"Failed to pull Ollama model: {self.model}")
                    return False
                setup_needed = True
        
        if setup_needed:
            self.logger.info("Auto-setup completed successfully")
        
        return True
    
    def send_message(self, message: str, add_to_history: bool = True) -> str:
        """
        Send a message to Bielik and get response.
        
        Args:
            message: User message to send
            add_to_history: Whether to add to conversation history
            
        Returns:
            Assistant's response
        """
        # Prepare messages for this request
        request_messages = self.messages.copy()
        request_messages.append({"role": "user", "content": message})
        
        # Use local model if requested and available
        if self.use_local:
            if self.model_manager.initialize_local_runner(self.model, self.local_model_kwargs):
                try:
                    response_content = self.model_manager.chat_with_local_model(request_messages)
                    if add_to_history:
                        self.messages.append({"role": "user", "content": message})
                        self.messages.append({"role": "assistant", "content": response_content})
                    return response_content
                except Exception as e:
                    self.logger.error(f"Local model failed: {e}")
                    # Fall through to Ollama methods
        
        # Try REST API first
        payload = {"model": self.model, "messages": request_messages, "stream": False}
        
        try:
            resp = requests.post(self.chat_endpoint, json=payload, timeout=self.config.REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            choice = data.get("choices", [{}])[0]
            response_content = choice.get("message", {}).get("content")
            if response_content:
                if add_to_history:
                    self.messages.append({"role": "user", "content": message})
                    self.messages.append({"role": "assistant", "content": response_content})
                return response_content
        except Exception as e:
            self.logger.warning(f"REST API failed: {e}")
            # Fallback to ollama client if available
            if self.have_ollama:
                try:
                    response = self.ollama_client.chat(model=self.model, messages=request_messages)
                    response_content = response["message"]["content"]
                    if add_to_history:
                        self.messages.append({"role": "user", "content": message})
                        self.messages.append({"role": "assistant", "content": response_content})
                    return response_content
                except Exception as e2:
                    self.logger.error(f"Ollama client failed: {e2}")
                    return f"[OLLAMA CLIENT ERROR] {e2}"
            return f"[REST API ERROR] {e}"
    
    def chat(self, message: str) -> str:
        """Alias for send_message with history enabled."""
        return self.send_message(message, add_to_history=True)
    
    def query(self, message: str) -> str:
        """Send a one-off query without affecting conversation history."""
        return self.send_message(message, add_to_history=False)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get current conversation history."""
        return self.messages.copy()
    
    def export_conversation(self, format: str = "json") -> Union[str, Dict]:
        """
        Export conversation history.
        
        Args:
            format: Export format ("json", "text", "markdown")
            
        Returns:
            Formatted conversation data
        """
        return self.utils.export_conversation(self.messages, format)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status information."""
        status = {
            "client_config": {
                "model": self.model,
                "use_local": self.use_local,
                "host": self.host,
                "has_ollama_client": self.have_ollama
            },
            "ollama_status": self.utils.check_ollama_status(),
            "model_info": self.model_manager.get_current_model_info(self.model, self.use_local)
        }
        return status
