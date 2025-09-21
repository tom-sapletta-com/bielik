#!/usr/bin/env python3
"""
Content processing module for Bielik.
Handles automatic fetching of URLs, HTML parsing, and document conversion to text.
"""

import os
import re
import mimetypes
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from urllib.parse import urlparse, urljoin
import logging

import requests
from bs4 import BeautifulSoup
import html2text

# Optional imports for document processing
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

try:
    import textract
    HAS_TEXTRACT = True
except ImportError:
    HAS_TEXTRACT = False
    textract = None

try:
    import pypdf
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

# Import new analysis modules
try:
    from .image_analyzer import get_image_analyzer
    from .folder_scanner import get_folder_scanner
    HAS_ANALYSIS_MODULES = True
except ImportError:
    HAS_ANALYSIS_MODULES = False

from .config import get_config, get_logger


class ContentProcessor:
    """
    Processes various content types: URLs, HTML, documents.
    Converts them to clean text for use in AI prompts.
    """
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(__name__)
        
        # Setup HTML to text converter
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        self.html_converter.ignore_emphasis = False
        self.html_converter.body_width = 0  # No line wrapping
    
    def is_url(self, text: str) -> bool:
        """Check if text is a valid URL."""
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def is_file_path(self, text: str) -> bool:
        """Check if text is a valid file path."""
        try:
            path = Path(text)
            return path.exists() and path.is_file()
        except Exception:
            return False
    
    def is_blocked_domain(self, url: str) -> bool:
        """Check if URL domain is blocked."""
        if not self.config.BLOCKED_DOMAINS:
            return False
        
        try:
            domain = urlparse(url).netloc.lower()
            return any(blocked.lower() in domain for blocked in self.config.BLOCKED_DOMAINS)
        except Exception:
            return False
    
    def fetch_url_content(self, url: str) -> Optional[str]:
        """
        Fetch and convert URL content to text.
        
        Args:
            url: URL to fetch
            
        Returns:
            Text content or None if failed
        """
        if not self.config.FETCH_URLS_AUTO:
            self.logger.info(f"URL fetching disabled, skipping: {url}")
            return None
        
        if self.is_blocked_domain(url):
            self.logger.warning(f"Blocked domain, skipping: {url}")
            return None
        
        try:
            self.logger.info(f"Fetching URL content: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; Bielik/1.0; +https://github.com/tomsapletta/bielik)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(
                url, 
                headers=headers, 
                timeout=self.config.REQUEST_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Check content length
            content = response.text
            if len(content) > self.config.MAX_URL_CONTENT_LENGTH:
                self.logger.warning(f"Content too long ({len(content)} chars), truncating")
                content = content[:self.config.MAX_URL_CONTENT_LENGTH]
            
            # Parse HTML and convert to text
            if 'html' in response.headers.get('content-type', '').lower():
                return self._html_to_text(content, url)
            else:
                return content
                
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch URL {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching URL {url}: {e}")
            return None
    
    def _html_to_text(self, html_content: str, base_url: str = None) -> str:
        """Convert HTML content to clean text."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text using html2text for better formatting
            text = self.html_converter.handle(str(soup))
            
            # Clean up the text
            text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Remove excessive newlines
            text = re.sub(r'[ \t]+', ' ', text)  # Normalize spaces
            text = text.strip()
            
            return text
            
        except Exception as e:
            self.logger.error(f"Failed to convert HTML to text: {e}")
            return html_content
    
    def get_file_type(self, file_path: str) -> Optional[str]:
        """Determine file type using multiple methods."""
        path = Path(file_path)
        
        # Check extension first
        extension = path.suffix.lower()
        if extension:
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type:
                return mime_type
        
        # Use python-magic if available
        if HAS_MAGIC:
            try:
                mime_type = magic.from_file(file_path, mime=True)
                return mime_type
            except Exception as e:
                self.logger.warning(f"Magic failed for {file_path}: {e}")
        
        return None
    
    def is_allowed_file(self, file_path: str) -> bool:
        """Check if file type is allowed for processing."""
        if not self.config.ALLOW_FILE_ACCESS:
            return False
        
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if self.config.ALLOWED_FILE_EXTENSIONS:
            return extension in self.config.ALLOWED_FILE_EXTENSIONS
        
        return True
    
    def convert_document_to_text(self, file_path: str) -> Optional[str]:
        """
        Convert document to text based on file type.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Text content or None if failed
        """
        if not self.config.CONVERT_DOCUMENTS_AUTO:
            self.logger.info(f"Document conversion disabled, skipping: {file_path}")
            return None
        
        if not self.is_allowed_file(file_path):
            self.logger.warning(f"File type not allowed: {file_path}")
            return None
        
        path = Path(file_path)
        
        # Check file size
        try:
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > self.config.MAX_DOCUMENT_SIZE_MB:
                self.logger.warning(f"File too large ({size_mb:.1f}MB): {file_path}")
                return None
        except Exception as e:
            self.logger.error(f"Could not check file size: {e}")
            return None
        
        self.logger.info(f"Converting document to text: {file_path}")
        
        # Try specific converters first
        extension = path.suffix.lower()
        
        if extension == '.txt':
            return self._read_text_file(file_path)
        elif extension == '.md':
            return self._read_text_file(file_path)
        elif extension in ['.html', '.htm']:
            return self._convert_html_file(file_path)
        elif extension == '.pdf':
            return self._convert_pdf_file(file_path)
        elif extension == '.docx':
            return self._convert_docx_file(file_path)
        
        # Fallback to textract if available
        if HAS_TEXTRACT:
            return self._convert_with_textract(file_path)
        
        self.logger.warning(f"No suitable converter for file: {file_path}")
        return None
    
    def _read_text_file(self, file_path: str) -> Optional[str]:
        """Read plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Failed to read text file {file_path}: {e}")
            return None
    
    def _convert_html_file(self, file_path: str) -> Optional[str]:
        """Convert HTML file to text."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            return self._html_to_text(html_content)
        except Exception as e:
            self.logger.error(f"Failed to convert HTML file {file_path}: {e}")
            return None
    
    def _convert_pdf_file(self, file_path: str) -> Optional[str]:
        """Convert PDF file to text."""
        if not HAS_PYPDF:
            self.logger.warning("pypdf not available for PDF conversion")
            return None
        
        try:
            reader = PdfReader(file_path)
            text_parts = []
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            return '\n\n'.join(text_parts)
            
        except Exception as e:
            self.logger.error(f"Failed to convert PDF file {file_path}: {e}")
            return None
    
    def _convert_docx_file(self, file_path: str) -> Optional[str]:
        """Convert DOCX file to text."""
        if not HAS_DOCX:
            self.logger.warning("python-docx not available for DOCX conversion")
            return None
        
        try:
            doc = Document(file_path)
            text_parts = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            return '\n\n'.join(text_parts)
            
        except Exception as e:
            self.logger.error(f"Failed to convert DOCX file {file_path}: {e}")
            return None
    
    def _convert_with_textract(self, file_path: str) -> Optional[str]:
        """Convert file using textract library."""
        try:
            text = textract.process(file_path).decode('utf-8', errors='ignore')
            return text
        except Exception as e:
            self.logger.error(f"Textract failed for {file_path}: {e}")
            return None
    
    def process_content_in_text(self, text: str) -> str:
        """
        Process text and automatically fetch/convert any URLs or file paths found.
        
        Args:
            text: Input text that may contain URLs or file paths
            
        Returns:
            Enhanced text with fetched content appended
        """
        enhanced_parts = [text]
        
        # Find URLs in text
        url_pattern = r'https?://[^\s<>"{}|\\^`[\]]+[^\s<>"{}|\\^`[\].,!?;:]'
        urls = re.findall(url_pattern, text)
        
        for url in urls:
            if self.config.VERBOSE_OUTPUT:
                self.logger.info(f"Found URL in text: {url}")
            
            content = self.fetch_url_content(url)
            if content:
                enhanced_parts.append("\n--- Content from " + url + " ---\n" + content + "\n--- End of " + url + " ---\n")
        
        # Find file paths in text (simple heuristic)
        # Look for strings that look like file paths
        path_pattern = r'(?:\.?/|\w:)[^\s<>"{}|\\^`[\]]+\.(?:txt|md|pdf|docx|html|htm)'
        paths = re.findall(path_pattern, text)
        
        for path in paths:
            path = path.strip()
            if self.is_file_path(path):
                if self.config.VERBOSE_OUTPUT:
                    self.logger.info(f"Found file path in text: {path}")
                
                content = self.convert_document_to_text(path)
                if content:
                    enhanced_parts.append("\n--- Content from " + path + " ---\n" + content + "\n--- End of " + path + " ---\n")
        
        # Find image paths in text
        if HAS_ANALYSIS_MODULES:
            image_analyzer = get_image_analyzer()
            if image_analyzer.is_available():
                image_pattern = r'(?:\.?/|\w:)[^\s<>"{}|\\^`[\]]+\.(?:jpg|jpeg|png|gif|bmp|webp|svg|tiff|ico|heic|heif)'
                image_paths = re.findall(image_pattern, text, re.IGNORECASE)
                
                for image_path in image_paths:
                    image_path = image_path.strip()
                    if os.path.exists(image_path) and image_analyzer.is_image_file(image_path):
                        if self.config.VERBOSE_OUTPUT:
                            self.logger.info(f"Found image path in text: {image_path}")
                        
                        image_content = self.analyze_image(image_path)
                        if image_content:
                            enhanced_parts.append("\n--- Image Analysis: " + image_path + " ---\n" + image_content + "\n--- End of image analysis ---\n")
        
        # Find folder paths in text
        if HAS_ANALYSIS_MODULES:
            folder_scanner = get_folder_scanner()
            folder_pattern = r'(?:\.?/|\w:)[^\s<>"{}|\\^`[\]]+/?'
            potential_paths = re.findall(folder_pattern, text)
            
            for path in potential_paths:
                path = path.strip().rstrip('/')
                if os.path.exists(path) and os.path.isdir(path):
                    if self.config.VERBOSE_OUTPUT:
                        self.logger.info(f"Found folder path in text: {path}")
                    
                    folder_content = self.analyze_folder(path)
                    if folder_content:
                        enhanced_parts.append("\n--- Folder Analysis: " + path + " ---\n" + folder_content + "\n--- End of folder analysis ---\n")
        
        return '\n'.join(enhanced_parts)
    
    def analyze_image(self, image_path: str, question: Optional[str] = None) -> Optional[str]:
        """
        Analyze an image using HuggingFace vision models.
        
        Args:
            image_path: Path to image file
            question: Optional question about the image
            
        Returns:
            str: Image analysis text or None if failed
        """
        if not HAS_ANALYSIS_MODULES:
            self.logger.warning("Image analysis not available - missing analysis modules")
            return None
        
        try:
            image_analyzer = get_image_analyzer()
            if not image_analyzer.is_available():
                self.logger.warning("Image analysis not available - missing dependencies")
                return None
            
            result = image_analyzer.analyze_image(image_path, question)
            
            if result.get("error"):
                self.logger.error(f"Image analysis failed: {result['error']}")
                return None
            
            # Format the analysis result
            description = result.get("description", "No description available")
            metadata = result.get("metadata", {})
            
            analysis_text = "🖼️ Image: " + os.path.basename(image_path) + "\n"
            analysis_text += "📝 Description: " + description + "\n"
            
            if metadata:
                if metadata.get("dimensions"):
                    analysis_text += "📐 Size: " + str(metadata['dimensions'][0]) + "x" + str(metadata['dimensions'][1]) + "\n"
                if metadata.get("file_size"):
                    size_mb = metadata['file_size'] / (1024 * 1024)
                    analysis_text += "💾 File Size: " + str(round(size_mb, 1)) + " MB\n"
            
            if question:
                analysis_text += "❓ Question: " + question + "\n"
            
            return analysis_text
            
        except Exception as e:
            self.logger.error(f"Error analyzing image {image_path}: {e}")
            return None
    
    def analyze_folder(self, folder_path: str, max_depth: int = 3) -> Optional[str]:
        """
        Analyze folder structure and contents.
        
        Args:
            folder_path: Path to folder to analyze
            max_depth: Maximum depth to scan
            
        Returns:
            str: Folder analysis text or None if failed
        """
        if not HAS_ANALYSIS_MODULES:
            self.logger.warning("Folder analysis not available - missing analysis modules")
            return None
        
        try:
            folder_scanner = get_folder_scanner()
            summary = folder_scanner.get_folder_summary(folder_path)
            return summary
            
        except Exception as e:
            self.logger.error(f"Error analyzing folder {folder_path}: {e}")
            return None
    
    def process_image_path(self, image_path: str, question: Optional[str] = None) -> str:
        """
        Process image path and return analysis if available.
        
        Args:
            image_path: Path to image file
            question: Optional question about image
            
        Returns:
            str: Processed content
        """
        if not os.path.exists(image_path):
            return f"❌ Image file not found: {image_path}"
        
        analysis = self.analyze_image(image_path, question)
        if analysis:
            return analysis
        else:
            return f"🖼️ Image file: {image_path} (analysis not available)"
    
    def process_folder_path(self, folder_path: str) -> str:
        """
        Process folder path and return analysis if available.
        
        Args:
            folder_path: Path to folder
            
        Returns:
            str: Processed content
        """
        if not os.path.exists(folder_path):
            return f"❌ Folder not found: {folder_path}"
        
        if not os.path.isdir(folder_path):
            return f"❌ Path is not a directory: {folder_path}"
        
        analysis = self.analyze_folder(folder_path)
        if analysis:
            return analysis
        else:
            return f"📁 Folder: {folder_path} (analysis not available)"
    
    def get_processing_summary(self) -> Dict[str, bool]:
        """Get summary of available processing capabilities."""
        summary = {
            'url_fetching': self.config.FETCH_URLS_AUTO,
            'document_conversion': self.config.CONVERT_DOCUMENTS_AUTO,
            'has_magic': HAS_MAGIC,
            'has_textract': HAS_TEXTRACT,
            'has_pypdf': HAS_PYPDF,
            'has_docx': HAS_DOCX,
            'allowed_extensions': self.config.ALLOWED_FILE_EXTENSIONS,
            'blocked_domains': self.config.BLOCKED_DOMAINS
        }
        
        # Add new analysis capabilities
        if HAS_ANALYSIS_MODULES:
            try:
                image_analyzer = get_image_analyzer()
                folder_scanner = get_folder_scanner()
                summary.update({
                    'image_analysis': image_analyzer.is_available(),
                    'folder_scanning': True,
                    'supported_image_formats': list(image_analyzer.supported_formats) if image_analyzer.supported_formats else []
                })
            except Exception as e:
                self.logger.warning(f"Error checking analysis modules: {e}")
                summary.update({
                    'image_analysis': False,
                    'folder_scanning': False
                })
        else:
            summary.update({
                'image_analysis': False,
                'folder_scanning': False
            })
        
        return summary


# Global processor instance
_processor_instance: Optional[ContentProcessor] = None


def get_content_processor() -> ContentProcessor:
    """Get global content processor instance."""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = ContentProcessor()
    return _processor_instance
