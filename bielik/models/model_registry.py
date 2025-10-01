#!/usr/bin/env python3
"""
Model registry data structures and utilities for Bielik.
Manages model information and registry operations.
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ModelInfo:
    """Information about a downloaded model."""
    name: str
    repo_id: str
    file_name: str
    local_path: str
    size_bytes: int
    downloaded_at: str
    model_type: str = "gguf"
    description: str = ""
    parameters: str = ""
    version: str = ""

