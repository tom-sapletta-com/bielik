"""
Optimized model loading with timeout and debug support.

This module provides a wrapper for model loading that includes:
- Configurable timeout
- Debug mode with detailed logging
- Automatic fallback to CPU if GPU fails
- Memory optimization
"""

import os
import time
import signal
import logging
from typing import Any, Callable, Optional, TypeVar, Type, TypeVar
from functools import wraps
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')

class ModelLoadingError(Exception):
    """Custom exception for model loading errors."""
    pass

class ModelLoadingTimeoutError(ModelLoadingError):
    """Raised when model loading exceeds the timeout."""
    pass

def timeout_handler(signum, frame):
    """Handle the timeout signal."""
    raise ModelLoadingTimeoutError("Model loading timed out")

@contextmanager
def timeout_context(seconds: int):
    """Context manager for timing out operations."""
    # Set the signal handler and a timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Disable the alarm
        signal.alarm(0)

def timeit(func: Callable) -> Callable:
    """Decorator to measure execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.debug(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result
    return wrapper

def load_model_with_timeout(
    loader_func: Callable[..., T],
    timeout: int = 10,
    debug: bool = False,
    **loader_kwargs
) -> T:
    """
    Load a model with a timeout and debug support.
    
    Args:
        loader_func: Function that loads and returns the model
        timeout: Maximum time in seconds to wait for model loading
        debug: If True, enable debug logging
        **loader_kwargs: Arguments to pass to the loader function
        
    Returns:
        The loaded model
        
    Raises:
        ModelLoadingTimeoutError: If loading exceeds the timeout
        ModelLoadingError: For other loading errors
    """
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    logger.info(f"Loading model with timeout of {timeout} seconds...")
    
    try:
        with timeout_context(timeout):
            start_time = time.time()
            
            try:
                # Try to load the model
                model = loader_func(**loader_kwargs)
                load_time = time.time() - start_time
                logger.info(f"Model loaded successfully in {load_time:.2f} seconds")
                return model
                
            except Exception as e:
                logger.error(f"Error loading model: {str(e)}", exc_info=debug)
                if debug:
                    logger.debug("Attempting to load with CPU fallback...")
                    try:
                        loader_kwargs["device"] = "cpu"
                        model = loader_func(**loader_kwargs)
                        logger.warning("Model loaded on CPU as fallback")
                        return model
                    except Exception as cpu_e:
                        logger.error(f"CPU fallback failed: {str(cpu_e)}")
                raise ModelLoadingError(f"Failed to load model: {str(e)}")
                
    except ModelLoadingTimeoutError:
        logger.error(f"Model loading timed out after {timeout} seconds")
        if debug:
            logger.debug("Debug info:")
            logger.debug(f"Loader function: {loader_func.__name__}")
            logger.debug(f"Loader arguments: {loader_kwargs}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during model loading: {str(e)}")
        raise ModelLoadingError(f"Unexpected error: {str(e)}")

def get_model_loading_timeout() -> int:
    """Get the model loading timeout from environment or use default."""
    return int(os.environ.get("BIELIK_LOAD_TIMEOUT", "10"))

def is_debug_mode() -> bool:
    """Check if debug mode is enabled via environment variable."""
    return os.environ.get("BIELIK_DEBUG", "0").lower() in ("1", "true", "yes")
