#!/usr/bin/env python3
"""
Model loading exceptions for Bielik HuggingFace integration.
"""

class ModelLoadingError(Exception):
    """Base exception for model loading errors."""
    pass

class ModelLoadingTimeoutError(ModelLoadingError):
    """Raised when model loading exceeds the timeout."""
    pass
