#!/usr/bin/env python3
"""
Local GGUF model runner using llama-cpp-python for Bielik.
Provides chat interface without requiring external dependencies.
"""

import os
import time
from typing import Dict, List

try:
    from llama_cpp import Llama
    HAS_LLAMA_CPP = True
except ImportError:
    HAS_LLAMA_CPP = False

from ..config import get_config, get_logger
from ..progress_logger import ProgressLogger
from .model_exceptions import ModelLoadingError, ModelLoadingTimeoutError
from .model_loading import load_with_timeout, get_model_loading_timeout, is_debug_mode

class LocalLlamaRunner:
    """
    Runs GGUF models locally using llama-cpp-python.
    Provides chat interface without requiring Ollama.
    """
    
    def __init__(self, model_path: str, **kwargs):
        """
        Initialize local Llama runner with optimized loading.
        
        Args:
            model_path: Path to GGUF model file
            **kwargs: Additional arguments for Llama initialization
            
        Raises:
            ImportError: If llama-cpp-python is not installed
            ModelLoadingError: If model loading fails
            ModelLoadingTimeoutError: If model loading times out
        """
        if not HAS_LLAMA_CPP:
            raise ImportError("llama-cpp-python is required for local model execution")
        
        self.config = get_config()
        self.logger = get_logger(__name__)
        self.model_path = model_path
        self.model = None
        self.progress_logger = ProgressLogger(self.logger)
        
        # Default parameters
        default_params = {
            "n_ctx": 4096,  # Context length
            "n_threads": None,  # Auto-detect
            "n_gpu_layers": 0,  # CPU only by default
            "verbose": self.config.VERBOSE_OUTPUT if hasattr(self.config, 'VERBOSE_OUTPUT') else False,
        }
        
        # Merge with user params
        self.params = {**default_params, **kwargs}
        
        # Load the model with timeout
        self._load_model()
    
    def _load_model(self):
        """Load the model with timeout and error handling."""
        self.logger.info(f"Loading model from: {self.model_path}")
        self.logger.debug(f"Model parameters: {self.params}")
        
        # Define the loader function
        def loader():
            return Llama(self.model_path, **self.params)
        
        try:
            # Try loading with GPU first if specified
            if self.params.get("n_gpu_layers", 0) > 0:
                try:
                    self.model = load_with_timeout(
                        loader,
                        timeout=get_model_loading_timeout()
                    )
                    self.logger.info("Model loaded successfully with GPU acceleration")
                    return
                except (ModelLoadingError, Exception) as e:
                    self.logger.warning(f"GPU loading failed: {str(e)}. Falling back to CPU...")
                    # Fall back to CPU
                    self.params["n_gpu_layers"] = 0
            
            # Load with CPU
            self.model = load_with_timeout(
                loader,
                timeout=get_model_loading_timeout()
            )
            self.logger.info("Model loaded successfully on CPU")
            
        except ModelLoadingTimeoutError as e:
            self.logger.error("Model loading timed out. The model file might be corrupted or too large.")
            if is_debug_mode():
                self.logger.debug("Debug information:")
                self.logger.debug(f"Model path: {self.model_path}")
                self.logger.debug(f"File exists: {os.path.exists(self.model_path)}")
                if os.path.exists(self.model_path):
                    self.logger.debug(f"File size: {os.path.getsize(self.model_path) / (1024*1024):.2f} MB")
            raise
        except Exception as e:
            self.logger.error(f"Failed to load model: {str(e)}", exc_info=is_debug_mode())
            raise ModelLoadingError(f"Failed to load model: {str(e)}")

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate chat response with detailed progress tracking and auto-optimized
        parameters for short prompts.

        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional generation parameters (override auto-tuning)

        Returns:
            Generated response text
        """
        import time

        # Convert messages to prompt
        prompt = self._messages_to_prompt(messages)
        prompt_length = len(prompt)

        # Default generation parameters
        default_params = {
            "max_tokens": 2048,
            "temperature": 0.7,
            "top_p": 0.9,
            "echo": False,
            "stop": ["</s>", "<|im_end|>", "<|endoftext|>"]
        }

        # Merge with user-provided params
        params = {**default_params, **kwargs}

        # Auto-optimize for short prompts unless explicitly overridden
        def _auto_tune(plen: int) -> None:
            nonlocal params
            # Limit max tokens for short prompts
            if "max_tokens" not in kwargs:
                if plen < 120:
                    params["max_tokens"] = 64
                elif plen < 300:
                    params["max_tokens"] = 128
                elif plen < 800:
                    params["max_tokens"] = 256
                else:
                    # Cap excessive default for very long prompts to avoid slow runs
                    params["max_tokens"] = min(params.get("max_tokens", 2048), 512)

            # Adjust temperature based on simple intent heuristics
            if "temperature" not in kwargs:
                text = prompt.lower()
                factual_markers = ["ile", "co to", "definiuj", "podaj", "kiedy", "gdzie", "policz", "?", "ile to"]
                creative_markers = ["napisz", "stwórz", "stworz", "opowiedz", "historyj", "generuj", "zaprojektuj"]
                if any(m in text for m in creative_markers):
                    params["temperature"] = 0.9
                elif any(m in text for m in factual_markers):
                    params["temperature"] = 0.3
                else:
                    params["temperature"] = 0.6

        _auto_tune(prompt_length)

        max_tokens = params.get("max_tokens", 2048)

        # Start progress tracking and log summary
        self.logger.info("============================================================")
        self.logger.info("🚀 Starting AI response generation")
        self.logger.info(f"📝 Prompt length: {prompt_length} characters")
        self.logger.info(f"🎯 Max tokens to generate: {max_tokens}")
        self.logger.info("============================================================")
        self.logger.info(f"🔧 Generation parameters: temp={params['temperature']}, top_p={params.get('top_p', 0.9)}, max_tokens={max_tokens}")

        self.progress_logger.start_inference(prompt_length, max_tokens)
        start_time = time.time()

        try:
            # Generate with progress tracking
            result = self.model(prompt, **params)
            response = result['choices'][0]['text'].strip()

            # Calculate actual metrics
            elapsed = time.time() - start_time
            tokens_generated = len(response.split())  # Rough token estimate
            tokens_per_sec = tokens_generated / elapsed if elapsed > 0 else 0

            # Update progress to 100% and finish
            self.progress_logger.update_progress(tokens_generated, force=True)
            self.progress_logger.finish_inference()

            # Log final stats
            self.logger.info(f"📊 Response: {len(response)} chars (~{tokens_generated} tokens)")
            self.logger.info(f"⚡ Performance: {tokens_per_sec:.2f} tokens/sec, {elapsed:.2f}s total")

            return response

        except Exception as e:
            self.logger.error(f"Failed to generate response: {e}")
            # Ensure progress logger is cleaned up on error
            try:
                self.progress_logger.finish_inference()
            except Exception:
                pass
            return f"[LOCAL MODEL ERROR] {e}"

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to prompt format."""
        prompt_parts = []
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        # Add final prompt for assistant response
        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)
    
    def __del__(self):
        """Cleanup model when object is destroyed."""
        if hasattr(self, 'model'):
            del self.model
