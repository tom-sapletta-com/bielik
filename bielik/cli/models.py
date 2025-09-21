#!/usr/bin/env python3
"""
Bielik CLI Model Manager - Handles Hugging Face model management commands.

This module provides CLI commands for downloading, managing, and switching
between SpeakLeash models from Hugging Face.
"""

from typing import Dict, Any
from pathlib import Path

from ..hf_models import get_model_manager, HAS_LLAMA_CPP
from ..config import get_config, get_logger


class ModelManager:
    """Manages CLI model operations for Hugging Face models."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(__name__)
        self.model_manager = get_model_manager()
    
    def show_models(self) -> None:
        """Display available and downloaded Hugging Face models."""
        print("\n🤗 Hugging Face Models - SpeakLeash:")
        print("=" * 50)
        
        # Show available models
        available = self.model_manager.list_available_models()
        print("📋 Available Models:")
        for model_name, info in available.items():
            status = "✅ Downloaded" if self.model_manager.is_model_downloaded(model_name) else "⬇️ Available for download"
            print(f"  {model_name}")
            print(f"    📝 {info['description']}")
            print(f"    📊 Parameters: {info['parameters']}")
            print(f"    📈 Status: {status}")
            print()
        
        # Show downloaded models
        downloaded = self.model_manager.list_downloaded_models()
        if downloaded:
            print("💾 Downloaded Models:")
            for model_name, info in downloaded.items():
                size_gb = info.size_bytes / (1024**3)
                print(f"  {model_name} ({size_gb:.1f} GB)")
                print(f"    📁 Path: {info.local_path}")
            print()
    
    def download_model(self, model_name: str) -> bool:
        """Download a Hugging Face model and return success status."""
        if model_name not in self.model_manager.SPEAKLEASH_MODELS:
            print(f"❌ Unknown model: {model_name}")
            print("💡 Use :models to see available models")
            return False
        
        if self.model_manager.is_model_downloaded(model_name):
            print(f"ℹ️  Model {model_name} is already downloaded.")
            try:
                force = input("Download again? (y/N): ").lower()
                if force not in ['y', 'yes']:
                    return False
                force_download = True
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Download cancelled")
                return False
        else:
            force_download = False
        
        print(f"⬇️ Downloading model {model_name}...")
        try:
            model_info = self.model_manager.download_model(model_name, force=force_download)
            if model_info:
                size_gb = model_info.size_bytes / (1024**3)
                print(f"✅ Model downloaded successfully! ({size_gb:.1f} GB)")
                print(f"📁 Path: {model_info.local_path}")
                return True
            else:
                print("❌ Failed to download model")
                return False
        except Exception as e:
            self.logger.error(f"Error downloading model: {e}")
            print(f"❌ Download error: {e}")
            return False
    
    def delete_model(self, model_name: str) -> None:
        """Delete a downloaded Hugging Face model."""
        if not self.model_manager.is_model_downloaded(model_name):
            print(f"❌ Model {model_name} is not downloaded")
            return
        
        # Get model info for confirmation
        downloaded = self.model_manager.list_downloaded_models()
        if model_name in downloaded:
            size_gb = downloaded[model_name].get('size_bytes', 0) / (1024**3)
            print(f"🗑️  Are you sure you want to delete model {model_name} ({size_gb:.1f} GB)?")
            try:
                confirm = input("Confirm deletion (y/N): ").lower()
                if confirm not in ['y', 'yes']:
                    print("❌ Deletion cancelled")
                    return
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Deletion cancelled")
                return
        
        try:
            if self.model_manager.delete_model(model_name):
                print(f"✅ Model {model_name} deleted successfully")
            else:
                print(f"❌ Failed to delete model {model_name}")
        except Exception as e:
            self.logger.error(f"Error deleting model: {e}")
            print(f"❌ Deletion error: {e}")
    
    def show_storage_stats(self) -> None:
        """Show storage statistics for HF models."""
        print("\n💾 Storage Statistics:")
        print("=" * 30)
        
        try:
            stats = self.model_manager.get_storage_stats()
            print(f"📊 Downloaded models: {stats['downloaded_count']}")
            print(f"💽 Total size: {stats['total_size_gb']:.1f} GB")
            print(f"📁 Models directory: {stats['models_dir']}")
            
            if stats['models']:
                print("\n📋 Model Details:")
                for model_name, info in stats['models'].items():
                    size_gb = info['size_bytes'] / (1024**3)
                    print(f"  {model_name}: {size_gb:.1f} GB")
        except Exception as e:
            self.logger.error(f"Error getting storage stats: {e}")
            print(f"❌ Error retrieving statistics: {e}")
    
    def switch_model(self, model_name: str, current_model: str) -> str:
        """
        Switch to a different model (HF or Ollama).
        
        Args:
            model_name: Name of the model to switch to
            current_model: Currently active model name
            
        Returns:
            New model name to use
        """
        # Check if it's an HF model
        if model_name in self.model_manager.SPEAKLEASH_MODELS:
            if not self.model_manager.is_model_downloaded(model_name):
                print(f"❌ Model {model_name} is not downloaded")
                print(f"💡 Use :download {model_name} to download it")
                return current_model
            
            # Allow switching even without llama-cpp-python (minimal version)
            # Local execution will be handled elsewhere with appropriate fallbacks
            print(f"🔄 Switched to HF model: {model_name}")
            if not HAS_LLAMA_CPP:
                print("💡 Note: Local execution requires: pip install 'bielik[local]'")
                print("💡 Model preference saved - will use HF API if available")
            else:
                print("💡 Model will be used for local execution")
            return model_name
            
        else:
            # Assume it's an Ollama model - we can't easily check this without setup manager
            print(f"🔄 Switched to Ollama model: {model_name}")
            print("💡 Make sure the model is installed in Ollama")
            return model_name
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        info = {
            "model_name": model_name,
            "is_hf_model": model_name in self.model_manager.SPEAKLEASH_MODELS,
            "is_downloaded": False,
            "has_llama_cpp": HAS_LLAMA_CPP
        }
        
        if info["is_hf_model"]:
            info["is_downloaded"] = self.model_manager.is_model_downloaded(model_name)
            if info["is_downloaded"]:
                downloaded = self.model_manager.list_downloaded_models()
                if model_name in downloaded:
                    model_info = downloaded[model_name]
                    info.update({
                        "local_path": model_info.local_path,
                        "size_gb": model_info.size_bytes / (1024**3),
                        "description": self.model_manager.SPEAKLEASH_MODELS[model_name]["description"],
                        "parameters": self.model_manager.SPEAKLEASH_MODELS[model_name]["parameters"]
                    })
        
        return info
    
    def get_full_model_name(self, model_name: str) -> str:
        """
        Get the full model name for Ollama usage.
        
        For HF models, this returns the model name as-is since they're used directly.
        For Ollama models, this would be the complete model identifier.
        
        Args:
            model_name: Short model name
            
        Returns:
            Full model name for usage in chat
        """
        # For HF models, return as-is
        if model_name in self.model_manager.SPEAKLEASH_MODELS:
            return model_name
        
        # For Ollama models, assume the name is already correct
        # In a more sophisticated implementation, we could validate against Ollama API
        return model_name
