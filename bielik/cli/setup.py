#!/usr/bin/env python3
"""
Bielik CLI Setup Manager - Handles interactive setup and system configuration.

This module provides automatic detection, installation, and configuration
of required components (Ollama, models) for first-time users.
"""

import os
import subprocess
import platform
import shutil
import time
import requests
from typing import Optional

from ..config import get_config, get_logger


class SetupManager:
    """Manages interactive setup process for first-time users."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(__name__)
        self.ollama_host = self.config.OLLAMA_HOST
        
    def is_ollama_installed(self) -> bool:
        """Check if Ollama is installed on the system."""
        return shutil.which("ollama") is not None
    
    def is_ollama_running(self) -> bool:
        """Check if Ollama server is running."""
        try:
            resp = requests.get(f"{self.ollama_host.rstrip('/')}/api/version", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
    
    def get_installed_models(self) -> list:
        """Get list of installed Ollama models."""
        try:
            resp = requests.get(f"{self.ollama_host.rstrip('/')}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return [m['name'] for m in data.get('models', [])]
        except Exception:
            pass
        return []
    
    def is_bielik_model_available(self) -> bool:
        """Check if Bielik model is available."""
        models = self.get_installed_models()
        return any('bielik' in model.lower() for model in models)
    
    def install_ollama(self) -> bool:
        """Install Ollama based on the operating system."""
        system = platform.system().lower()
        
        print("🔧 Installing Ollama...")
        
        try:
            if system == "linux":
                print("📦 Detected Linux - using curl to download Ollama...")
                cmd = ["curl", "-fsSL", "https://ollama.com/install.sh"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    # Run the install script
                    install_cmd = ["sh", "-c", result.stdout]
                    subprocess.run(install_cmd, check=True, timeout=300)
                    print("✅ Ollama installed successfully!")
                    return True
                else:
                    print(f"❌ Error downloading install script: {result.stderr}")
                    return False
                    
            elif system == "darwin":  # macOS
                print("📦 Detected macOS - checking for Homebrew...")
                if shutil.which("brew"):
                    subprocess.run(["brew", "install", "ollama"], check=True, timeout=300)
                    print("✅ Ollama installed via Homebrew!")
                    return True
                else:
                    print("❌ Homebrew not found. Please install manually from https://ollama.com")
                    return False
                    
            elif system == "windows":
                print("🪟 Detected Windows - please install Ollama manually from https://ollama.com")
                print("💡 Download the Windows installer and run it")
                return False
                
            else:
                print(f"❌ Unsupported operating system: {system}")
                print("💡 Please install Ollama manually from https://ollama.com")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Ollama installation timed out")
            return False
        except Exception as e:
            print(f"❌ Error installing Ollama: {e}")
            return False
    
    def start_ollama_server(self) -> bool:
        """Start Ollama server in background."""
        print("🚀 Starting Ollama server...")
        
        try:
            # Start Ollama server in background
            if platform.system().lower() == "windows":
                # Windows
                subprocess.Popen(["ollama", "serve"], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                # Unix-like systems
                subprocess.Popen(["ollama", "serve"], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            
            # Wait a bit for server to start
            print("⏳ Waiting for server to start...")
            for i in range(10):
                time.sleep(1)
                if self.is_ollama_running():
                    print("✅ Ollama server started successfully!")
                    return True
                print(f"   Checking... ({i+1}/10)")
            
            print("❌ Ollama server failed to start within timeout")
            return False
            
        except Exception as e:
            print(f"❌ Error starting Ollama server: {e}")
            return False
    
    def download_bielik_model(self) -> bool:
        """Download the Bielik model via Ollama."""
        model_name = self.config.BIELIK_MODEL
        print(f"📥 Downloading model: {model_name}")
        print("⏳ This may take several minutes depending on your connection...")
        
        try:
            # Use ollama pull command
            result = subprocess.run(
                ["ollama", "pull", model_name], 
                capture_output=True, 
                text=True, 
                timeout=1800  # 30 minutes timeout
            )
            
            if result.returncode == 0:
                print(f"✅ Model {model_name} downloaded successfully!")
                return True
            else:
                print(f"❌ Error downloading model: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Model download timed out (30 min limit)")
            return False
        except Exception as e:
            print(f"❌ Error downloading model: {e}")
            return False
    
    def check_system_status(self, target_model: str = None) -> str:
        """Check overall system status."""
        try:
            # Quick health check
            resp = requests.get(f"{self.ollama_host.rstrip('/')}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                models = [m['name'] for m in data.get('models', [])]
                check_model = target_model or self.config.BIELIK_MODEL
                if any(check_model.lower() in model.lower() for model in models):
                    self.logger.info(f"Ollama status check: Model {check_model} available")
                    return f"✅ Ollama running, model {check_model} available"
                else:
                    available = ', '.join(models[:3]) if models else "none"
                    self.logger.warning(f"Ollama running but model {check_model} not found")
                    return f"⚠️ Ollama running, but model '{check_model}' missing. Available: {available}"
            else:
                self.logger.error(f"Ollama HTTP error: {resp.status_code}")
                return f"❌ Ollama responds but HTTP error {resp.status_code}"
        except Exception as e:
            self.logger.error(f"Ollama connection failed: {e}")
            return f"❌ Ollama unavailable: {str(e)}"
    
    def interactive_setup(self) -> bool:
        """Interactive setup process for first-time users."""
        print("🔍 Checking system configuration...")
        print()
        
        setup_needed = False
        
        # Check Ollama installation
        if not self.is_ollama_installed():
            print("❌ Ollama is not installed")
            try:
                install_choice = input("🤔 Would you like to install Ollama automatically? (Y/n): ").strip().lower()
                if install_choice not in ['n', 'no']:
                    print()
                    if self.install_ollama():
                        setup_needed = True
                    else:
                        print("💡 Manual installation instructions:")
                        print("   1. Visit: https://ollama.com")
                        print("   2. Download and install for your OS")
                        print("   3. Restart terminal and run: bielik --setup")
                        return False
                else:
                    return False
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Setup interrupted by user")
                return False
        
        # Check if Ollama is running
        if not self.is_ollama_running():
            print("❌ Ollama server is not running")
            try:
                start_choice = input("🤔 Would you like to start Ollama server? (Y/n): ").strip().lower()
                if start_choice not in ['n', 'no']:
                    print()
                    if self.start_ollama_server():
                        setup_needed = True
                    else:
                        print("💡 Manual server start:")
                        print("   1. Open new terminal")
                        print("   2. Run: ollama serve")
                        print("   3. Keep terminal open")
                        return False
                else:
                    return False
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Setup interrupted by user")
                return False
        
        # Check if Bielik model is available
        if not self.is_bielik_model_available():
            print(f"❌ Bielik model ({self.config.BIELIK_MODEL}) is not available")
            try:
                download_choice = input("🤔 Would you like to download the Bielik model? (Y/n): ").strip().lower()
                if download_choice not in ['n', 'no']:
                    print()
                    if self.download_bielik_model():
                        setup_needed = True
                    else:
                        print(f"💡 Manual model download:")
                        print(f"   Run: ollama pull {self.config.BIELIK_MODEL}")
                        return False
                else:
                    return False
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Setup interrupted by user")
                return False
        
        if setup_needed:
            print("✅ Setup completed successfully!")
            print("🚀 You can now start chatting with Bielik!")
        else:
            print("✅ System is already properly configured!")
        
        return True
