#!/usr/bin/env python3
"""
Bielik Client Model Manager - Handles model management for the client.

This module provides model management functionality for the BielikClient,
including Hugging Face model operations and local model initialization.
All content has been converted to English as requested.
"""

from typing import Dict, Any, Optional
from pathlib import Path

from ..hf_models import get_model_manager, LocalLlamaRunner, HAS_LLAMA_CPP
from ..config import get_config, get_logger


class ClientModelManager:
    """Manages model operations for the BielikClient."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(__name__)
        self.hf_model_manager = get_model_manager()
        self.local_runner = None
        
    def get_available_hf_models(self) -> Dict[str, Dict[str, str]]:
        """List all available SpeakLeash models on Hugging Face."""
        return self.hf_model_manager.list_available_models()
    
    def get_downloaded_hf_models(self) -> Dict[str, Any]:
        """List all downloaded HF models."""
        return self.hf_model_manager.list_downloaded_models()
    
    def is_hf_model_downloaded(self, model_name: str) -> bool:
        """Check if a HF model is downloaded locally."""
        return self.hf_model_manager.is_model_downloaded(model_name)
    
    def download_hf_model(self, model_name: str, force: bool = False) -> bool:
        """
        Download a SpeakLeash model from Hugging Face.
        
        Args:
            model_name: Name of the model to download
            force: Force re-download even if model exists
            
        Returns:
            True if successful, False otherwise
        """
        try:
            model_info = self.hf_model_manager.download_model(model_name, force=force)
            success = model_info is not None
            if success:
                self.logger.info(f"Successfully downloaded HF model: {model_name}")
            else:
                self.logger.error(f"Failed to download HF model: {model_name}")
            return success
        except Exception as e:
            self.logger.error(f"Error downloading HF model {model_name}: {e}")
            return False
    
    def delete_hf_model(self, model_name: str) -> bool:
        """Delete a downloaded HF model."""
        try:
            success = self.hf_model_manager.delete_model(model_name)
            if success:
                self.logger.info(f"Successfully deleted HF model: {model_name}")
            else:
                self.logger.error(f"Failed to delete HF model: {model_name}")
            return success
        except Exception as e:
            self.logger.error(f"Error deleting HF model {model_name}: {e}")
            return False
    
    def initialize_local_runner(self, model_name: str, model_kwargs: Dict = None) -> bool:
        """
        Initialize local model runner if needed.
        
        Args:
            model_name: Name of the model to initialize
            model_kwargs: Additional model parameters
            
        Returns:
            True if successful, False otherwise
        """
        if self.local_runner is not None:
            return True
        
        if not HAS_LLAMA_CPP:
            self.logger.error("llama-cpp-python not available for local model execution")
            return False
        
        # Check if model is a local HF model name
        if model_name in self.hf_model_manager.SPEAKLEASH_MODELS:
            model_path = self.hf_model_manager.get_model_path(model_name)
            if not model_path:
                self.logger.warning(f"Model {model_name} not downloaded locally")
                return False
        else:
            # Assume it's a direct path to GGUF file
            model_path = model_name
            if not Path(model_path).exists():
                self.logger.error(f"Model file not found: {model_path}")
                return False
        
        try:
            self.logger.info(f"Initializing local runner for: {model_path}")
            kwargs = model_kwargs or {}
            self.local_runner = LocalLlamaRunner(model_path, **kwargs)
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize local runner: {e}")
            return False
    
    def chat_with_local_model(self, messages: list) -> str:
        """
        Send messages to local model.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Model response
        """
        if self.local_runner is None:
            raise RuntimeError("Local runner not initialized")
        
        return self.local_runner.chat(messages)
    
    def switch_to_hf_model(self, model_name: str, **local_kwargs) -> bool:
        """
        Switch to using a local HF model.
        
        Args:
            model_name: Name of the HF model to use
            **local_kwargs: Additional parameters for local model initialization
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_hf_model_downloaded(model_name):
            self.logger.warning(f"Model {model_name} not downloaded. Use download_hf_model() first.")
            return False
        
        # Clear existing local runner
        if self.local_runner:
            del self.local_runner
            self.local_runner = None
        
        # Test initialization
        if self.initialize_local_runner(model_name, local_kwargs):
            self.logger.info(f"Switched to local HF model: {model_name}")
            return True
        else:
            self.logger.error(f"Failed to switch to HF model: {model_name}")
            return False
    
    def get_model_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics for downloaded HF models."""
        try:
            return self.hf_model_manager.get_storage_stats()
        except Exception as e:
            self.logger.error(f"Error getting storage stats: {e}")
            return {"error": str(e)}
    
    def get_current_model_info(self, model_name: str, use_local: bool) -> Dict[str, Any]:
        """Get information about the currently configured model."""
        info = {
            "model_name": model_name,
            "use_local": use_local,
            "has_local_runner": self.local_runner is not None,
            "has_llama_cpp": HAS_LLAMA_CPP
        }
        
        if use_local and model_name in self.hf_model_manager.SPEAKLEASH_MODELS:
            if self.is_hf_model_downloaded(model_name):
                downloaded = self.get_downloaded_hf_models()
                if model_name in downloaded:
                    model_info = downloaded[model_name]
                    info.update({
                        "local_path": model_info.local_path,
                        "file_size_gb": model_info.size_bytes / (1024**3),
                        "model_description": self.hf_model_manager.SPEAKLEASH_MODELS[model_name].get("description"),
                        "model_parameters": self.hf_model_manager.SPEAKLEASH_MODELS[model_name].get("parameters")
                    })
            else:
                info["status"] = "not_downloaded"
        
        return info
