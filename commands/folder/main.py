#!/usr/bin/env python3
"""
Folder Command - Context Provider for directory analysis.

This command analyzes directory contents and provides structured context
for AI processing. Usage: folder: ~/documents
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from bielik.cli.command_api import ContextProviderCommand


class FolderCommand(ContextProviderCommand):
    """Directory analysis context provider."""
    
    def __init__(self):
        super().__init__()
        self.description = "Analyze directory contents and provide context for AI processing"
    
    def provide_context(self, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze directory and provide structured context data.
        
        Args:
            args: ['folder:', 'path/to/directory']
            context: Current context
            
        Returns:
            Dictionary with directory analysis data
        """
        if len(args) < 2:
            return {"error": "Please provide a directory path: folder: ~/documents"}
        
        # Extract path (skip 'folder:' command name)
        dir_path = args[1]
        
        # Expand user home directory
        if dir_path.startswith('~'):
            dir_path = os.path.expanduser(dir_path)
        
        # Convert to absolute path
        dir_path = os.path.abspath(dir_path)
        
        if not os.path.exists(dir_path):
            return {"error": f"Directory does not exist: {dir_path}"}
        
        if not os.path.isdir(dir_path):
            return {"error": f"Path is not a directory: {dir_path}"}
        
        try:
            # Analyze directory contents
            analysis = self._analyze_directory(dir_path)
            return {
                "directory_path": dir_path,
                "analysis": analysis,
                "context_type": "directory_analysis"
            }
        except PermissionError:
            return {"error": f"Permission denied accessing directory: {dir_path}"}
        except Exception as e:
            return {"error": f"Error analyzing directory: {str(e)}"}
    
    def _analyze_directory(self, dir_path: str) -> Dict[str, Any]:
        """Perform detailed directory analysis."""
        
        path_obj = Path(dir_path)
        files = []
        folders = []
        file_types = {}
        total_size = 0
        
        try:
            # Scan directory contents
            for item in path_obj.iterdir():
                try:
                    if item.is_file():
                        file_info = {
                            "name": item.name,
                            "size": item.stat().st_size,
                            "extension": item.suffix.lower(),
                            "modified": item.stat().st_mtime
                        }
                        files.append(file_info)
                        total_size += file_info["size"]
                        
                        # Count file types
                        ext = item.suffix.lower() or '.no_extension'
                        file_types[ext] = file_types.get(ext, 0) + 1
                        
                    elif item.is_dir():
                        # Analyze subdirectory (one level deep)
                        try:
                            subdir_count = len(list(item.iterdir()))
                        except PermissionError:
                            subdir_count = "Permission denied"
                        
                        folder_info = {
                            "name": item.name,
                            "item_count": subdir_count
                        }
                        folders.append(folder_info)
                        
                except (PermissionError, OSError):
                    # Skip items we can't access
                    continue
        
        except PermissionError:
            return {"error": "Permission denied scanning directory"}
        
        # Sort files by name
        files.sort(key=lambda x: x["name"].lower())
        folders.sort(key=lambda x: x["name"].lower())
        
        # Generate summary
        summary = {
            "total_files": len(files),
            "total_folders": len(folders),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types,
            "largest_files": sorted(files, key=lambda x: x["size"], reverse=True)[:5]
        }
        
        return {
            "summary": summary,
            "files": files[:50],  # Limit to first 50 files
            "folders": folders[:20],  # Limit to first 20 folders
            "file_types_distribution": file_types
        }
    
    def get_help(self) -> str:
        """Return detailed help for folder command."""
        return """📁 Folder Context Provider

Analyzes directory contents and provides structured context for AI processing.

Usage:
  folder: ~/documents                # Analyze home documents folder
  folder: /path/to/project           # Analyze project directory
  folder: .                          # Analyze current directory
  folder: ../parent                  # Analyze parent directory

The command analyzes:
  • File and folder counts
  • File types distribution
  • Directory size statistics
  • Largest files
  • Directory structure overview

After running this command, you can ask the AI questions like:
  "What types of files are in this directory?"
  "Show me the largest files"
  "Summarize the project structure"
  "Find Python files in this directory"

Example conversation:
  User: folder: ~/projects/myapp
  AI: [Analyzes directory structure]
  User: What Python files are in this project?
  AI: [Uses the directory context to answer]
"""

    def get_usage(self) -> str:
        """Return usage example."""
        return "folder: <directory_path>"


# Export the command class
command_class = FolderCommand
