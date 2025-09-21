#!/usr/bin/env python3
"""
Bielik CLI - Modular command-line interface for Bielik AI assistant.

This package provides a command-line interface for interacting with Bielik,
supporting both Ollama integration and direct Hugging Face model execution.
"""

from .main import main
from .commands import CommandProcessor
from .setup import SetupManager
from .models import ModelManager as CLIModelManager

__all__ = ['main', 'CommandProcessor', 'SetupManager', 'CLIModelManager']
