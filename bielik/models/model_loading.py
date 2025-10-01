#!/usr/bin/env python3
"""
Model loading utilities with timeout handling for Bielik HuggingFace integration.
"""

import os
import signal
import time
from typing import Any, Callable

from .model_exceptions import ModelLoadingTimeoutError


def get_model_loading_timeout() -> int:
    """Get the model loading timeout from environment or use default."""
    return int(os.environ.get("BIELIK_LOAD_TIMEOUT", "10"))


def is_debug_mode() -> bool:
    """Check if debug mode is enabled via environment variable."""
    return os.environ.get("BIELIK_DEBUG", "0").lower() in ("1", "true", "yes")


def timeout_handler(signum, frame):
    """Handle the timeout signal."""
    raise ModelLoadingTimeoutError("Model loading timed out")


def load_with_timeout(loader_func: Callable, timeout: int, **kwargs) -> Any:
    """
    Load model with timeout protection.
    
    Args:
        loader_func: Function to call for loading
        timeout: Timeout in seconds
        **kwargs: Arguments to pass to loader_func
        
    Returns:
        Result from loader_func
        
    Raises:
        ModelLoadingTimeoutError: If loading times out
    """
    # Set up signal handler for timeout
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        result = loader_func(**kwargs)
        signal.alarm(0)  # Cancel the alarm
        return result
    except ModelLoadingTimeoutError:
        raise
    except Exception as e:
        signal.alarm(0)  # Cancel the alarm
        raise
    finally:
        # Restore the old signal handler
        signal.signal(signal.SIGALRM, old_handler)
