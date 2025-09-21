#!/usr/bin/env python3
"""
Bielik Python API Client - programmatic interface for using Bielik AI assistant.
"""

import os
import requests
import subprocess
import shutil
import platform
from typing import List, Dict, Optional, Union


class BielikClient:
    """
    Python client for interacting with Bielik AI assistant through Ollama.
    
    This class provides a programmatic interface to:
    - Check system configuration
    - Automatically setup missing components
    - Send chat messages to the Bielik model
    - Manage conversation history
    """
    
    def __init__(
        self, 
        model: str = None, 
        host: str = None,
        auto_setup: bool = True
    ):
        """
        Initialize Bielik client.
        
        Args:
            model: Model name to use (default: SpeakLeash/bielik-7b-instruct-v0.1-gguf)
            host: Ollama server host (default: http://localhost:11434)
            auto_setup: Whether to automatically setup missing components
        """
        self.model = model or os.environ.get("BIELIK_MODEL", "SpeakLeash/bielik-7b-instruct-v0.1-gguf")
        self.host = host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.chat_endpoint = self.host.rstrip("/") + "/v1/chat/completions"
        
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
        
        # Try REST API first
        payload = {"model": self.model, "messages": request_messages, "stream": False}
        
        try:
            resp = requests.post(self.chat_endpoint, json=payload, timeout=30)
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
