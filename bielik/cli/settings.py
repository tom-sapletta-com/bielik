"""
CLI Settings Manager for Bielik

Handles user personalization settings, model display names, and .env file management.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from ..config import get_config, get_logger


class CLISettingsManager:
    """
    Manages CLI personalization settings and automatic .env file updates.
    """
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(__name__)
        self.env_file_path = Path.cwd() / '.env'
        
        # Default settings
        self._settings = {
            'user_name': self._get_default_username(),
            'assistant_name': self._get_model_display_name(),
            'current_model': None,
            'auto_switch_after_download': True
        }
        
        # Load existing settings from .env
        self._load_settings_from_env()
    
    def _get_default_username(self) -> str:
        """Get default username from whoami command."""
        try:
            result = subprocess.run(['whoami'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                username = result.stdout.strip()
                if username:
                    return username.title()  # Capitalize first letter
        except Exception as e:
            self.logger.warning(f"Could not get username from whoami: {e}")
        
        # Fallback to environment variables or default
        return os.environ.get('USER', os.environ.get('USERNAME', 'You'))
    
    def _get_model_display_name(self, model_name: Optional[str] = None) -> str:
        """Generate short display name from model name."""
        if not model_name:
            model_name = self.config.BIELIK_MODEL
        
        # Extract meaningful parts from model name
        if 'bielik' in model_name.lower():
            # For Bielik models, extract version info
            parts = model_name.lower().split('-')
            for part in parts:
                if 'bielik' in part:
                    continue
                # Look for parts like "4.5b", "7b", "11b"
                if any(char.isdigit() for char in part) and 'b' in part and 'v' not in part:
                    return f"bielik-{part}"
            return "bielik"
        
        elif 'llama' in model_name.lower():
            return "Llama"
        elif 'mistral' in model_name.lower():
            return "Mistral"
        elif 'qwen' in model_name.lower():
            return "Qwen"
        elif 'gemma' in model_name.lower():
            return "Gemma"
        else:
            # Extract first meaningful part
            parts = model_name.replace('/', '-').split('-')
            if parts:
                return parts[0].title()[:8]  # Max 8 chars
            return "AI"
    
    def _load_settings_from_env(self):
        """Load settings from .env file if it exists."""
        if not self.env_file_path.exists():
            return
        
        try:
            with open(self.env_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or '=' not in line:
                        continue
                    
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    
                    # Map env variables to settings
                    if key == 'BIELIK_CLI_USERNAME':
                        self._settings['user_name'] = value
                    elif key == 'BIELIK_CLI_ASSISTANT_NAME':
                        self._settings['assistant_name'] = value
                    elif key == 'BIELIK_CLI_CURRENT_MODEL':
                        self._settings['current_model'] = value
                    elif key == 'BIELIK_CLI_AUTO_SWITCH':
                        self._settings['auto_switch_after_download'] = value.lower() in ('true', '1', 'yes')
                        
        except Exception as e:
            self.logger.warning(f"Could not load settings from .env: {e}")
    
    def _save_settings_to_env(self):
        """Save current settings to .env file."""
        try:
            # Read existing .env content
            existing_lines = []
            if self.env_file_path.exists():
                with open(self.env_file_path, 'r') as f:
                    existing_lines = f.readlines()
            
            # Remove old Bielik CLI settings
            filtered_lines = []
            for line in existing_lines:
                if not any(line.strip().startswith(key) for key in [
                    'BIELIK_CLI_USERNAME=',
                    'BIELIK_CLI_ASSISTANT_NAME=', 
                    'BIELIK_CLI_CURRENT_MODEL=',
                    'BIELIK_CLI_AUTO_SWITCH='
                ]):
                    filtered_lines.append(line)
            
            # Add current settings
            cli_settings = [
                f'# Bielik CLI Settings\n',
                f'BIELIK_CLI_USERNAME="{self._settings["user_name"]}"\n',
                f'BIELIK_CLI_ASSISTANT_NAME="{self._settings["assistant_name"]}"\n',
            ]
            
            if self._settings['current_model']:
                cli_settings.append(f'BIELIK_CLI_CURRENT_MODEL="{self._settings["current_model"]}"\n')
            
            cli_settings.append(f'BIELIK_CLI_AUTO_SWITCH="{str(self._settings["auto_switch_after_download"]).lower()}"\n')
            cli_settings.append('\n')
            
            # Write updated .env file
            with open(self.env_file_path, 'w') as f:
                f.writelines(filtered_lines)
                f.writelines(cli_settings)
            
            self.logger.info(f"CLI settings saved to {self.env_file_path}")
            
        except Exception as e:
            self.logger.error(f"Could not save settings to .env: {e}")
    
    def get_user_name(self) -> str:
        """Get current user display name."""
        return self._settings['user_name']
    
    def get_assistant_name(self) -> str:
        """Get current assistant display name."""
        return self._settings['assistant_name']
    
    def get_current_model(self) -> Optional[str]:
        """Get current model name."""
        return self._settings['current_model']
    
    def set_user_name(self, name: str) -> bool:
        """Set user display name and save to .env."""
        try:
            self._settings['user_name'] = name.strip().title()
            self._save_settings_to_env()
            return True
        except Exception as e:
            self.logger.error(f"Could not set user name: {e}")
            return False
    
    def set_current_model(self, model_name: str) -> bool:
        """Set current model and update assistant display name."""
        try:
            self._settings['current_model'] = model_name
            self._settings['assistant_name'] = self._get_model_display_name(model_name)
            self._save_settings_to_env()
            return True
        except Exception as e:
            self.logger.error(f"Could not set current model: {e}")
            return False
    
    def should_auto_switch_after_download(self) -> bool:
        """Check if should auto-switch to model after download."""
        return self._settings['auto_switch_after_download']
    
    def get_user_prompt_prefix(self) -> str:
        """Get formatted user prompt prefix."""
        return f"🧑 {self.get_user_name()}:"
    
    def get_assistant_prompt_prefix(self) -> str:
        """Get formatted assistant prompt prefix."""
        name = self.get_assistant_name()
        # Choose emoji based on assistant name
        if 'bielik' in name.lower():
            emoji = '🦅'
        elif 'llama' in name.lower():
            emoji = '🦙'
        elif 'mistral' in name.lower():
            emoji = '🌪️'
        elif 'qwen' in name.lower():
            emoji = '🐼'
        elif 'gemma' in name.lower():
            emoji = '💎'
        else:
            emoji = '🤖'
        
        return f"{emoji} {name}:"
    
    def get_settings_summary(self) -> Dict[str, Any]:
        """Get summary of all current settings."""
        return {
            'user_name': self.get_user_name(),
            'assistant_name': self.get_assistant_name(),
            'current_model': self.get_current_model(),
            'auto_switch': self.should_auto_switch_after_download(),
            'env_file_path': str(self.env_file_path),
            'env_file_exists': self.env_file_path.exists()
        }


def get_cli_settings() -> CLISettingsManager:
    """Get global CLI settings manager instance."""
    if not hasattr(get_cli_settings, '_instance'):
        get_cli_settings._instance = CLISettingsManager()
    return get_cli_settings._instance
