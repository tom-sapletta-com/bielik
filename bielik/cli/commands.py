#!/usr/bin/env python3
"""
Bielik CLI Command Processor - Handles CLI command parsing and execution.

This module processes user commands in the interactive CLI interface,
including special commands like :help, :status, :models, etc.
"""

import json
import os
from typing import List, Dict, Optional, Tuple
from huggingface_hub import snapshot_download
from .setup import SetupManager
from .models import ModelManager
from .settings import get_cli_settings
from .command_api import get_command_registry
from ..config import get_config, get_logger


class CommandProcessor:
    """Processes and executes CLI commands."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(__name__)
        self.setup_manager = SetupManager()
        self.model_manager = ModelManager()
        self.settings = get_cli_settings()
        
        # Initialize dynamic command registry
        self.command_registry = get_command_registry()
        
    def show_welcome(self) -> None:
        """Display welcome message and help for beginners."""
        assistant_name = self.settings.get_assistant_name()
        user_name = self.settings.get_user_name()
        
        print("🦅 " + "="*50)
        print(f"   {assistant_name.upper()} - Polish AI Assistant")
        print("   Powered by HuggingFace + SpeakLeash")
        print("="*53)
        print()
        print(f"👋 Welcome {user_name}!")
        print()
        print("📋 Built-in Commands:")
        print("  :help    - show this help")
        print("  :setup   - show HF model setup information")
        print("  :clear   - clear conversation history")
        print("  :models  - show available HF models")
        print("  :download <model> - download HF model (auto-switches)")
        print("  :delete <model>   - delete downloaded model")
        print("  :switch <model>   - switch to model")
        print("  :model <model>    - switch to model (alias for :switch)")
        print("  :storage - show storage statistics")
        print("  :name <name>      - change your display name")
        print("  :settings         - show current settings")
        print("  :download-bielik  - download Polish Bielik models from HuggingFace")
        print("  :exit    - end session")
        print("  Ctrl+C   - quick exit")
        
        # Show dynamic commands separated by type
        dynamic_commands = self.command_registry.list_commands()
        if dynamic_commands:
            direct_commands = []
            context_providers = []
            
            # Separate commands by type
            for cmd_name in sorted(dynamic_commands):
                cmd = self.command_registry.get_command(cmd_name)
                if cmd:
                    if getattr(cmd, 'is_context_provider', False):
                        context_providers.append((cmd_name, cmd.description))
                    else:
                        direct_commands.append((cmd_name, cmd.description))
            
            # Show direct extension commands
            if direct_commands:
                print()
                print("🔧 Extension Commands:")
                for cmd_name, description in direct_commands:
                    print(f"  :{cmd_name}  - {description}")
                print("  Use ':<command> help' for detailed help on any extension command")
            
            # Show context provider commands
            if context_providers:
                print()
                print("📊 Context Providers:")
                for cmd_name, description in context_providers:
                    print(f"  {cmd_name}:  - {description}")
                print("  These commands provide context for AI analysis.")
                print("  Example: folder: ~/documents → then ask AI questions about the directory")
        print()
        print("💡 Tips:")
        print("  • Write in Polish - AI understands Polish!")
        print("  • Ask questions, request help, chat naturally")
        print("  • Include image/folder paths for automatic analysis")
        print("  • Local HF models provide fast, private AI responses")
        print()
    
    def process_command(self, command: str, messages: List[Dict], current_model: str) -> Tuple[bool, Optional[str], List[Dict]]:
        """
        Process a special command.
        
        Args:
            command: The command string (starting with :)
            messages: Current conversation messages
            current_model: Currently active model
            
        Returns:
            Tuple of (continue_chat, new_model, updated_messages)
            - continue_chat: False if should exit, True to continue
            - new_model: New model name if changed, None if no change
            - updated_messages: Updated message list (e.g., cleared)
        """
        command = command.strip()
        
        # Exit commands
        if command in [":exit", ":quit", ":q"]:
            print("👋 Goodbye!")
            return False, None, messages
        
        # Help command
        elif command == ":help":
            self.show_welcome()
            return True, None, messages
        
        # Clear command
        elif command == ":clear":
            system_prompt = ("You are Bielik, a helpful Polish AI assistant. "
                           "Respond in Polish unless asked otherwise.")
            new_messages = [{"role": "system", "content": system_prompt}]
            print("🧹 Conversation history cleared.")
            return True, None, new_messages
        
        # Setup command - show HF model setup information
        elif command == ":setup":
            print("🔧 HuggingFace Model Setup Information:")
            print()
            print("📦 Available SpeakLeash Models:")
            print("  • bielik-7b-instruct")
            print("  • bielik-4.5b-v3.0-instruct")
            print()
            print("💡 How to get started:")
            print("  1. Download a model: :download bielik-4.5b-v3.0-instruct")
            print("  2. Switch to model: :switch bielik-4.5b-v3.0-instruct")
            print("  3. Start chatting!")
            print()
            print("🔍 Check current status:")
            print("  • :models - show available models")
            print("  • :storage - show storage usage")
            print("  • :settings - show current configuration")
            print()
            # Check current setup
            from ..hf_models import HAS_LLAMA_CPP, get_model_manager
            hf_manager = get_model_manager()
            
            if not HAS_LLAMA_CPP:
                print("❌ llama-cpp-python not installed")
                print("💡 Install with: conda install -c conda-forge llama-cpp-python")
            else:
                print("✅ llama-cpp-python is available")
                
            downloaded = hf_manager.list_downloaded_models()
            if downloaded:
                print(f"✅ {len(downloaded)} model(s) downloaded")
            else:
                print("⚠️  No models downloaded yet")
            print()
            return True, None, messages
        
        # Models command
        elif command == ":models":
            self.model_manager.show_models()
            return True, None, messages
        
        # Download command with auto-switch
        elif command.startswith(":download"):
            parts = command.split(None, 1)
            if len(parts) > 1:
                model_name = parts[1]
                success = self.model_manager.download_model(model_name)
                
                # Auto-switch to downloaded model if enabled and download was successful
                if success and self.settings.should_auto_switch_after_download():
                    print(f"🔄 Auto-switching to downloaded model: {model_name}")
                    new_model = self.model_manager.get_full_model_name(model_name)
                    if new_model:
                        self.settings.set_current_model(new_model)
                        print(f"✅ Switched to model: {self.settings.get_assistant_name()}")
                        return True, new_model, messages
                    else:
                        print("⚠️ Could not determine full model name for auto-switch")
                
            else:
                print("❓ Usage: :download <model_name>")
            return True, None, messages
        
        # Delete command
        elif command.startswith(":delete"):
            parts = command.split(None, 1)
            if len(parts) > 1:
                self.model_manager.delete_model(parts[1])
            else:
                print("❓ Usage: :delete <model_name>")
            return True, None, messages
        
        # Storage command
        elif command == ":storage":
            self.model_manager.show_storage_stats()
            return True, None, messages
        
        # Switch command (and :model alias)
        elif command.startswith(":switch") or command.startswith(":model"):
            parts = command.split(None, 1)
            if len(parts) > 1:
                new_model = self.model_manager.switch_model(parts[1], current_model)
                if new_model:
                    # Update settings with new model
                    self.settings.set_current_model(new_model)
                    print(f"✅ Assistant name updated to: {self.settings.get_assistant_name()}")
                return True, new_model, messages
            else:
                cmd_name = ":switch" if command.startswith(":switch") else ":model"
                print(f"❓ Usage: {cmd_name} <model_name>")
                return True, None, messages
        
        # Name command - change user display name
        elif command.startswith(":name"):
            parts = command.split(None, 1)
            if len(parts) > 1:
                new_name = parts[1]
                if self.settings.set_user_name(new_name):
                    print(f"✅ Your display name changed to: {self.settings.get_user_name()}")
                else:
                    print("❌ Could not change display name")
            else:
                print("❓ Usage: :name <your_name>")
                print(f"Current name: {self.settings.get_user_name()}")
            return True, None, messages
        
        # Settings command - show current settings
        elif command == ":settings":
            settings = self.settings.get_settings_summary()
            print("⚙️ Current CLI Settings:")
            print(f"  👤 User name: {settings['user_name']}")
            print(f"  🤖 Assistant name: {settings['assistant_name']}")
            print(f"  📦 Current model: {settings['current_model'] or 'Default'}")
            print(f"  🔄 Auto-switch after download: {settings['auto_switch']}")
            print(f"  📄 Settings file: {settings['env_file_path']}")
            print(f"  💾 File exists: {'✅' if settings['env_file_exists'] else '❌'}")
            return True, None, messages
        
        # Download Bielik models command
        elif command.startswith(":download-bielik"):
            parts = command.split(None, 1)
            if len(parts) > 1:
                model_identifier = parts[1]
                return self._handle_bielik_download(model_identifier, current_model)
            else:
                self._show_bielik_models()
                return True, None, messages
        
        # Check for dynamic/extension commands
        else:
            # Handle both formats: :command and command:
            is_context_provider = self._is_context_provider_command(command)
            
            if is_context_provider:
                # Context provider format: "folder: ~/documents"
                return self._handle_context_provider(command, current_model, messages)
            else:
                # Direct command format: ":calc 2+3"
                return self._handle_direct_command(command, current_model, messages)
            
    def _handle_context_provider(self, command: str, current_model: str, messages: list) -> tuple:
        """Handle context provider commands (format: 'name: args')."""
        try:
            # Parse command: "folder: ~/documents" 
            parts = command.split(':', 1)
            cmd_name = parts[0].strip()
            cmd_args = parts[1].strip() if len(parts) > 1 else ""
            
            # Get the command from registry
            dynamic_command = self.command_registry.get_command(cmd_name)
            if not dynamic_command:
                print(f"❌ Unknown context provider command: {cmd_name}")
                return True, None, messages
            
            # Prepare context for dynamic command
            context = {
                'current_model': current_model,
                'messages': messages,
                'settings': self.settings,
                'config': self.config
            }
            
            # Build args array: ['folder:', '~/documents']
            args = [f"{cmd_name}:", cmd_args] if cmd_args else [f"{cmd_name}:"]
            
            # Get the command instance to call provide_context directly for display
            command_instance = self.command_registry.get_command(cmd_name)
            if command_instance and hasattr(command_instance, 'provide_context'):
                # Get raw dict data for display formatting
                raw_context_data = command_instance.provide_context(args, context)
                
                print(f"🔍 Context generated from {cmd_name}: command")
                
                # Display context provider results to user using raw dict
                self._display_context_provider_result(cmd_name, raw_context_data)
                
                # Execute command normally for AI formatted string
                result = self.command_registry.execute_command(cmd_name, args, context)
                
                # ✅ FIX: Return True to continue chat, context data for interactive loop
                return True, result, messages
            else:
                # Fallback to normal execution if command doesn't have provide_context
                result = self.command_registry.execute_command(cmd_name, args, context)
                
                if result and not result.startswith("❌"):
                    print(f"🔍 Context generated from {cmd_name}: command")
                    
                    # Display context provider results to user
                    self._display_context_provider_result(cmd_name, result)
                    
                    # ✅ FIX: Return True to continue chat, context data for interactive loop
                    return True, result, messages
                else:
                    print(f"❌ No context generated: {result}")
                    return True, None, messages
                
        except Exception as e:
            print(f"❌ Context provider command failed: {e}")
            return True, None, messages
    
    def _display_context_provider_result(self, cmd_name: str, result):
        """Display context provider results to user in a friendly format."""
        try:
            if cmd_name == "folder" and isinstance(result, dict):
                self._display_folder_result(result)
            elif cmd_name == "calc" and isinstance(result, dict):
                self._display_calc_result(result)
            elif cmd_name == "pdf" and isinstance(result, dict):
                self._display_pdf_result(result)
            else:
                # Generic display for other context providers
                print(f"📋 Results from {cmd_name}:")
                if isinstance(result, dict) and 'analysis' in result:
                    print(f"   {result.get('summary', 'Context data generated')}")
                elif isinstance(result, str):
                    print(f"   {result[:200]}{'...' if len(result) > 200 else ''}")
                else:
                    print(f"   {str(result)[:200]}{'...' if len(str(result)) > 200 else ''}")
        except Exception as e:
            # Don't break if display fails - just show generic message  
            print(f"📋 Context data generated (display error: {str(e)[:50]})")
    
    def _display_folder_result(self, result: dict):
        """Display folder analysis results to user."""
        if 'error' in result:
            print(f"❌ {result['error']}")
            return
        
        dir_path = result.get('directory_path', 'Unknown path')
        analysis = result.get('analysis', {})
        
        print(f"📁 Folder analysis: {dir_path}")
        
        if 'summary' in analysis:
            summary = analysis['summary']
            print(f"   📊 {summary.get('total_files', 0)} files, {summary.get('total_folders', 0)} folders")
            if summary.get('total_size_mb', 0) > 0:
                print(f"   💾 Total size: {summary['total_size_mb']} MB")
        
        # Show first few files
        files = analysis.get('files', [])
        if files:
            print(f"   📄 Files ({len(files)} shown):")
            for file_info in files[:8]:  # Show first 8 files
                size_kb = round(file_info.get('size', 0) / 1024, 1)
                print(f"      • {file_info['name']} ({size_kb} KB)")
            if len(files) > 8:
                print(f"      ... and {len(files) - 8} more files")
        
        # Show first few folders
        folders = analysis.get('folders', [])
        if folders:
            print(f"   📂 Folders ({len(folders)} shown):")
            for folder_info in folders[:6]:  # Show first 6 folders
                count = folder_info.get('item_count', '?')
                print(f"      • {folder_info['name']}/ ({count} items)")
            if len(folders) > 6:
                print(f"      ... and {len(folders) - 6} more folders")
    
    def _display_calc_result(self, result: dict):
        """Display calculator results to user."""
        if 'error' in result:
            print(f"❌ {result['error']}")
        elif 'result' in result:
            print(f"🧮 Calculation result: {result['result']}")
        else:
            print("🧮 Calculation completed")
    
    def _display_pdf_result(self, result: dict):
        """Display PDF analysis results to user."""
        if 'error' in result:
            print(f"❌ {result['error']}")
        elif 'text' in result:
            text = result['text']
            print(f"📄 PDF content extracted ({len(text)} characters)")
            if len(text) > 300:
                print(f"   Preview: {text[:300]}...")
            else:
                print(f"   Content: {text}")
        else:
            print("📄 PDF processed successfully")
    
    def _handle_direct_command(self, command: str, current_model: str, messages: list) -> tuple:
        """Handle direct extension commands (format: ':command args')."""
        try:
            # Extract command name (remove ':' prefix)
            cmd_name = command.split()[0][1:] if command.startswith(':') else command.split()[0]
            
            # Try to execute dynamic command
            dynamic_command = self.command_registry.get_command(cmd_name)
            if dynamic_command:
                # Prepare context for dynamic command
                context = {
                    'current_model': current_model,
                    'messages': messages,
                    'settings': self.settings,
                    'config': self.config
                }
                
                # Parse command arguments
                args = command.split() if command else []
                
                # Execute dynamic command
                result = self.command_registry.execute_command(cmd_name, args, context)
                print(result)
                return True, None, messages
                
            else:
                # Unknown command
                help_msg = (f"❓ Unknown command: {command}. "
                           "Type :help to see available commands.")
                print(help_msg)
                return True, None, messages
                
        except Exception as e:
            print(f"❌ Extension command failed: {e}")
            return True, None, messages
    
    def is_command(self, user_input: str) -> bool:
        """Check if user input is a command."""
        stripped = user_input.strip()
        # Check for :command format (builtin and direct extension commands)
        if stripped.startswith(':'):
            return True
        
        # Check for command: format (context providers)
        if self._is_context_provider_command(stripped):
            return True
            
        return False
    
    def _is_context_provider_command(self, user_input: str) -> bool:
        """Check if input matches context provider format: 'command: args'"""
        if ':' not in user_input:
            return False
        
        # Split on first colon
        parts = user_input.split(':', 1)
        if len(parts) != 2:
            return False
        
        command_name = parts[0].strip()
        
        # Check if this command exists in registry and is a context provider
        dynamic_command = self.command_registry.get_command(command_name)
        return dynamic_command is not None and getattr(dynamic_command, 'is_context_provider', False)
    
    def get_available_commands(self) -> List[str]:
        """Get list of available commands including dynamic commands."""
        # Built-in commands
        builtin_commands = [
            ":help", ":setup", ":clear", ":models",
            ":download", ":delete", ":switch", ":storage", ":download-bielik", ":exit", ":quit", ":q"
        ]
        
        # Dynamic/extension commands (separate direct commands from context providers)
        direct_commands = []
        context_providers = []
        
        for cmd_name in self.command_registry.list_commands():
            cmd_obj = self.command_registry.get_command(cmd_name)
            if cmd_obj and getattr(cmd_obj, 'is_context_provider', False):
                context_providers.append(f"{cmd_name}:")
            else:
                direct_commands.append(f":{cmd_name}")
        
        # Combine and return
        return builtin_commands + direct_commands + context_providers
    
    def _load_bielik_models(self) -> dict:
        """Load Bielik models registry from JSON file."""
        try:
            models_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'bielik_models.json')
            with open(models_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load Bielik models registry: {e}")
            return {"bielik_models": {}, "recommendations": {}}
    
    def _show_bielik_models(self):
        """Display available Bielik models for download."""
        models_data = self._load_bielik_models()
        models = models_data.get('bielik_models', {})
        recommendations = models_data.get('recommendations', {})
        
        print("🦅 Available Bielik Models for Download")
        print("========================================")
        print()
        
        # Show recommendations first
        if recommendations:
            print("🌟 Recommended Models:")
            for use_case, model_id in recommendations.items():
                model_info = self._find_model_by_id(models, model_id)
                if model_info:
                    print(f"  • {use_case.replace('_', ' ').title()}: {model_info['name']}")
                    print(f"    ID: {model_id}")
            print()
        
        # Show all categories
        for category, category_models in models.items():
            if not category_models:
                continue
                
            category_title = {
                'official': '🏛️ Official Models',
                'quantized': '⚡ Quantized Models (Optimized)',
                'community': '👥 Community Models',
                'specialized': '🎯 Specialized Models',
                'compressed': '📦 Compressed Models'
            }.get(category, f'📁 {category.title()} Models')
            
            print(category_title)
            for model_id, model_info in category_models.items():
                status = "⭐ RECOMMENDED" if model_info.get('recommended') else ""
                print(f"  • {model_info['name']} {status}")
                print(f"    ID: {model_id}")
                print(f"    Type: {model_info['type']} | Size: {model_info['size']} | Format: {model_info['format']}")
                print(f"    {model_info['description']}")
                print()
        
        print("💡 Usage:")
        print("  :download-bielik <model_id>    - Download specific model")
        print("  :download-bielik recommended   - Download recommended model")
        print("  Example: :download-bielik speakleash/Bielik-7B-Instruct-v0.1-GGUF")
    
    def _find_model_by_id(self, models: dict, model_id: str) -> dict:
        """Find model info by ID across all categories."""
        for category_models in models.values():
            if model_id in category_models:
                return category_models[model_id]
        return None
    
    def _handle_bielik_download(self, model_identifier: str, current_model: str) -> tuple:
        """Handle Bielik model download."""
        models_data = self._load_bielik_models()
        models = models_data.get('bielik_models', {})
        recommendations = models_data.get('recommendations', {})
        
        # Handle special cases
        if model_identifier == "recommended":
            model_identifier = recommendations.get('beginner', 'speakleash/Bielik-7B-Instruct-v0.1-GGUF')
        
        # Find model info
        model_info = self._find_model_by_id(models, model_identifier)
        if not model_info:
            print(f"❌ Model '{model_identifier}' not found in Bielik registry")
            print("💡 Use ':download-bielik' to see available models")
            return True, None, []
        
        try:
            print(f"🦅 Downloading Bielik model: {model_info['name']}")
            print(f"📋 Description: {model_info['description']}")
            print(f"🔄 Starting download from HuggingFace...")
            
            # Download model using HuggingFace Hub
            models_dir = os.path.expanduser("~/.cache/bielik/models")
            os.makedirs(models_dir, exist_ok=True)
            
            model_path = snapshot_download(
                repo_id=model_identifier,
                cache_dir=models_dir,
                local_files_only=False
            )
            
            print(f"✅ Model downloaded successfully!")
            print(f"📂 Model location: {model_path}")
            
            # Show usage instructions
            print(f"💡 Model Usage:")
            print(f"   • GGUF models: Use with llama.cpp or compatible tools")
            print(f"   • PyTorch models: Use with transformers library")
            print(f"   • Model ID: {model_identifier}")
            
            # Save model info to local cache for future reference
            try:
                models_cache_file = os.path.expanduser("~/.cache/bielik/downloaded_models.json")
                os.makedirs(os.path.dirname(models_cache_file), exist_ok=True)
                
                # Load existing cache
                try:
                    with open(models_cache_file, 'r') as f:
                        cache = json.load(f)
                except:
                    cache = {}
                
                # Add new model to cache
                cache[model_identifier] = {
                    'name': model_info['name'],
                    'description': model_info['description'],
                    'path': model_path,
                    'downloaded_at': __import__('datetime').datetime.now().isoformat(),
                    'type': model_info.get('type', 'unknown'),
                    'format': model_info.get('format', 'unknown')
                }
                
                # Save updated cache
                with open(models_cache_file, 'w') as f:
                    json.dump(cache, f, indent=2)
                
                print(f"📝 Model cached for future reference")
                
            except Exception as e:
                self.logger.warning(f"Failed to cache model info: {e}")
            
            return True, None, []
            
        except Exception as e:
            self.logger.error(f"Failed to download Bielik model {model_identifier}: {e}")
            print(f"❌ Download failed: {e}")
            print(f"💡 Check your internet connection and try again")
            return True, None, []
