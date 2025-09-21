"""
Folder Scanner Module for Bielik

This module provides folder structure analysis and file scanning capabilities.
Generates comprehensive reports about directory contents and structure.
"""

import os
import json
import hashlib
import mimetypes
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from datetime import datetime

from .config import get_config, get_logger


class FolderScanner:
    """
    Folder structure analyzer and scanner.
    Provides detailed analysis of directory contents, structure, and statistics.
    """
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(__name__)
        
        # File categories for analysis
        self.file_categories = {
            'code': {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', 
                    '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.r'},
            'config': {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', 
                      '.env', '.properties', '.xml'},
            'documentation': {'.md', '.rst', '.txt', '.pdf', '.doc', '.docx', '.tex'},
            'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', 
                      '.tiff', '.ico', '.heic', '.heif'},
            'data': {'.csv', '.xlsx', '.xls', '.db', '.sqlite', '.json', '.parquet'},
            'archives': {'.zip', '.tar', '.gz', '.rar', '.7z', '.bz2', '.xz'},
            'media': {'.mp4', '.avi', '.mov', '.wmv', '.mp3', '.wav', '.flac', '.aac'}
        }
        
        # Default ignore patterns
        self.default_ignore = {
            '__pycache__', '.git', '.svn', '.hg', 'node_modules', '.venv', 'venv',
            '.pytest_cache', '.mypy_cache', '.tox', 'dist', 'build', '.egg-info',
            '.DS_Store', 'Thumbs.db', '.env', '.vscode', '.idea'
        }

    def scan_folder(self, folder_path: str, 
                   max_depth: int = 10, 
                   include_hidden: bool = False,
                   ignore_patterns: Optional[Set[str]] = None) -> Dict[str, Any]:
        """
        Scan folder and return comprehensive analysis.
        
        Args:
            folder_path: Path to folder to scan
            max_depth: Maximum depth to recurse
            include_hidden: Whether to include hidden files/folders
            ignore_patterns: Additional patterns to ignore
            
        Returns:
            dict: Complete folder analysis report
        """
        if not os.path.exists(folder_path):
            return {"error": f"Folder not found: {folder_path}"}
        
        if not os.path.isdir(folder_path):
            return {"error": f"Path is not a directory: {folder_path}"}
        
        # Combine ignore patterns
        ignore_set = self.default_ignore.copy()
        if ignore_patterns:
            ignore_set.update(ignore_patterns)
        
        try:
            self.logger.info(f"Scanning folder: {folder_path}")
            start_time = datetime.now()
            
            # Perform the scan
            scan_result = self._recursive_scan(
                folder_path, 0, max_depth, include_hidden, ignore_set
            )
            
            # Generate statistics
            stats = self._generate_statistics(scan_result)
            
            # Generate file type analysis
            file_analysis = self._analyze_file_types(scan_result)
            
            # Generate folder structure tree
            tree_structure = self._generate_tree_structure(scan_result)
            
            scan_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "error": None,
                "folder_path": folder_path,
                "scan_time": scan_time,
                "statistics": stats,
                "file_analysis": file_analysis,
                "structure": scan_result,
                "tree_view": tree_structure,
                "metadata": {
                    "scanned_at": start_time.isoformat(),
                    "max_depth_used": max_depth,
                    "included_hidden": include_hidden,
                    "ignore_patterns": list(ignore_set)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error scanning folder {folder_path}: {e}")
            return {"error": f"Scan failed: {str(e)}"}

    def _recursive_scan(self, path: str, current_depth: int, max_depth: int,
                       include_hidden: bool, ignore_patterns: Set[str]) -> Dict[str, Any]:
        """Recursively scan directory structure."""
        result = {
            "path": path,
            "name": os.path.basename(path),
            "type": "directory",
            "size": 0,
            "files": [],
            "subdirectories": [],
            "file_count": 0,
            "directory_count": 0
        }
        
        if current_depth >= max_depth:
            result["truncated"] = True
            return result
        
        try:
            entries = os.listdir(path)
        except PermissionError:
            result["error"] = "Permission denied"
            return result
        
        for entry in sorted(entries):
            # Skip hidden files if not requested
            if not include_hidden and entry.startswith('.'):
                continue
            
            # Skip ignored patterns
            if entry in ignore_patterns:
                continue
            
            entry_path = os.path.join(path, entry)
            
            try:
                if os.path.isfile(entry_path):
                    file_info = self._get_file_info(entry_path)
                    result["files"].append(file_info)
                    result["file_count"] += 1
                    result["size"] += file_info.get("size", 0)
                    
                elif os.path.isdir(entry_path):
                    subdir_info = self._recursive_scan(
                        entry_path, current_depth + 1, max_depth, 
                        include_hidden, ignore_patterns
                    )
                    result["subdirectories"].append(subdir_info)
                    result["directory_count"] += 1 + subdir_info.get("directory_count", 0)
                    result["file_count"] += subdir_info.get("file_count", 0)
                    result["size"] += subdir_info.get("size", 0)
                    
            except (OSError, PermissionError) as e:
                self.logger.warning(f"Cannot access {entry_path}: {e}")
                continue
        
        return result

    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get detailed information about a file."""
        try:
            stat_info = os.stat(file_path)
            file_ext = Path(file_path).suffix.lower()
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            
            # Categorize file
            category = self._categorize_file(file_ext)
            
            return {
                "name": os.path.basename(file_path),
                "path": file_path,
                "extension": file_ext,
                "size": stat_info.st_size,
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "mime_type": mime_type,
                "category": category,
                "permissions": oct(stat_info.st_mode)[-3:]
            }
        except Exception as e:
            return {
                "name": os.path.basename(file_path),
                "path": file_path,
                "error": str(e)
            }

    def _categorize_file(self, extension: str) -> str:
        """Categorize file based on extension."""
        for category, extensions in self.file_categories.items():
            if extension in extensions:
                return category
        return "other"

    def _generate_statistics(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive statistics from scan results."""
        return {
            "total_files": scan_result.get("file_count", 0),
            "total_directories": scan_result.get("directory_count", 0),
            "total_size": scan_result.get("size", 0),
            "total_size_human": self._format_size(scan_result.get("size", 0)),
            "depth_reached": self._calculate_max_depth(scan_result),
            "largest_files": self._find_largest_files(scan_result, limit=5),
            "file_type_distribution": self._get_file_type_distribution(scan_result)
        }

    def _analyze_file_types(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze file types and provide insights."""
        file_types = {}
        category_stats = {cat: {"count": 0, "size": 0} for cat in self.file_categories.keys()}
        category_stats["other"] = {"count": 0, "size": 0}
        
        def analyze_files(node):
            for file_info in node.get("files", []):
                if "error" in file_info:
                    continue
                
                ext = file_info.get("extension", "")
                category = file_info.get("category", "other")
                size = file_info.get("size", 0)
                
                # Count by extension
                if ext not in file_types:
                    file_types[ext] = {"count": 0, "size": 0}
                file_types[ext]["count"] += 1
                file_types[ext]["size"] += size
                
                # Count by category
                category_stats[category]["count"] += 1
                category_stats[category]["size"] += size
            
            # Recurse into subdirectories
            for subdir in node.get("subdirectories", []):
                analyze_files(subdir)
        
        analyze_files(scan_result)
        
        # Sort and format results
        sorted_types = sorted(file_types.items(), 
                            key=lambda x: x[1]["count"], reverse=True)[:10]
        
        return {
            "by_extension": {ext: {**stats, "size_human": self._format_size(stats["size"])} 
                           for ext, stats in sorted_types},
            "by_category": {cat: {**stats, "size_human": self._format_size(stats["size"])} 
                          for cat, stats in category_stats.items() if stats["count"] > 0}
        }

    def _generate_tree_structure(self, scan_result: Dict[str, Any], 
                                prefix: str = "") -> str:
        """Generate ASCII tree representation of folder structure."""
        tree_lines = []
        
        def add_tree_node(node, prefix, is_last=True):
            # Add current directory
            connector = "└── " if is_last else "├── "
            tree_lines.append(f"{prefix}{connector}{node['name']}/")
            
            # Prepare prefix for children
            child_prefix = prefix + ("    " if is_last else "│   ")
            
            # Add files
            files = node.get("files", [])
            subdirs = node.get("subdirectories", [])
            
            # Show first few files
            for i, file_info in enumerate(files[:5]):  # Limit to first 5 files
                file_is_last = (i == len(files) - 1) and len(subdirs) == 0
                file_connector = "└── " if file_is_last else "├── "
                tree_lines.append(f"{child_prefix}{file_connector}{file_info['name']}")
            
            # Show file count if there are more
            if len(files) > 5:
                tree_lines.append(f"{child_prefix}├── ... ({len(files) - 5} more files)")
            
            # Add subdirectories
            for i, subdir in enumerate(subdirs):
                subdir_is_last = (i == len(subdirs) - 1)
                add_tree_node(subdir, child_prefix, subdir_is_last)
        
        add_tree_node(scan_result, prefix)
        return "\n".join(tree_lines)

    def _calculate_max_depth(self, node: Dict[str, Any], current_depth: int = 0) -> int:
        """Calculate maximum depth reached in scan."""
        max_depth = current_depth
        for subdir in node.get("subdirectories", []):
            subdir_depth = self._calculate_max_depth(subdir, current_depth + 1)
            max_depth = max(max_depth, subdir_depth)
        return max_depth

    def _find_largest_files(self, node: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """Find largest files in the scan results."""
        all_files = []
        
        def collect_files(current_node):
            for file_info in current_node.get("files", []):
                if "error" not in file_info and "size" in file_info:
                    all_files.append(file_info)
            
            for subdir in current_node.get("subdirectories", []):
                collect_files(subdir)
        
        collect_files(node)
        
        # Sort by size and return top files
        largest = sorted(all_files, key=lambda x: x.get("size", 0), reverse=True)[:limit]
        
        # Add human-readable size
        for file_info in largest:
            file_info["size_human"] = self._format_size(file_info.get("size", 0))
        
        return largest

    def _get_file_type_distribution(self, node: Dict[str, Any]) -> Dict[str, int]:
        """Get distribution of file types."""
        distribution = {}
        
        def count_extensions(current_node):
            for file_info in current_node.get("files", []):
                ext = file_info.get("extension", "no_extension")
                distribution[ext] = distribution.get(ext, 0) + 1
            
            for subdir in current_node.get("subdirectories", []):
                count_extensions(subdir)
        
        count_extensions(node)
        return distribution

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        units = ["B", "KB", "MB", "GB", "TB"]
        size = float(size_bytes)
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"

    def get_folder_summary(self, folder_path: str) -> str:
        """Get a concise text summary of folder contents."""
        scan_result = self.scan_folder(folder_path, max_depth=3)
        
        if scan_result.get("error"):
            return f"Error scanning folder: {scan_result['error']}"
        
        stats = scan_result["statistics"]
        file_analysis = scan_result["file_analysis"]
        
        summary_lines = [
            f"📁 Folder Analysis: {folder_path}",
            f"📊 Statistics:",
            f"  - Files: {stats['total_files']}",
            f"  - Directories: {stats['total_directories']}",
            f"  - Total Size: {stats['total_size_human']}",
            f"  - Max Depth: {stats['depth_reached']}",
            "",
            f"🏷️ File Categories:"
        ]
        
        # Add category breakdown
        for category, data in file_analysis["by_category"].items():
            if data["count"] > 0:
                summary_lines.append(f"  - {category.title()}: {data['count']} files ({data['size_human']})")
        
        # Add top file types
        if file_analysis["by_extension"]:
            summary_lines.extend([
                "",
                f"📄 Top File Types:"
            ])
            for ext, data in list(file_analysis["by_extension"].items())[:5]:
                ext_display = ext if ext else "no extension"
                summary_lines.append(f"  - {ext_display}: {data['count']} files")
        
        return "\n".join(summary_lines)


def get_folder_scanner() -> FolderScanner:
    """Get global folder scanner instance."""
    if not hasattr(get_folder_scanner, '_instance'):
        get_folder_scanner._instance = FolderScanner()
    return get_folder_scanner._instance
