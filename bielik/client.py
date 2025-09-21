#!/usr/bin/env python3
"""
Bielik Python API Client - programmatic interface for using Bielik AI assistant.
"""

import os
import requests
import subprocess
import shutil
import platform
from typing import List, Dict, Optional, Union, Any
from pathlib import Path

from .hf_models import get_model_manager, LocalLlamaRunner, HAS_LLAMA_CPP
from .config import get_config, get_logger


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
            host: Ollama server host (default: http://localhost:11434)
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
        
        # Initialize model manager
        self.model_manager = get_model_manager()
        
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
    
    def set_system_prompt(self, prompt: str):
        """Set a custom system prompt and reset conversation."""
        self.system_prompt = prompt
        self.reset_conversation()
    
    def is_ollama_installed(self) -> bool:
        """Check if Ollama binary is installed."""
        return shutil.which("ollama") is not None
    
    def is_ollama_running(self) -> bool:
        """Check if Ollama server is running."""
        try:
            resp = requests.get(f"{self.host.rstrip('/')}/api/tags", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
    
    def get_installed_models(self) -> List[str]:
        """Get list of installed Ollama models."""
        try:
            resp = requests.get(f"{self.host.rstrip('/')}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return [m['name'] for m in data.get('models', [])]
        except Exception:
            pass
        return []
    
    def is_model_available(self, model_name: str = None) -> bool:
        """Check if specified model (or default) is available."""
        target_model = model_name or self.model
        models = self.get_installed_models()
        return any(target_model.lower() in model.lower() for model in models)
    
    def get_status(self) -> Dict[str, Union[bool, str, List[str]]]:
        """Get comprehensive system status."""
        return {
            "ollama_installed": self.is_ollama_installed(),
            "ollama_running": self.is_ollama_running(),
            "model_available": self.is_model_available(),
            "installed_models": self.get_installed_models(),
            "current_model": self.model,
            "ollama_host": self.host,
            "have_ollama_client": self.have_ollama
        }
    
    def install_ollama(self) -> bool:
        """Install Ollama based on the operating system."""
        system = platform.system().lower()
        
        try:
            if system == "linux":
                cmd = ["curl", "-fsSL", "https://ollama.com/install.sh"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    install_cmd = ["sh", "-c", result.stdout]
                    subprocess.run(install_cmd, check=True, timeout=300)
                    return True
                    
            elif system == "darwin":  # macOS
                if shutil.which("brew"):
                    subprocess.run(["brew", "install", "ollama"], check=True, timeout=300)
                    return True
                    
            elif system == "windows":
                # Windows requires manual installation
                return False
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception):
            pass
        
        return False
    
    def start_ollama_server(self) -> bool:
        """Start Ollama server in background."""
        try:
            if platform.system().lower() == "windows":
                subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for server to start
            import time
            time.sleep(3)
            
            return self.is_ollama_running()
        except Exception:
            return False
    
    def pull_model(self, model_name: str = None) -> bool:
        """Download and install specified model (or default)."""
        target_model = model_name or self.model
        try:
            result = subprocess.run(
                ["ollama", "pull", target_model], 
                capture_output=True, 
                text=True, 
                timeout=1800  # 30 minutes timeout
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, Exception):
            return False
    
    def ensure_setup(self, interactive: bool = False) -> bool:
        """
        Ensure all components are properly setup.
        
        Args:
            interactive: Whether to prompt user for confirmations
            
        Returns:
            True if setup is complete, False if manual intervention needed
        """
        setup_needed = False
        
        # Check Ollama installation
        if not self.is_ollama_installed():
            if interactive:
                choice = input("Ollama not installed. Install automatically? (y/N): ").strip().lower()
                if choice in ['y', 'yes']:
                    if not self.install_ollama():
                        print("Failed to install Ollama automatically.")
                        return False
                else:
                    return False
            else:
                if not self.install_ollama():
                    return False
            setup_needed = True
        
        # Check if server is running
        if not self.is_ollama_running():
            if interactive:
                choice = input("Ollama server not running. Start automatically? (y/N): ").strip().lower()
                if choice in ['y', 'yes']:
                    if not self.start_ollama_server():
                        print("Failed to start Ollama server.")
                        return False
                else:
                    return False
            else:
                if not self.start_ollama_server():
                    return False
            setup_needed = True
        
        # Check if model is available
        if not self.is_model_available():
            if interactive:
                choice = input(f"Model {self.model} not available. Download automatically? (y/N): ").strip().lower()
                if choice in ['y', 'yes']:
                    if not self.pull_model():
                        print(f"Failed to download model {self.model}.")
                        return False
                else:
                    return False
            else:
                if not self.pull_model():
                    return False
            setup_needed = True
        
        return True
    
    def _initialize_local_runner(self) -> bool:
        """Initialize local model runner if needed."""
        if self.local_runner is not None:
            return True
        
        if not HAS_LLAMA_CPP:
            self.logger.error("llama-cpp-python not available for local model execution")
            return False
        
        # Check if model is a local HF model name
        if self.model in self.model_manager.SPEAKLEASH_MODELS:
            model_path = self.model_manager.get_model_path(self.model)
            if not model_path:
                self.logger.warning(f"Model {self.model} not downloaded locally")
                return False
        else:
            # Assume it's a direct path to GGUF file
            model_path = self.model
            if not Path(model_path).exists():
                self.logger.error(f"Model file not found: {model_path}")
                return False
        
        try:
            self.logger.info(f"Initializing local runner for: {model_path}")
            self.local_runner = LocalLlamaRunner(model_path, **self.local_model_kwargs)
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize local runner: {e}")
            return False
    
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
            if self._initialize_local_runner():
                try:
                    response_content = self.local_runner.chat(request_messages)
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
    
    # Hugging Face Model Management Methods
    
    def list_available_hf_models(self) -> Dict[str, Dict[str, str]]:
        """List all available SpeakLeash models on Hugging Face."""
        return self.model_manager.list_available_models()
    
    def list_downloaded_hf_models(self) -> Dict[str, Any]:
        """List all downloaded HF models."""
        return self.model_manager.list_downloaded_models()
    
    def download_hf_model(self, model_name: str, force: bool = False) -> bool:
        """
        Download a SpeakLeash model from Hugging Face.
        
        Args:
            model_name: Name of the model to download
            force: Force re-download even if model exists
            
        Returns:
            True if successful, False otherwise
        """
        model_info = self.model_manager.download_model(model_name, force=force)
        return model_info is not None
    
    def delete_hf_model(self, model_name: str) -> bool:
        """Delete a downloaded HF model."""
        return self.model_manager.delete_model(model_name)
    
    def switch_to_hf_model(self, model_name: str, **local_kwargs) -> bool:
        """
        Switch to using a local HF model.
        
        Args:
            model_name: Name of the HF model to use
            **local_kwargs: Additional parameters for local model initialization
            
        Returns:
            True if successful, False otherwise
        """
        if not self.model_manager.is_model_downloaded(model_name):
            self.logger.warning(f"Model {model_name} not downloaded. Use download_hf_model() first.")
            return False
        
        # Clear existing local runner
        if self.local_runner:
            del self.local_runner
            self.local_runner = None
        
        # Update configuration
        self.model = model_name
        self.use_local = True
        self.local_model_kwargs = local_kwargs
        
        # Test initialization
        if self._initialize_local_runner():
            self.logger.info(f"Switched to local HF model: {model_name}")
            return True
        else:
            self.logger.error(f"Failed to switch to HF model: {model_name}")
            return False
    
    def switch_to_ollama_model(self, model_name: str, host: str = None):
        """
        Switch to using an Ollama model.
        
        Args:
            model_name: Name of the Ollama model to use
            host: Ollama server host (optional)
        """
        # Clear local runner
        if self.local_runner:
            del self.local_runner
            self.local_runner = None
        
        # Update configuration
        self.model = model_name
        self.use_local = False
        if host:
            self.host = host
            self.chat_endpoint = self.host.rstrip("/") + "/v1/chat/completions"
        
        self.logger.info(f"Switched to Ollama model: {model_name}")
    
    def get_model_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics for downloaded HF models."""
        return self.model_manager.get_storage_stats()
    
    def get_current_model_info(self) -> Dict[str, Any]:
        """Get information about the currently configured model."""
        info = {
            "model_name": self.model,
            "use_local": self.use_local,
            "ollama_host": self.host,
            "has_local_runner": self.local_runner is not None,
            "has_ollama_client": self.have_ollama
        }
        
        if self.use_local and self.model in self.model_manager.SPEAKLEASH_MODELS:
            if self.model_manager.is_model_downloaded(self.model):
                model_info = self.model_manager.registry[self.model]
                info.update({
                    "local_path": model_info.local_path,
                    "file_size_gb": model_info.size_bytes / (1024**3),
                    "model_description": model_info.description,
                    "model_parameters": model_info.parameters
                })
            else:
                info["status"] = "not_downloaded"
        
        return info
    
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
        if format == "json":
            import json
            return json.dumps(self.messages, indent=2, ensure_ascii=False)
        
        elif format == "text":
            lines = []
            for msg in self.messages:
                if msg["role"] == "system":
                    continue
                role = "Użytkownik" if msg["role"] == "user" else "Bielik"
                lines.append(f"{role}: {msg['content']}")
            return "\n\n".join(lines)
        
        elif format == "markdown":
            lines = []
            for msg in self.messages:
                if msg["role"] == "system":
                    continue
                role = "**Użytkownik**" if msg["role"] == "user" else "**Bielik**"
                lines.append(f"{role}: {msg['content']}")
            return "\n\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")


# Convenience functions for quick usage
def create_client(**kwargs) -> BielikClient:
    """Create a new Bielik client with optional configuration."""
    return BielikClient(**kwargs)


def quick_chat(message: str, model: str = None) -> str:
    """Send a quick message without managing conversation state."""
    client = BielikClient(model=model, auto_setup=True)
    return client.query(message)


def get_system_status() -> Dict:
    """Get current system status without creating a persistent client."""
    client = BielikClient(auto_setup=False)
    return client.get_status()
