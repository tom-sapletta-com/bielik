#!/usr/bin/env python3
"""
Bielik Client Utils - Utility functions for the Bielik client.

This module provides utility functions for system checks, Ollama operations,
conversation export, and other helper functionality for the BielikClient.
All content has been converted to English as requested.
"""

import os
import json
import shutil
import requests
import subprocess
import platform
from typing import Dict, Any, List, Union
from pathlib import Path

from ..config import get_config, get_logger


class ClientUtils:
    """Utility class for Bielik client operations."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(__name__)
        
    def is_ollama_installed(self) -> bool:
        """Check if Ollama is installed on the system."""
        return shutil.which("ollama") is not None
    
    def is_ollama_running(self) -> bool:
        """Check if Ollama server is running."""
        try:
            resp = requests.get(f"{self.config.OLLAMA_HOST.rstrip('/')}/api/version", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
    
    def start_ollama_server(self) -> bool:
        """Attempt to start Ollama server."""
        if not self.is_ollama_installed():
            self.logger.error("Ollama is not installed")
            return False
        
        if self.is_ollama_running():
            self.logger.info("Ollama server is already running")
            return True
        
        try:
            if platform.system() == "Windows":
                # On Windows, start Ollama in background
                subprocess.Popen(["ollama", "serve"], 
                               creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                # On Unix systems, start in background
                subprocess.Popen(["ollama", "serve"], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            
            # Wait a moment and check if it started
            import time
            time.sleep(3)
            
            if self.is_ollama_running():
                self.logger.info("Ollama server started successfully")
                return True
            else:
                self.logger.error("Ollama server failed to start")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start Ollama server: {e}")
            return False
    
    def pull_ollama_model(self, model_name: str) -> bool:
        """Pull a model in Ollama."""
        if not self.is_ollama_running():
            self.logger.error("Ollama server is not running")
            return False
        
        try:
            self.logger.info(f"Pulling Ollama model: {model_name}")
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for model download
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully pulled model: {model_name}")
                return True
            else:
                self.logger.error(f"Failed to pull model {model_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout while pulling model: {model_name}")
            return False
        except Exception as e:
            self.logger.error(f"Error pulling model {model_name}: {e}")
            return False
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a model is available in Ollama."""
        try:
            resp = requests.get(f"{self.config.OLLAMA_HOST.rstrip('/')}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                models = [model.get("name", "") for model in data.get("models", [])]
                return any(model_name in model for model in models)
            return False
        except Exception:
            return False
    
    def list_ollama_models(self) -> List[str]:
        """List all available models in Ollama."""
        try:
            resp = requests.get(f"{self.config.OLLAMA_HOST.rstrip('/')}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return [model.get("name", "") for model in data.get("models", [])]
            return []
        except Exception:
            return []
    
    def check_ollama_status(self) -> Dict[str, Any]:
        """Get comprehensive Ollama status information."""
        status = {
            "installed": self.is_ollama_installed(),
            "running": False,
            "host": self.config.OLLAMA_HOST,
            "models": [],
            "version": None
        }
        
        if status["installed"]:
            status["running"] = self.is_ollama_running()
            
            if status["running"]:
                try:
                    # Get version
                    resp = requests.get(f"{self.config.OLLAMA_HOST.rstrip('/')}/api/version", timeout=5)
                    if resp.status_code == 200:
                        status["version"] = resp.json().get("version")
                    
                    # Get models
                    status["models"] = self.list_ollama_models()
                    
                except Exception as e:
                    self.logger.error(f"Error getting Ollama status: {e}")
        
        return status
    
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
        
        # Check Ollama
        try:
            resp = requests.get(f"{self.config.OLLAMA_HOST.rstrip('/')}/api/version", timeout=5)
            connectivity["ollama"] = resp.status_code == 200
        except Exception:
            connectivity["ollama"] = False
        
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
