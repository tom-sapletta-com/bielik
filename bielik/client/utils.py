#!/usr/bin/env python3
"""
Bielik Client Utils - Utility functions for the Bielik client.

This module provides utility functions for conversation export, system checks,
and other helper functionality for the BielikClient.
All content has been converted to English as requested.
"""

import os
import json
import requests
import platform
from typing import Dict, Any, List, Union
from pathlib import Path

from ..config import get_config, get_logger


class ClientUtils:
    """Utility class for Bielik client operations."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(__name__)
    
    def check_llama_cpp_installed(self) -> bool:
        """Check if llama-cpp-python is installed."""
        try:
            import llama_cpp
            return True
        except ImportError:
            return False
    
    def get_hf_cache_dir(self) -> Path:
        """Get HuggingFace cache directory."""
        hf_home = os.environ.get('HF_HOME')
        if hf_home:
            return Path(hf_home)
        
        cache_home = os.environ.get('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))
        return Path(cache_home) / 'huggingface'
    
    def find_local_gguf_models(self) -> List[str]:
        """Find locally downloaded GGUF models."""
        cache_dir = self.get_hf_cache_dir()
        models = []
        
        if not cache_dir.exists():
            return models
        
        # Search for GGUF files
        for path in cache_dir.rglob('*.gguf'):
            models.append(str(path))
        
        return models
    
    def export_conversation(self, messages: List[Dict[str, str]], format: str = "json") -> Union[str, Dict]:
        """
        Export conversation history in various formats.
        
        Args:
            messages: List of message dictionaries
            format: Export format ("json", "text", "markdown")
            
        Returns:
            Formatted conversation data
        """
        if format.lower() == "json":
            return {
                "conversation": messages,
                "message_count": len(messages),
                "export_format": "json"
            }
        
        elif format.lower() == "text":
            lines = []
            for msg in messages:
                role = msg.get("role", "unknown").upper()
                content = msg.get("content", "")
                if role != "SYSTEM":  # Skip system messages in text export
                    lines.append(f"{role}: {content}")
                    lines.append("")  # Empty line between messages
            return "\n".join(lines)
        
        elif format.lower() == "markdown":
            lines = ["# Bielik Conversation Export", ""]
            for msg in messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                if role == "system":
                    lines.append(f"**System Prompt:** {content}")
                elif role == "user":
                    lines.append(f"## User")
                    lines.append(content)
                elif role == "assistant":
                    lines.append(f"## Assistant")
                    lines.append(content)
                lines.append("")  # Empty line between messages
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def save_conversation(self, messages: List[Dict[str, str]], filepath: str, format: str = "json") -> bool:
        """
        Save conversation to file.
        
        Args:
            messages: List of message dictionaries
            filepath: Path to save file
            format: Export format ("json", "text", "markdown")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            content = self.export_conversation(messages, format)
            
            # Ensure directory exists
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2, ensure_ascii=False)
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            self.logger.info(f"Conversation saved to: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save conversation: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information."""
        return {
            "platform": platform.system(),
            "platform_version": platform.release(),
            "python_version": platform.python_version(),
            "architecture": platform.machine(),
            "processor": platform.processor() or "Unknown"
        }
    
    def check_network_connectivity(self) -> Dict[str, bool]:
        """Check network connectivity to various services."""
        connectivity = {}
        
        # Check Hugging Face
        try:
            resp = requests.get("https://hf.co", timeout=5)
            connectivity["huggingface"] = resp.status_code == 200
        except Exception:
            connectivity["huggingface"] = False
        
        # Check general internet
        try:
            resp = requests.get("https://httpbin.org/get", timeout=5)
            connectivity["internet"] = resp.status_code == 200
        except Exception:
            connectivity["internet"] = False
        
        return connectivity
    
    def get_model_info(self, model_path: str) -> Dict[str, Any]:
        """Get information about a local model file."""
        info = {
            "path": model_path,
            "exists": False,
            "size": None,
            "size_mb": None,
            "format": None
        }
        
        if os.path.exists(model_path):
            info["exists"] = True
            size = os.path.getsize(model_path)
            info["size"] = size
            info["size_mb"] = round(size / (1024 * 1024), 2)
            
            # Determine format from extension
            ext = Path(model_path).suffix.lower()
            if ext == '.gguf':
                info["format"] = "GGUF"
            elif ext in ['.bin', '.pt', '.pth']:
                info["format"] = "Binary Model"
            else:
                info["format"] = "Unknown"
        
        return info
    
    def validate_model_path(self, model_path: str) -> tuple[bool, str]:
        """
        Validate if a model path is usable.
        
        Returns:
            Tuple of (is_valid, message)
        """
        if not model_path:
            return False, "No model path provided"
        
        if not os.path.exists(model_path):
            return False, f"Model file not found: {model_path}"
        
        if not os.path.isfile(model_path):
            return False, f"Path is not a file: {model_path}"
        
        # Check if it's a GGUF file (preferred format)
        if not model_path.lower().endswith('.gguf'):
            return False, f"File is not a GGUF model: {model_path}"
        
        # Check file size (should be at least 1MB)
        size = os.path.getsize(model_path)
        if size < 1024 * 1024:
            return False, f"File too small to be a valid model: {size} bytes"
        
        return True, "Model path is valid"
