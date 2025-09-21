#!/usr/bin/env python3
"""
Bielik CLI Command Processor - Handles CLI command parsing and execution.

This module processes user commands in the interactive CLI interface,
including special commands like :help, :status, :models, etc.
"""

from typing import List, Dict, Optional, Tuple
from .setup import SetupManager
from .models import ModelManager
from .settings import get_cli_settings
from ..config import get_config, get_logger


class CommandProcessor:
    """Processes and executes CLI commands."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(__name__)
        self.setup_manager = SetupManager()
        self.model_manager = ModelManager()
        self.settings = get_cli_settings()
        
    def show_welcome(self) -> None:
        """Display welcome message and help for beginners."""
        assistant_name = self.settings.get_assistant_name()
        user_name = self.settings.get_user_name()
        
        print("🦅 " + "="*50)
        print(f"   {assistant_name.upper()} - Polish AI Assistant")
        print("   Powered by Ollama + Speakleash")
        print("="*53)
        print()
        print(f"👋 Welcome {user_name}!")
        print()
        print("📋 Available Commands:")
        print("  :help    - show this help")
        print("  :status  - check Ollama connection")
        print("  :setup   - run interactive configuration")
        print("  :clear   - clear conversation history")
        print("  :models  - show available HF models")
        print("  :download <model> - download HF model (auto-switches)")
        print("  :delete <model>   - delete downloaded model")
        print("  :switch <model>   - switch to model")
        print("  :storage - show storage statistics")
        print("  :name <name>      - change your display name")
        print("  :settings         - show current settings")
        print("  :exit    - end session")
        print("  Ctrl+C   - quick exit")
        print()
        print("💡 Tips:")
        print("  • Write in Polish - AI understands Polish!")
        print("  • Ask questions, request help, chat naturally")
        print("  • Include image/folder paths for automatic analysis")
        print("  • If Ollama doesn't work, you'll see an error message")
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
        
        # Status command
        elif command == ":status":
            status = self.setup_manager.check_system_status()
            print(f"🔗 Status: {status}")
            return True, None, messages
        
        # Clear command
        elif command == ":clear":
            system_prompt = ("You are Bielik, a helpful Polish AI assistant. "
                           "Respond in Polish unless asked otherwise.")
            new_messages = [{"role": "system", "content": system_prompt}]
            print("🧹 Conversation history cleared.")
            return True, None, new_messages
        
        # Setup command
        elif command == ":setup":
            print("🔧 Running interactive configuration...")
            self.setup_manager.interactive_setup()
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
        
        # Switch command
        elif command.startswith(":switch"):
            parts = command.split(None, 1)
            if len(parts) > 1:
                new_model = self.model_manager.switch_model(parts[1], current_model)
                if new_model:
                    # Update settings with new model
                    self.settings.set_current_model(new_model)
                    print(f"✅ Assistant name updated to: {self.settings.get_assistant_name()}")
                return True, new_model, messages
            else:
                print("❓ Usage: :switch <model_name>")
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
        
        # Unknown command
        else:
            help_msg = (f"❓ Unknown command: {command}. "
                       "Type :help to see available commands.")
            print(help_msg)
            return True, None, messages
    
    def is_command(self, user_input: str) -> bool:
        """Check if user input is a command."""
        return user_input.strip().startswith(':')
    
    def get_available_commands(self) -> List[str]:
        """Get list of available commands."""
        return [
            ":help", ":status", ":setup", ":clear", ":models",
            ":download", ":delete", ":switch", ":storage", ":exit", ":quit", ":q"
        ]
