#!/usr/bin/env python3
"""
Configuration management for Bielik package.
Handles .env files, environment variables, and default settings.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv


class BielikConfig:
    """
    Configuration management class for Bielik.
    Loads settings from .env files and environment variables with fallback defaults.
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to .env file (default: searches for .env in current/parent dirs)
        """
        # Load .env file
        self._load_env_file(env_file)
        
        # Initialize all configuration values
        self._init_config()
        
        # Setup logging based on configuration
        self._setup_logging()
    
    def _load_env_file(self, env_file: Optional[str] = None):
        """Load .env file if it exists."""
        if env_file:
            if Path(env_file).exists():
                load_dotenv(env_file)
        else:
            # Search for .env file in current directory and parent directories
            current_dir = Path.cwd()
            for path in [current_dir] + list(current_dir.parents):
                env_path = path / '.env'
                if env_path.exists():
                    load_dotenv(env_path)
                    break
    
    def _get_env_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean value from environment variable."""
        value = os.environ.get(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on', 'enabled')
    
    def _get_env_int(self, key: str, default: int) -> int:
        """Get integer value from environment variable."""
        try:
            return int(os.environ.get(key, str(default)))
        except (ValueError, TypeError):
            return default
    
    def _get_env_list(self, key: str, default: List[str] = None) -> List[str]:
        """Get list value from environment variable (comma-separated)."""
        if default is None:
            default = []
        value = os.environ.get(key, '')
        if not value:
            return default
        return [item.strip() for item in value.split(',') if item.strip()]
    
    def _init_config(self):
        """Initialize all configuration values."""
        # Ollama Configuration
        self.OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.BIELIK_MODEL = os.environ.get("BIELIK_MODEL", "SpeakLeash/bielik-7b-instruct-v0.1-gguf")
        self.CHAT_ENDPOINT = self.OLLAMA_HOST.rstrip("/") + "/v1/chat/completions"
        
        # Auto-setup Behavior
        self.AUTO_SETUP_ENABLED = self._get_env_bool("AUTO_SETUP_ENABLED", True)
        self.INTERACTIVE_SETUP = self._get_env_bool("INTERACTIVE_SETUP", True)
        self.INSTALL_OLLAMA_AUTO = self._get_env_bool("INSTALL_OLLAMA_AUTO", True)
        self.PULL_MODEL_AUTO = self._get_env_bool("PULL_MODEL_AUTO", True)
        
        # Logging Configuration
        self.LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
        self.LOG_FORMAT = os.environ.get("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.LOG_TO_FILE = self._get_env_bool("LOG_TO_FILE", False)
        self.LOG_FILE_PATH = os.environ.get("LOG_FILE_PATH", "./bielik.log")
        
        # Content Processing Configuration
        self.FETCH_URLS_AUTO = self._get_env_bool("FETCH_URLS_AUTO", True)
        self.CONVERT_DOCUMENTS_AUTO = self._get_env_bool("CONVERT_DOCUMENTS_AUTO", True)
        self.MAX_URL_CONTENT_LENGTH = self._get_env_int("MAX_URL_CONTENT_LENGTH", 100000)
        self.MAX_DOCUMENT_SIZE_MB = self._get_env_int("MAX_DOCUMENT_SIZE_MB", 10)
        
        # Security Settings
        self.ALLOW_FILE_ACCESS = self._get_env_bool("ALLOW_FILE_ACCESS", True)
        self.ALLOWED_FILE_EXTENSIONS = self._get_env_list("ALLOWED_FILE_EXTENSIONS", 
            ['.txt', '.md', '.pdf', '.docx', '.html', '.htm'])
        self.BLOCKED_DOMAINS = self._get_env_list("BLOCKED_DOMAINS", [])
        
        # Performance Settings
        self.REQUEST_TIMEOUT = self._get_env_int("REQUEST_TIMEOUT", 30)
        self.MODEL_TIMEOUT = self._get_env_int("MODEL_TIMEOUT", 300)
        self.SETUP_TIMEOUT = self._get_env_int("SETUP_TIMEOUT", 1800)
        
        # Development Settings
        self.DEBUG_MODE = self._get_env_bool("DEBUG_MODE", False)
        self.VERBOSE_OUTPUT = self._get_env_bool("VERBOSE_OUTPUT", False)
    
    def _setup_logging(self):
        """Setup logging based on configuration."""
        # Convert string log level to logging constant
        log_level = getattr(logging, self.LOG_LEVEL, logging.INFO)
        
        # Create logger
        logger = logging.getLogger('bielik')
        logger.setLevel(log_level)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create formatter
        formatter = logging.Formatter(self.LOG_FORMAT)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler if enabled
        if self.LOG_TO_FILE:
            try:
                file_handler = logging.FileHandler(self.LOG_FILE_PATH)
                file_handler.setLevel(log_level)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"Could not setup file logging: {e}")
        
        self.logger = logger
    
    def get_logger(self) -> logging.Logger:
        """Get configured logger instance."""
        return self.logger
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_') and key != 'logger'
        }
    
    def update_from_dict(self, config_dict: Dict[str, Any]):
        """Update configuration from dictionary."""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Reinitialize derived values
        self.CHAT_ENDPOINT = self.OLLAMA_HOST.rstrip("/") + "/v1/chat/completions"
        
        # Re-setup logging if logging config changed
        if any(key.startswith('LOG_') for key in config_dict.keys()):
            self._setup_logging()
    
    def save_to_env_file(self, file_path: str = ".env"):
        """Save current configuration to .env file."""
        config_lines = [
            "# Bielik Configuration File",
            "# Generated automatically - modify as needed",
            "",
            "# Ollama Server Configuration",
            f"OLLAMA_HOST={self.OLLAMA_HOST}",
            f"BIELIK_MODEL={self.BIELIK_MODEL}",
            "",
            "# Auto-setup Behavior",
            f"AUTO_SETUP_ENABLED={str(self.AUTO_SETUP_ENABLED).lower()}",
            f"INTERACTIVE_SETUP={str(self.INTERACTIVE_SETUP).lower()}",
            f"INSTALL_OLLAMA_AUTO={str(self.INSTALL_OLLAMA_AUTO).lower()}",
            f"PULL_MODEL_AUTO={str(self.PULL_MODEL_AUTO).lower()}",
            "",
            "# Logging Configuration",
            f"LOG_LEVEL={self.LOG_LEVEL}",
            f"LOG_FORMAT={self.LOG_FORMAT}",
            f"LOG_TO_FILE={str(self.LOG_TO_FILE).lower()}",
            f"LOG_FILE_PATH={self.LOG_FILE_PATH}",
            "",
            "# Content Processing Configuration",
            f"FETCH_URLS_AUTO={str(self.FETCH_URLS_AUTO).lower()}",
            f"CONVERT_DOCUMENTS_AUTO={str(self.CONVERT_DOCUMENTS_AUTO).lower()}",
            f"MAX_URL_CONTENT_LENGTH={self.MAX_URL_CONTENT_LENGTH}",
            f"MAX_DOCUMENT_SIZE_MB={self.MAX_DOCUMENT_SIZE_MB}",
            "",
            "# Security Settings",
            f"ALLOW_FILE_ACCESS={str(self.ALLOW_FILE_ACCESS).lower()}",
            f"ALLOWED_FILE_EXTENSIONS={','.join(self.ALLOWED_FILE_EXTENSIONS)}",
            f"BLOCKED_DOMAINS={','.join(self.BLOCKED_DOMAINS)}",
            "",
            "# Performance Settings",
            f"REQUEST_TIMEOUT={self.REQUEST_TIMEOUT}",
            f"MODEL_TIMEOUT={self.MODEL_TIMEOUT}",
            f"SETUP_TIMEOUT={self.SETUP_TIMEOUT}",
            "",
            "# Development Settings",
            f"DEBUG_MODE={str(self.DEBUG_MODE).lower()}",
            f"VERBOSE_OUTPUT={str(self.VERBOSE_OUTPUT).lower()}",
        ]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(config_lines))


# Global configuration instance
_config_instance: Optional[BielikConfig] = None


def get_config(env_file: Optional[str] = None) -> BielikConfig:
    """
    Get global configuration instance.
    
    Args:
        env_file: Path to .env file (only used on first call)
        
    Returns:
        BielikConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = BielikConfig(env_file)
    return _config_instance


def get_logger(name: str = 'bielik') -> logging.Logger:
    """
    Get configured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger
    """
    config = get_config()
    return logging.getLogger(name)
