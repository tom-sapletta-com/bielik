"""
Image Analysis Module for Bielik

This module provides image analysis capabilities using HuggingFace vision models.
Supports multiple image formats and provides detailed descriptions.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

try:
    # Handle Python 3.11 compatibility issue with transformers/tensorflow
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    from transformers import (
        BlipProcessor, BlipForConditionalGeneration,
        AutoProcessor, AutoModelForCausalLM
    )
    import torch
    HAVE_TRANSFORMERS = True
except (ImportError, RuntimeError, AttributeError) as e:
    # Handle various import errors including Python 3.11 formatargspec issues
    HAVE_TRANSFORMERS = False
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"Transformers not available: {e}")

from .config import get_config, get_logger


class ImageAnalyzer:
    """
    Image analysis using HuggingFace vision models.
    Supports image captioning and visual question answering.
    """
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(__name__)
        self.processor = None
        self.model = None
        self.model_loaded = False
        
        # Check if vision packages are available
        self._vision_available = HAVE_PIL and HAVE_TRANSFORMERS
        if not self._vision_available:
            self.logger.info("Vision packages not installed - image analysis disabled")
            if not HAVE_PIL:
                self.logger.info("Missing: Pillow (install with: pip install bielik[vision])")
            if not HAVE_TRANSFORMERS:
                self.logger.info("Missing: transformers, torch (install with: pip install bielik[vision])")
        
        # Supported image formats
        self.supported_formats = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', 
            '.webp', '.tiff', '.ico', '.heic', '.heif'
        }
        
        if not HAVE_PIL:
            self.logger.warning("PIL/Pillow not available - image analysis disabled")
        if not HAVE_TRANSFORMERS:
            self.logger.warning("Transformers not available - image analysis disabled")

    def is_available(self) -> bool:
        """Check if image analysis is available."""
        return HAVE_PIL and HAVE_TRANSFORMERS

    def is_image_file(self, file_path: str) -> bool:
        """Check if file is a supported image format."""
        if not os.path.exists(file_path):
            return False
        
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_formats

    def load_model(self, model_name: str = "Salesforce/blip-image-captioning-base") -> bool:
        """
        Load vision model for image analysis.
        
        Args:
            model_name: HuggingFace model name for image captioning
            
        Returns:
            bool: True if model loaded successfully
        """
        if not self.is_available():
            self.logger.error("Image analysis dependencies not available")
            return False

        try:
            self.logger.info(f"Loading vision model: {model_name}")
            
            # Load BLIP model for image captioning
            self.processor = BlipProcessor.from_pretrained(model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(model_name)
            
            # Move to GPU if available
            if torch.cuda.is_available():
                self.model = self.model.cuda()
                self.logger.info("Using GPU for image analysis")
            else:
                self.logger.info("Using CPU for image analysis")
            
            self.model_loaded = True
            self.logger.info("Vision model loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load vision model: {e}")
            return False

    def analyze_image(self, image_path: str, question: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze an image and return description.
        
        Args:
            image_path: Path to image file
            question: Optional question about the image
            
        Returns:
            dict: Analysis results with description and metadata
        """
        if not self.is_available():
            return {
                "error": "Image analysis not available - missing dependencies",
                "description": None,
                "metadata": {}
            }
        
        if not self.is_image_file(image_path):
            return {
                "error": f"Unsupported image format or file not found: {image_path}",
                "description": None,
                "metadata": {}
            }
        
        # Load model if not already loaded
        if not self.model_loaded:
            if not self.load_model():
                return {
                    "error": "Failed to load vision model",
                    "description": None,
                    "metadata": {}
                }
        
        try:
            # Load and process image
            image = Image.open(image_path).convert('RGB')
            
            # Get image metadata
            metadata = {
                "file_path": image_path,
                "file_size": os.path.getsize(image_path),
                "dimensions": image.size,
                "format": image.format,
                "mode": image.mode
            }
            
            # Generate description
            if question:
                # Visual Question Answering
                inputs = self.processor(image, question, return_tensors="pt")
            else:
                # Image Captioning
                inputs = self.processor(image, return_tensors="pt")
            
            # Move inputs to same device as model
            if torch.cuda.is_available() and self.model_loaded:
                inputs = {k: v.cuda() if isinstance(v, torch.Tensor) else v 
                         for k, v in inputs.items()}
            
            # Generate caption/answer
            with torch.no_grad():
                out = self.model.generate(**inputs, max_length=150)
            
            description = self.processor.decode(out[0], skip_special_tokens=True)
            
            # Clean up description
            if question and description.lower().startswith(question.lower()):
                description = description[len(question):].strip()
            
            self.logger.info(f"Successfully analyzed image: {image_path}")
            
            return {
                "error": None,
                "description": description,
                "metadata": metadata,
                "question": question
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing image {image_path}: {e}")
            return {
                "error": f"Image analysis failed: {str(e)}",
                "description": None,
                "metadata": {}
            }

    def analyze_multiple_images(self, image_paths: List[str], 
                              question: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Analyze multiple images.

        Args:
            image_paths: List of image file paths
            question: Optional question about the images

        Returns:
            list: List of analysis results for each image
        """
        results = []

        for image_path in image_paths:
            result = self.analyze_image(image_path, question)
            results.append(result)

        return results

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "model_loaded": self.model_loaded,
            "dependencies_available": self.is_available(),
            "supported_formats": list(self.supported_formats),
            "gpu_available": torch.cuda.is_available() if HAVE_TRANSFORMERS else False
        }


def get_image_analyzer() -> ImageAnalyzer:
    """Get global image analyzer instance."""
    if not hasattr(get_image_analyzer, '_instance'):
        get_image_analyzer._instance = ImageAnalyzer()
    return get_image_analyzer._instance
