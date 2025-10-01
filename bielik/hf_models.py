#!/usr/bin/env python3
"""
Hugging Face model management for Bielik.
Downloads, manages, and runs SpeakLeash models directly from Hugging Face.
"""

import os
import json
import shutil
import signal
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
import logging

from huggingface_hub import hf_hub_download, list_repo_files, HfApi
from huggingface_hub.utils import HfHubHTTPError

try:
    from llama_cpp import Llama
    HAS_LLAMA_CPP = True
except ImportError:
    HAS_LLAMA_CPP = False

from .config import get_config, get_logger
from .progress_logger import ProgressLogger
from .models.model_exceptions import ModelLoadingError, ModelLoadingTimeoutError
from .models.model_loading import load_with_timeout, get_model_loading_timeout, is_debug_mode
from .models.model_registry import ModelInfo
from .models.model_manager import SpeakLeashModelManager
from .models.local_runner import LocalLlamaRunner

# Model loading utilities and timeout handling now imported from .models.model_loading

# All model loading utilities now imported from .models.model_loading


# ModelInfo dataclass now imported from .models.model_registry

# Global model manager instance for lazy initialization
_model_manager: Optional[SpeakLeashModelManager] = None
_model_initialized = False

def get_model_manager() -> SpeakLeashModelManager:
    """
    Get global model manager instance with lazy initialization.
    
    The manager is only fully initialized when actually needed to reduce startup time.
    """
    global _model_manager, _model_initialized
    
    if _model_manager is None:
        # Create instance but delay heavy initialization
        _model_manager = SpeakLeashModelManager()
        _model_initialized = False
    
    if not _model_initialized and HAS_LLAMA_CPP:
        # Only initialize models when actually needed
        _model_manager.initialize_models()
        _model_initialized = True
        
    return _model_manager
