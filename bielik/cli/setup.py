#!/usr/bin/env python3
"""
Bielik CLI Setup Manager - Handles interactive setup and system configuration.

This module provides guidance for setting up HuggingFace models for local execution.
"""

import os
import platform
from typing import Optional, List
from pathlib import Path

from ..config import get_config, get_logger


class SetupManager:
    """Manages interactive setup process for first-time users."""
    
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
    
    def find_local_models(self) -> List[str]:
        """Find locally downloaded GGUF models."""
        cache_dir = self.get_hf_cache_dir()
        models = []
        
        if not cache_dir.exists():
            return models
        
        # Search for GGUF files
        for path in cache_dir.rglob('*.gguf'):
            models.append(str(path))
        
        return models
    
    def check_system_status(self) -> str:
        """Check overall system status."""
        status = []
        
        # Check llama-cpp-python
        if self.check_llama_cpp_installed():
            status.append("✅ llama-cpp-python is installed")
        else:
            status.append("❌ llama-cpp-python is NOT installed")
        
        # Check for local models
        models = self.find_local_models()
        if models:
            status.append(f"✅ Found {len(models)} local GGUF model(s)")
        else:
            status.append("⚠️ No local GGUF models found")
        
        return "\n".join(status)
    
    def interactive_setup(self) -> bool:
        """Interactive setup process for first-time users."""
        print("🔍 Checking system configuration for Bielik CLI...")
        print()
        
        # Check llama-cpp-python
        if not self.check_llama_cpp_installed():
            print("❌ llama-cpp-python is not installed")
            print()
            print("📦 Recommended installation method (avoids C++ compilation issues):")
            print("   conda install -c conda-forge llama-cpp-python")
            print()
            print("🚀 Alternative: Install via pip with GPU acceleration (CUDA):")
            print("   CMAKE_ARGS='-DLLAMA_CUDA=on' pip install llama-cpp-python")
            print()
            print("🍎 Alternative: Install via pip for macOS with Metal:")
            print("   CMAKE_ARGS='-DLLAMA_METAL=on' pip install llama-cpp-python")
            print()
            return False
        else:
            print("✅ llama-cpp-python is installed")
        
        # Check for local models
        models = self.find_local_models()
        print()
        if models:
            print(f"✅ Found {len(models)} local GGUF model(s):")
            for model in models[:5]:  # Show first 5
                print(f"   • {Path(model).name}")
            if len(models) > 5:
                print(f"   ... and {len(models) - 5} more")
        else:
            print("⚠️ No local GGUF models found")
            print()
            print("📥 To use Bielik, download a GGUF model from HuggingFace:")
            print()
            print("🔹 SpeakLeash Bielik models:")
            print("   https://huggingface.co/SpeakLeash")
            print()
            print("🔹 Download GGUF files and specify path with --model or HF_MODEL_PATH env var")
            print()
            print("💡 Example usage:")
            print("   export HF_MODEL_PATH='/path/to/model.gguf'")
            print("   bielik -p 'Hello!'")
            print()
        
        print()
        print("✅ Setup check completed!")
        print()
        print("📚 For more information:")
        print("   • HuggingFace models: https://huggingface.co/SpeakLeash")
        print("   • Documentation: https://github.com/tom-sapletta-com/bielik")
        print()
        
        return True
    
    def run_setup_command(self) -> None:
        """Run the :setup command - show configuration guidance."""
        print("\n" + "="*60)
        print("🔧 BIELIK CLI SETUP GUIDE")
        print("="*60 + "\n")
        
        print("📚 Bielik CLI uses local HuggingFace models via llama-cpp-python")
        print()
        
        # Show system status
        print(self.check_system_status())
        print()
        
        print("="*60)
        print("📖 CONFIGURATION OPTIONS")
        print("="*60)
        print()
        print("1️⃣ Set model path via environment variable:")
        print("   export HF_MODEL_PATH='/path/to/your/model.gguf'")
        print()
        print("2️⃣ Or specify model when running:")
        print("   bielik --model /path/to/model.gguf -p 'Your prompt'")
        print()
        print("3️⃣ Configure in .env file:")
        print("   HF_MODEL_PATH=/path/to/model.gguf")
        print()
        
        print("="*60)
        print("🌟 RECOMMENDED MODELS")
        print("="*60)
        print()
        print("• SpeakLeash Bielik 7B (GGUF)")
        print("  https://huggingface.co/SpeakLeash/bielik-7b-instruct-v0.1-gguf")
        print()
        print("• SpeakLeash Bielik 11B (GGUF)")
        print("  https://huggingface.co/SpeakLeash/bielik-11b-v2.2-gguf")
        print()
        
        print("="*60)
        print("🚀 QUICK START")
        print("="*60)
        print()
        print("1. Download a GGUF model from HuggingFace")
        print("2. Set HF_MODEL_PATH environment variable")
        print("3. Run: bielik -p 'Hello, Bielik!'")
        print()
