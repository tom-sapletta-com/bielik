#!/usr/bin/env python3
"""
PDF and Document Reader Command - Extract text from various document formats.

This command provides comprehensive document processing capabilities including
PDF, DOCX, TXT, and other common document formats with MCP integration.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import the command API from the parent package
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from bielik.cli.command_api import ContextProviderCommand

# Import document processing libraries
try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    from docx import Document
    HAS_PYTHON_DOCX = True
except ImportError:
    HAS_PYTHON_DOCX = False

try:
    import textract
    HAS_TEXTRACT = True
except ImportError:
    HAS_TEXTRACT = False


class DocumentReaderCommand(ContextProviderCommand):
    """Advanced document reader with multiple format support and Context Provider integration."""
    
    def __init__(self):
        super().__init__()
        self.name = "pdf"
        self.description = "Extract text from PDF, DOCX, TXT and other document formats"
        
        # Supported file extensions
        self.supported_extensions = {
            '.pdf': self._read_pdf,
            '.docx': self._read_docx,
            '.doc': self._read_doc_with_textract,
            '.txt': self._read_txt,
            '.md': self._read_txt,
            '.rtf': self._read_rtf_with_textract,
            '.odt': self._read_odt_with_textract,
        }
    
    def provide_context(self, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate context data from document processing operations.
        
        Args:
            args: Command arguments (e.g., ['pdf:', 'document.pdf'])
            context: Current context data
            
        Returns:
            Dictionary with document content and metadata
        """
        if len(args) < 2:  # args[0] is 'pdf:'
            return {
                "error": "Please provide a file path",
                "help": "Usage: pdf: document.pdf",
                "document": None,
                "content": None
            }
        
        # Handle special commands
        if args[1].lower() in ['help', '?']:
            return {
                "type": "help",
                "content": self.get_help(),
                "document": None
            }
        elif args[1].lower() == 'formats':
            return {
                "type": "formats_list",
                "content": self._list_supported_formats(),
                "document": None
            }
        
        file_path = args[1]
        
        # Additional options
        options = {
            'page_range': None,
            'output_format': 'text',
            'include_metadata': False
        }
        
        # Parse additional arguments
        for i, arg in enumerate(args[2:], start=2):
            if arg.startswith('--pages='):
                try:
                    page_range = arg.split('=')[1]
                    if '-' in page_range:
                        start, end = map(int, page_range.split('-'))
                        options['page_range'] = (start - 1, end)  # Convert to 0-based
                    else:
                        page_num = int(page_range)
                        options['page_range'] = (page_num - 1, page_num)
                except ValueError:
                    return {
                        "type": "error",
                        "error": f"Invalid page range: {page_range}",
                        "document": None,
                        "content": None
                    }
            elif arg == '--metadata':
                options['include_metadata'] = True
            elif arg.startswith('--format='):
                options['output_format'] = arg.split('=')[1]
        
        try:
            # Validate file path
            is_valid, error_msg = self.validate_file_path(file_path)
            if not is_valid:
                return {
                    "type": "error",
                    "error": error_msg,
                    "document": file_path,
                    "content": None
                }
            
            # Get file info
            file_size = self.get_file_size(file_path)
            file_ext = self.get_file_extension(file_path)
            
            # Check if format is supported
            if file_ext not in self.supported_extensions:
                return {
                    "type": "error",
                    "error": f"Unsupported file format: {file_ext}",
                    "help": "Use 'pdf: formats' to see supported formats",
                    "document": file_path,
                    "content": None
                }
            
            # Extract text using appropriate method
            result = self._extract_text(file_path, file_ext, options)
            
            # Get metadata if requested
            metadata = None
            if options['include_metadata']:
                metadata = self._get_metadata(file_path, file_ext)
            
            # Format output
            output = [f"📄 Document: {Path(file_path).name}"]
            output.append(f"📊 Size: {self._format_file_size(file_size)}")
            output.append(f"📝 Format: {file_ext.upper()}")
            
            if metadata:
                output.append("📋 Metadata:")
                for key, value in metadata.items():
                    output.append(f"  {key}: {value}")
            
            output.append("-" * 50)
            output.append(result)
            
            return {
                "type": "document",
                "document": {
                    "path": file_path,
                    "name": Path(file_path).name,
                    "size": file_size,
                    "format": file_ext.upper(),
                    "extension": file_ext
                },
                "content": result,
                "metadata": metadata,
                "formatted_result": "\n".join(output),
                "options": options,
                "success": True
            }
            
        except Exception as e:
            return {
                "type": "error",
                "document": file_path,
                "error": str(e),
                "formatted_result": f"❌ Failed to process document: {str(e)}",
                "success": False
            }
    
    def _extract_text(self, file_path: str, file_ext: str, options: Dict[str, Any]) -> str:
        """Extract text from document using appropriate method."""
        reader_func = self.supported_extensions.get(file_ext)
        if not reader_func:
            raise ValueError(f"No reader available for {file_ext}")
        
        return reader_func(file_path, options)
    
    def _read_pdf(self, file_path: str, options: Dict[str, Any]) -> str:
        """Read PDF file using pypdf."""
        if not HAS_PYPDF:
            return "❌ pypdf not installed. Install with: pip install pypdf"
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                # Determine page range
                total_pages = len(pdf_reader.pages)
                if options['page_range']:
                    start, end = options['page_range']
                    start = max(0, start)
                    end = min(total_pages, end)
                else:
                    start, end = 0, total_pages
                
                # Extract text from specified pages
                text_parts = []
                for page_num in range(start, end):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text.strip():
                        if options['output_format'] == 'markdown':
                            text_parts.append(f"## Page {page_num + 1}\n\n{page_text}\n")
                        else:
                            text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}\n")
                
                if not text_parts:
                    return "⚠️ No text content found in the specified pages"
                
                return "\n".join(text_parts)
                
        except Exception as e:
            raise Exception(f"PDF reading failed: {e}")
    
    def _read_docx(self, file_path: str, options: Dict[str, Any]) -> str:
        """Read DOCX file using python-docx."""
        if not HAS_PYTHON_DOCX:
            return "❌ python-docx not installed. Install with: pip install python-docx"
        
        try:
            doc = Document(file_path)
            
            paragraphs = []
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if text:
                    paragraphs.append(text)
            
            if not paragraphs:
                return "⚠️ No text content found in the document"
            
            if options['output_format'] == 'markdown':
                return "\n\n".join(paragraphs)
            else:
                return "\n".join(paragraphs)
                
        except Exception as e:
            raise Exception(f"DOCX reading failed: {e}")
    
    def _read_txt(self, file_path: str, options: Dict[str, Any]) -> str:
        """Read plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if not content.strip():
                return "⚠️ File is empty"
            
            return content
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin1') as file:
                    content = file.read()
                return content
            except Exception as e:
                raise Exception(f"Text file reading failed: {e}")
        except Exception as e:
            raise Exception(f"Text file reading failed: {e}")
    
    def _read_doc_with_textract(self, file_path: str, options: Dict[str, Any]) -> str:
        """Read DOC file using textract."""
        return self._use_textract(file_path)
    
    def _read_rtf_with_textract(self, file_path: str, options: Dict[str, Any]) -> str:
        """Read RTF file using textract."""
        return self._use_textract(file_path)
    
    def _read_odt_with_textract(self, file_path: str, options: Dict[str, Any]) -> str:
        """Read ODT file using textract."""
        return self._use_textract(file_path)
    
    def _use_textract(self, file_path: str) -> str:
        """Use textract for various file formats."""
        if not HAS_TEXTRACT:
            return "❌ textract not installed. Install with: pip install 'bielik[local]'"
        
        try:
            text = textract.process(file_path).decode('utf-8')
            if not text.strip():
                return "⚠️ No text content found in the document"
            return text
        except Exception as e:
            raise Exception(f"Textract processing failed: {e}")
    
    def _get_metadata(self, file_path: str, file_ext: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from document."""
        metadata = {}
        
        if file_ext == '.pdf' and HAS_PYPDF:
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = pypdf.PdfReader(file)
                    if pdf_reader.metadata:
                        for key, value in pdf_reader.metadata.items():
                            if value:
                                metadata[key[1:]] = str(value)  # Remove leading '/'
                    metadata['Pages'] = len(pdf_reader.pages)
            except:
                pass
        
        # Add file system metadata
        path = Path(file_path)
        stat = path.stat()
        metadata['File Size'] = self._format_file_size(stat.st_size)
        metadata['Modified'] = self._format_timestamp(stat.st_mtime)
        
        return metadata if metadata else None
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def _format_timestamp(self, timestamp: float) -> str:
        """Format timestamp in readable format."""
        import datetime
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    def _list_supported_formats(self) -> str:
        """List supported file formats."""
        formats = []
        for ext in sorted(self.supported_extensions.keys()):
            formats.append(f"  {ext.upper()} - {self._get_format_description(ext)}")
        
        return "📄 Supported Document Formats:\n" + "\n".join(formats)
    
    def _get_format_description(self, ext: str) -> str:
        """Get description for file format."""
        descriptions = {
            '.pdf': 'Portable Document Format',
            '.docx': 'Microsoft Word Document',
            '.doc': 'Microsoft Word Document (legacy)',
            '.txt': 'Plain Text File',
            '.md': 'Markdown Document',
            '.rtf': 'Rich Text Format',
            '.odt': 'OpenDocument Text',
        }
        return descriptions.get(ext, 'Document file')
    
    def get_help(self) -> str:
        """Return help text for PDF/document reader command."""
        return """📄 Document Reader Command Help

Usage:
  pdf: <file_path>                    # Extract all text from document
  pdf: document.pdf --pages=1-5       # Extract text from pages 1-5
  pdf: document.pdf --pages=3         # Extract text from page 3 only
  pdf: document.docx --metadata       # Include document metadata
  pdf: document.txt --format=markdown # Output in markdown format

Supported Formats:
  • PDF (.pdf) - Using pypdf
  • Microsoft Word (.docx, .doc) - Using python-docx/textract
  • Plain Text (.txt, .md) - Direct reading
  • Rich Text (.rtf) - Using textract
  • OpenDocument (.odt) - Using textract

Special Commands:
  pdf: formats                        # List supported formats
  pdf: help                          # Show this help

Options:
  --pages=N or --pages=N-M           # Specify page range (PDF only)
  --metadata                         # Include document metadata
  --format=text|markdown             # Output format

Examples:
  pdf: ~/Documents/report.pdf
  pdf: presentation.pdf --pages=1-10 --metadata
  pdf: article.docx --format=markdown
  pdf: spreadsheet.txt

Dependencies:
  • pypdf (for PDF files)
  • python-docx (for DOCX files)  
  • textract (for DOC, RTF, ODT files)

Context Provider Integration:
  This command provides rich context data for document processing
  and integrates seamlessly with the Context Provider system.
"""

    def get_usage(self) -> str:
        """Return usage example."""
        return "pdf: <file_path> [--pages=N-M] [--metadata] [--format=text|markdown]"
    
    def validate_file_path(self, file_path: str) -> tuple[bool, str]:
        """Validate if file path exists and is accessible."""
        try:
            path = Path(file_path).expanduser().resolve()
            if not path.exists():
                return False, f"File not found: {file_path}"
            if not path.is_file():
                return False, f"Path is not a file: {file_path}"
            if not os.access(path, os.R_OK):
                return False, f"File is not readable: {file_path}"
            return True, ""
        except Exception as e:
            return False, f"Invalid file path: {e}"
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        try:
            return Path(file_path).expanduser().resolve().stat().st_size
        except Exception:
            return 0
    
    def get_file_extension(self, file_path: str) -> str:
        """Get file extension in lowercase."""
        return Path(file_path).suffix.lower()
