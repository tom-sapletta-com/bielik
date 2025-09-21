#!/usr/bin/env python3
"""
Hugging Face model management for Bielik.
Downloads, manages, and runs SpeakLeash models directly from Hugging Face.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import logging

from huggingface_hub import hf_hub_download, list_repo_files, HfApi
from huggingface_hub.utils import HfHubHTTPError

try:
    from llama_cpp import Llama
    HAS_LLAMA_CPP = True
except ImportError:
    HAS_LLAMA_CPP = False

from .config import get_config, get_logger


@dataclass
class ModelInfo:
    """Information about a downloaded model."""
    name: str
    repo_id: str
    file_name: str
    local_path: str
    size_bytes: int
    downloaded_at: str
    model_type: str = "gguf"
    description: str = ""
    parameters: str = ""
    version: str = ""


class SpeakLeashModelManager:
    """
    Manages SpeakLeash models from Hugging Face.
    Downloads, stores, and provides access to local GGUF models.
    """
    
    # Official SpeakLeash models we support
    SPEAKLEASH_MODELS = {
        "bielik-7b-instruct-v0.1": {
            "repo_id": "SpeakLeash/bielik-7b-instruct-v0.1-gguf",
            "file_patterns": ["*.gguf"],
            "description": "Bielik 7B Instruct model optimized for Polish language",
            "parameters": "7B",
            "version": "v0.1"
        },
        "bielik-11b-v2.3-instruct": {
            "repo_id": "SpeakLeash/bielik-11b-v2.3-instruct-gguf", 
            "file_patterns": ["*.gguf"],
            "description": "Bielik 11B Instruct model v2.3 with enhanced capabilities",
            "parameters": "11B",
            "version": "v2.3"
        },
        "bielik-4.5b-v3.0-instruct": {
            "repo_id": "SpeakLeash/bielik-4.5b-v3.0-instruct-gguf",
            "file_patterns": ["*.gguf"],
            "description": "Compact Bielik 4.5B model with latest improvements",
            "parameters": "4.5B", 
            "version": "v3.0"
        }
    }
    
    def __init__(self, models_dir: Optional[str] = None):
        """
        Initialize model manager.
        
        Args:
            models_dir: Directory to store models (default: ./models)
        """
        self.config = get_config()
        self.logger = get_logger(__name__)
        
        # Setup models directory
        if models_dir:
            self.models_dir = Path(models_dir)
        else:
            self.models_dir = Path.cwd() / "models"
        
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.models_dir / "model_registry.json"
        
        # Initialize HF API
        self.hf_api = HfApi()
        
        # Load existing model registry
        self.registry = self._load_registry()
        
        self.logger.info(f"Model manager initialized with directory: {self.models_dir}")
    
    def _load_registry(self) -> Dict[str, ModelInfo]:
        """Load model registry from file."""
        if not self.registry_file.exists():
            return {}
        
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            registry = {}
            for name, info_dict in data.items():
                registry[name] = ModelInfo(**info_dict)
            
            return registry
        except Exception as e:
            self.logger.error(f"Failed to load model registry: {e}")
            return {}
    
    def _save_registry(self):
        """Save model registry to file."""
        try:
            data = {}
            for name, model_info in self.registry.items():
                data[name] = asdict(model_info)
            
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save model registry: {e}")
    
    def list_available_models(self) -> Dict[str, Dict[str, Any]]:
        """List all available SpeakLeash models."""
        return self.SPEAKLEASH_MODELS.copy()
    
    def list_downloaded_models(self) -> Dict[str, ModelInfo]:
        """List all downloaded models."""
        # Verify that files still exist
        valid_registry = {}
        for name, model_info in self.registry.items():
            if Path(model_info.local_path).exists():
                valid_registry[name] = model_info
            else:
                self.logger.warning(f"Model file missing: {model_info.local_path}")
        
        # Update registry if needed
        if len(valid_registry) != len(self.registry):
            self.registry = valid_registry
            self._save_registry()
        
        return self.registry.copy()
    
    def is_model_downloaded(self, model_name: str) -> bool:
        """Check if model is already downloaded."""
        if model_name not in self.registry:
            return False
        
        model_info = self.registry[model_name]
        return Path(model_info.local_path).exists()
    
    def get_model_files(self, repo_id: str) -> List[str]:
        """Get list of GGUF files in repository."""
        try:
            files = list_repo_files(repo_id)
            gguf_files = [f for f in files if f.endswith('.gguf')]
            return gguf_files
        except Exception as e:
            self.logger.error(f"Failed to list files for {repo_id}: {e}")
            return []
    
    def download_model(self, model_name: str, force: bool = False) -> Optional[ModelInfo]:
        """
        Download a SpeakLeash model from Hugging Face.
        
        Args:
            model_name: Name of the model to download
            force: Force re-download even if model exists
            
        Returns:
            ModelInfo if successful, None otherwise
        """
        if model_name not in self.SPEAKLEASH_MODELS:
            self.logger.error(f"Unknown model: {model_name}")
            self.logger.info(f"Available models: {list(self.SPEAKLEASH_MODELS.keys())}")
            return None
        
        if not force and self.is_model_downloaded(model_name):
            self.logger.info(f"Model {model_name} already downloaded")
            return self.registry[model_name]
        
        model_config = self.SPEAKLEASH_MODELS[model_name]
        repo_id = model_config["repo_id"]
        
        self.logger.info(f"Downloading model {model_name} from {repo_id}")
        
        try:
            # Get available GGUF files
            gguf_files = self.get_model_files(repo_id)
            if not gguf_files:
                self.logger.error(f"No GGUF files found in {repo_id}")
                return None
            
            # Choose the best GGUF file (usually the first one or q4_0 quantization)
            target_file = self._choose_best_gguf_file(gguf_files)
            
            self.logger.info(f"Downloading file: {target_file}")
            
            # Download the model file
            local_path = hf_hub_download(
                repo_id=repo_id,
                filename=target_file,
                cache_dir=str(self.models_dir),
                local_files_only=False,
                force_download=force
            )
            
            # Get file size
            file_size = Path(local_path).stat().st_size
            
            # Create model info
            model_info = ModelInfo(
                name=model_name,
                repo_id=repo_id, 
                file_name=target_file,
                local_path=local_path,
                size_bytes=file_size,
                downloaded_at=str(Path().cwd()),
                model_type="gguf",
                description=model_config.get("description", ""),
                parameters=model_config.get("parameters", ""),
                version=model_config.get("version", "")
            )
            
            # Update registry
            self.registry[model_name] = model_info
            self._save_registry()
            
            self.logger.info(f"Successfully downloaded {model_name} to {local_path}")
            self.logger.info(f"File size: {file_size / (1024*1024*1024):.2f} GB")
            
            return model_info
            
        except HfHubHTTPError as e:
            self.logger.error(f"Failed to download {model_name}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error downloading {model_name}: {e}")
            return None
    
    def _choose_best_gguf_file(self, gguf_files: List[str]) -> str:
        """Choose the best GGUF file from available options."""
        # Preference order: q4_0, q4_1, q5_0, q5_1, q8_0, f16, f32
        preferred_quantizations = ['q4_0', 'q4_1', 'q5_0', 'q5_1', 'q8_0', 'f16', 'f32']
        
        for quant in preferred_quantizations:
            for file in gguf_files:
                if quant in file.lower():
                    return file
        
        # If no preferred quantization found, return the first file
        return gguf_files[0]
    
    def delete_model(self, model_name: str) -> bool:
        """
        Delete a downloaded model.
        
        Args:
            model_name: Name of the model to delete
            
        Returns:
            True if successful, False otherwise
        """
        if model_name not in self.registry:
            self.logger.warning(f"Model {model_name} not found in registry")
            return False
        
        model_info = self.registry[model_name]
        
        try:
            # Delete the model file
            model_path = Path(model_info.local_path)
            if model_path.exists():
                model_path.unlink()
                self.logger.info(f"Deleted model file: {model_path}")
            
            # Remove from registry
            del self.registry[model_name]
            self._save_registry()
            
            self.logger.info(f"Successfully deleted model {model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete model {model_name}: {e}")
            return False
    
    def get_model_path(self, model_name: str) -> Optional[str]:
        """Get local path for a downloaded model."""
        if not self.is_model_downloaded(model_name):
            return None
        
        return self.registry[model_name].local_path
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics for downloaded models."""
        total_size = 0
        model_count = 0
        
        for model_info in self.registry.values():
            if Path(model_info.local_path).exists():
                total_size += model_info.size_bytes
                model_count += 1
        
        return {
            "total_models": model_count,
            "total_size_bytes": total_size,
            "total_size_gb": total_size / (1024**3),
            "models_directory": str(self.models_dir),
            "registry_file": str(self.registry_file)
        }


class LocalLlamaRunner:
    """
    Runs GGUF models locally using llama-cpp-python.
    Provides chat interface without requiring Ollama.
    """
    
    def __init__(self, model_path: str, **kwargs):
        """
        Initialize local Llama runner.
        
        Args:
            model_path: Path to GGUF model file
            **kwargs: Additional arguments for Llama initialization
        """
        if not HAS_LLAMA_CPP:
            raise ImportError("llama-cpp-python is required for local model execution")
        
        self.config = get_config()
        self.logger = get_logger(__name__)
        self.model_path = model_path
        
        # Default parameters
        default_params = {
            "n_ctx": 4096,  # Context length
            "n_threads": None,  # Auto-detect
            "n_gpu_layers": 0,  # CPU only by default
            "verbose": self.config.VERBOSE_OUTPUT if hasattr(self.config, 'VERBOSE_OUTPUT') else False,
        }
        
        # Merge with user params
        params = {**default_params, **kwargs}
        
        self.logger.info(f"Loading model from: {model_path}")
        self.logger.info(f"Model parameters: {params}")
        
        try:
            self.model = Llama(model_path, **params)
            self.logger.info("Model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate chat response.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response text
        """
        # Convert messages to prompt
        prompt = self._messages_to_prompt(messages)
        
        # Default generation parameters
        default_params = {
            "max_tokens": 2048,
            "temperature": 0.7,
            "top_p": 0.9,
            "echo": False,
            "stop": ["</s>", "<|im_end|>", "<|endoftext|>"]
        }
        
        # Merge with user params
        params = {**default_params, **kwargs}
        
        try:
            self.logger.debug(f"Generating response with params: {params}")
            
            result = self.model(prompt, **params)
            response = result['choices'][0]['text'].strip()
            
            self.logger.debug(f"Generated response length: {len(response)} characters")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to generate response: {e}")
            return f"[LOCAL MODEL ERROR] {e}"
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to prompt format."""
        # Simple prompt format - can be enhanced for specific models
        prompt_parts = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        # Add final prompt for assistant response
        prompt_parts.append("Assistant:")
        
        return "\n".join(prompt_parts)
    
    def __del__(self):
        """Cleanup model when object is destroyed."""
        if hasattr(self, 'model'):
            del self.model


# Global model manager instance
_model_manager: Optional[SpeakLeashModelManager] = None


def get_model_manager() -> SpeakLeashModelManager:
    """Get global model manager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = SpeakLeashModelManager()
    return _model_manager
