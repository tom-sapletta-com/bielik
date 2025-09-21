#!/usr/bin/env python3
"""
Bielik CLI - Interactive chat shell with modular architecture.

This module serves as the main entry point for the Bielik CLI application.
It now uses a modular architecture with separate components for setup,
commands, model management, and chat communication.

All strings and comments have been converted to English as requested.

The original 716-line monolithic CLI has been refactored into:
- cli/main.py: Main entry point and argument parsing
- cli/commands.py: Command processing and help
- cli/setup.py: Interactive setup and system configuration  
- cli/models.py: HF model management commands
- cli/send_chat.py: Chat communication layer
"""

from .cli.main import main

# Backward compatibility exports
from .cli.send_chat import send_chat
from .cli.commands import CommandProcessor
from .cli.setup import SetupManager
from .cli.models import ModelManager as CLIModelManager

__all__ = ['main', 'send_chat', 'CommandProcessor', 'SetupManager', 'CLIModelManager']
