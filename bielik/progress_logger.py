#!/usr/bin/env python3
"""
Progress tracking and logging utilities for model inference.
Provides detailed performance metrics and ETA estimation.
"""

import time
import sys
from typing import Optional
from dataclasses import dataclass


@dataclass
class InferenceMetrics:
    """Metrics for model inference performance."""
    start_time: float
    tokens_generated: int = 0
    prompt_length: int = 0
    max_tokens: int = 0
    
    def get_tokens_per_second(self) -> float:
        """Calculate current generation speed."""
        elapsed = time.time() - self.start_time
        if elapsed == 0 or self.tokens_generated == 0:
            return 0.0
        return self.tokens_generated / elapsed
    
    def get_eta_seconds(self) -> float:
        """Estimate remaining time in seconds."""
        if self.tokens_generated == 0:
            return 0.0
        
        tokens_per_sec = self.get_tokens_per_second()
        if tokens_per_sec == 0:
            return 0.0
        
        remaining_tokens = self.max_tokens - self.tokens_generated
        return remaining_tokens / tokens_per_sec
    
    def get_progress_percentage(self) -> float:
        """Get generation progress as percentage."""
        if self.max_tokens == 0:
            return 0.0
        return (self.tokens_generated / self.max_tokens) * 100


class ProgressLogger:
    """Logs progress with metrics for model inference."""
    
    def __init__(self, logger):
        self.logger = logger
        self.metrics: Optional[InferenceMetrics] = None
        self.last_update = 0
        self.update_interval = 2.0  # Update every 2 seconds
        
    def start_inference(self, prompt_length: int, max_tokens: int):
        """Start tracking inference progress."""
        self.metrics = InferenceMetrics(
            start_time=time.time(),
            prompt_length=prompt_length,
            max_tokens=max_tokens
        )
        
        self.logger.info("=" * 60)
        self.logger.info("🚀 Starting AI response generation")
        self.logger.info(f"📝 Prompt length: {prompt_length} characters")
        self.logger.info(f"🎯 Max tokens to generate: {max_tokens}")
        self.logger.info("=" * 60)
        
    def update_progress(self, tokens_generated: int, force: bool = False):
        """Update progress metrics and log if enough time passed."""
        if not self.metrics:
            return
        
        self.metrics.tokens_generated = tokens_generated
        current_time = time.time()
        
        # Only update if enough time passed or forced
        if not force and (current_time - self.last_update) < self.update_interval:
            return
        
        self.last_update = current_time
        
        # Calculate metrics
        tokens_per_sec = self.metrics.get_tokens_per_second()
        eta_seconds = self.metrics.get_eta_seconds()
        progress_pct = self.metrics.get_progress_percentage()
        elapsed = current_time - self.metrics.start_time
        
        # Log progress
        self.logger.info(f"⏱️  Progress: {progress_pct:.1f}% | "
                        f"Generated: {tokens_generated}/{self.metrics.max_tokens} tokens | "
                        f"Speed: {tokens_per_sec:.1f} tokens/sec | "
                        f"ETA: {eta_seconds:.1f}s | "
                        f"Elapsed: {elapsed:.1f}s")
        
        # Print progress bar to stderr (won't interfere with output)
        self._print_progress_bar(progress_pct)
    
    def _print_progress_bar(self, percentage: float):
        """Print a visual progress bar."""
        bar_length = 40
        filled = int(bar_length * percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        sys.stderr.write(f"\r🔄 [{bar}] {percentage:.1f}%")
        sys.stderr.flush()
    
    def finish_inference(self):
        """Log completion metrics."""
        if not self.metrics:
            return
        
        elapsed = time.time() - self.metrics.start_time
        tokens_per_sec = self.metrics.get_tokens_per_second()
        
        # Clear progress bar
        sys.stderr.write("\r" + " " * 60 + "\r")
        sys.stderr.flush()
        
        self.logger.info("=" * 60)
        self.logger.info("✅ Response generation completed!")
        self.logger.info(f"⏱️  Total time: {elapsed:.2f} seconds")
        self.logger.info(f"📊 Tokens generated: {self.metrics.tokens_generated}")
        self.logger.info(f"⚡ Average speed: {tokens_per_sec:.2f} tokens/sec")
        self.logger.info("=" * 60)
        
        self.metrics = None
