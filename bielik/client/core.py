#!/usr/bin/env python3
"""
Bielik Client Core - Main BielikClient class with core functionality.

This module provides the main BielikClient class for local HuggingFace model execution,
conversation management, and system integration. All content has been converted to English.
"""

import os
from typing import List, Dict, Optional, Union, Any
from pathlib import Path

from .model_manager import ClientModelManager
from .utils import ClientUtils
from ..config import get_config, get_logger


class BielikClient:
    """
    Python client for interacting with Bielik AI assistant using local HuggingFace models.
    
    This class provides a programmatic interface to:
    - Check system configuration
    - Download and manage SpeakLeash models from Hugging Face
    - Execute chat messages using local GGUF models via llama-cpp-python
    - Manage conversation history
    - Export conversations in multiple formats
    """
    
    def __init__(
        self, 
        model: str = None,
        model_path: str = None,
        auto_setup: bool = True,
        model_kwargs: Dict = None
    ):
        """
        Initialize Bielik client.
        
        Args:
            model: Model name (for HuggingFace lookup)
            model_path: Direct path to local GGUF model file
            auto_setup: Whether to automatically setup missing components
            model_kwargs: Additional parameters for model initialization
        """
        self.config = get_config()
        self.logger = get_logger(__name__)
        
        self.model = model or self.config.BIELIK_MODEL
        self.model_path = model_path or os.getenv('HF_MODEL_PATH')
        self.model_kwargs = model_kwargs or {}
        
        # Initialize components
        self.model_manager = ClientModelManager()
        self.utils = ClientUtils()
        
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
        # Check if llama-cpp-python is installed
        if not self.utils.check_llama_cpp_installed():
            self.logger.error("llama-cpp-python is not installed. Install with: conda install -c conda-forge llama-cpp-python")
            return False
        
        # Check if we have a model path
        if not self.model_path:
            self.logger.warning("No model path configured. Set HF_MODEL_PATH environment variable or pass model_path parameter")
            # Try to find local models
            local_models = self.utils.find_local_gguf_models()
            if local_models:
                self.model_path = local_models[0]
                self.logger.info(f"Using found local model: {self.model_path}")
            else:
                self.logger.error("No local GGUF models found")
                return False
        
        # Validate model path
        is_valid, message = self.utils.validate_model_path(self.model_path)
        if not is_valid:
            self.logger.error(f"Invalid model path: {message}")
            return False
        
        self.logger.info(f"Setup complete. Using model: {self.model_path}")
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
        
        # Initialize and use local model
        try:
            if not self.model_manager.initialize_local_runner(self.model_path, self.model_kwargs):
                error_msg = "Failed to initialize local model runner"
                self.logger.error(error_msg)
                return f"[ERROR] {error_msg}"
            
            response_content = self.model_manager.chat_with_local_model(request_messages)
            
            if add_to_history:
                self.messages.append({"role": "user", "content": message})
                self.messages.append({"role": "assistant", "content": response_content})
            
            return response_content
            
        except ImportError as e:
            error_msg = "llama-cpp-python not installed. Install with: conda install -c conda-forge llama-cpp-python"
            self.logger.error(error_msg)
            return f"[ERROR] {error_msg}"
        except Exception as e:
            error_msg = f"Model execution failed: {e}"
            self.logger.error(error_msg)
            return f"[ERROR] {error_msg}"
    
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
    
    def save_conversation(self, filepath: str, format: str = "json") -> bool:
        """
        Save conversation to file.
        
        Args:
            filepath: Path to save file
            format: Export format ("json", "text", "markdown")
            
        Returns:
            True if successful, False otherwise
        """
        return self.utils.save_conversation(self.messages, filepath, format)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status information."""
        status = {
            "client_config": {
                "model": self.model,
                "model_path": self.model_path,
                "llama_cpp_installed": self.utils.check_llama_cpp_installed()
            },
            "system_info": self.utils.get_system_info(),
            "network": self.utils.check_network_connectivity()
        }
        
        # Add model info if path is set
        if self.model_path:
            status["model_info"] = self.utils.get_model_info(self.model_path)
        
        # List available local models
        local_models = self.utils.find_local_gguf_models()
        status["local_models_found"] = len(local_models)
        status["local_models"] = local_models[:5]  # Show first 5
        
        return status
    
    def list_local_models(self) -> List[str]:
        """List all locally available GGUF models."""
        return self.utils.find_local_gguf_models()
    
    def switch_model(self, model_path: str) -> bool:
        """
        Switch to a different local model.
        
        Args:
            model_path: Path to new model file
            
        Returns:
            True if successful, False otherwise
        """
        is_valid, message = self.utils.validate_model_path(model_path)
        if not is_valid:
            self.logger.error(f"Cannot switch to model: {message}")
            return False
        
        self.model_path = model_path
        # Clear any cached model runner
        self.model_manager.local_runner = None
        self.logger.info(f"Switched to model: {model_path}")
        return True
