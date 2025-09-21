#!/usr/bin/env python3
"""
Bielik Python API Client - Modular client architecture for Bielik AI assistant.

This module serves as the main entry point for the Bielik Python client.
It now uses a modular architecture with separate components for core functionality,
model management, and utilities.

All strings and comments have been converted to English as requested.

The original 510-line monolithic client has been refactored into:
- client/core.py: Core BielikClient class with main functionality
- client/model_manager.py: HF model management operations
- client/utils.py: Utility functions and system checks
"""

# Import the refactored BielikClient from the modular structure
from .client import BielikClient, ClientModelManager, ClientUtils

# Backward compatibility exports
__all__ = ['BielikClient', 'ClientModelManager', 'ClientUtils']
