#!/usr/bin/env python3
"""
Bielik Client - Modular client architecture for Bielik AI assistant.

This package provides a Python client interface for interacting with Bielik,
supporting both Ollama integration and direct Hugging Face model execution.
The client has been refactored into smaller, complementary modules.
"""

from .core import BielikClient
from .model_manager import ClientModelManager
from .utils import ClientUtils

__all__ = ['BielikClient', 'ClientModelManager', 'ClientUtils']
