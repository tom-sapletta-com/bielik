#!/usr/bin/env python3
"""
Bielik Validation Utilities - Validators for HTML artifacts, .env files, and command scripts.

This module provides comprehensive validation functions for:
- HTML artifacts correctness and metadata integrity
- .env configuration file validation
- Command scripts validation for compliance and correctness
"""

import os
import re
import ast
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    metadata: Dict[str, Any]


class HTMLArtifactValidator:
    """Validates HTML artifacts and their metadata integrity."""
    
    REQUIRED_META_TAGS = [
        'project-name',
        'project-description', 
        'created-at',
        'updated-at',
        'artifacts-count'
    ]
    
    REQUIRED_DATA_ATTRIBUTES = [
        'data-project-id',
        'data-session-id'
    ]
    
    def validate_html_file(self, html_path: Union[str, Path]) -> ValidationResult:
        """
        Validate HTML artifact file for correctness and metadata integrity.
        
        Args:
            html_path: Path to HTML file
            
        Returns:
            ValidationResult with detailed analysis
        """
        html_path = Path(html_path)
        errors = []
        warnings = []
        suggestions = []
        metadata = {}
        
        # Check file exists
        if not html_path.exists():
            return ValidationResult(
                is_valid=False,
                errors=[f"HTML file does not exist: {html_path}"],
                warnings=[],
                suggestions=[],
                metadata={}
            )
        
        # Check file size
        file_size = html_path.stat().st_size
        metadata['file_size_bytes'] = file_size
        
        if file_size == 0:
            errors.append("HTML file is empty")
        elif file_size > 10 * 1024 * 1024:  # 10MB
            warnings.append("HTML file is very large (>10MB)")
        
        # Parse HTML content
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
        except Exception as e:
            errors.append(f"Failed to parse HTML: {str(e)}")
            return ValidationResult(False, errors, warnings, suggestions, metadata)
        
        # Validate HTML structure
        self._validate_html_structure(soup, errors, warnings, suggestions)
        
        # Validate metadata
        self._validate_metadata(soup, errors, warnings, suggestions, metadata)
        
        # Validate artifacts
        self._validate_artifacts(soup, errors, warnings, suggestions, metadata)
        
        # Validate CSS and JavaScript
        self._validate_assets(soup, warnings, suggestions)
        
        # Calculate content hash for integrity
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        metadata['content_hash'] = content_hash
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            metadata=metadata
        )
    
    def _validate_html_structure(self, soup: BeautifulSoup, errors: List[str], 
                                warnings: List[str], suggestions: List[str]):
        """Validate basic HTML structure."""
        # Check DOCTYPE
        if not str(soup).startswith('<!DOCTYPE html>'):
            errors.append("Missing or incorrect DOCTYPE declaration")
        
        # Check required elements
        if not soup.find('html'):
            errors.append("Missing <html> element")
        
        if not soup.find('head'):
            errors.append("Missing <head> element")
        
        if not soup.find('title'):
            warnings.append("Missing <title> element")
        
        if not soup.find('meta', {'charset': True}):
            warnings.append("Missing charset meta tag")
        
        # Check for viewport meta tag
        if not soup.find('meta', {'name': 'viewport'}):
            suggestions.append("Consider adding viewport meta tag for mobile compatibility")
    
    def _validate_metadata(self, soup: BeautifulSoup, errors: List[str],
                          warnings: List[str], suggestions: List[str], 
                          metadata: Dict[str, Any]):
        """Validate project metadata in HTML."""
        html_element = soup.find('html')
        
        # Check required data attributes on html element
        for attr in self.REQUIRED_DATA_ATTRIBUTES:
            if not html_element or not html_element.get(attr):
                errors.append(f"Missing required attribute '{attr}' on <html> element")
        
        # Extract and validate metadata
        if html_element:
            project_id = html_element.get('data-project-id')
            session_id = html_element.get('data-session-id')
            
            metadata['project_id'] = project_id
            metadata['session_id'] = session_id
            
            # Validate UUID format
            uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            if project_id and not re.match(uuid_pattern, project_id):
                errors.append("Invalid project ID format (should be UUID)")
            if session_id and not re.match(uuid_pattern, session_id):
                errors.append("Invalid session ID format (should be UUID)")
        
        # Check required meta tags
        for meta_name in self.REQUIRED_META_TAGS:
            meta_tag = soup.find('meta', {'name': meta_name})
            if not meta_tag:
                errors.append(f"Missing required meta tag: {meta_name}")
            else:
                content = meta_tag.get('content', '')
                metadata[meta_name] = content
                
                # Validate specific meta tag formats
                if meta_name in ['created-at', 'updated-at']:
                    if not self._validate_iso_datetime(content):
                        errors.append(f"Invalid datetime format in {meta_name}: {content}")
                elif meta_name == 'artifacts-count':
                    try:
                        count = int(content)
                        if count < 0:
                            errors.append("Artifacts count cannot be negative")
                    except ValueError:
                        errors.append(f"Invalid artifacts count: {content}")
    
    def _validate_artifacts(self, soup: BeautifulSoup, errors: List[str],
                           warnings: List[str], suggestions: List[str],
                           metadata: Dict[str, Any]):
        """Validate artifact elements and their metadata."""
        artifacts = soup.find_all('div', {'class': 'artifact'})
        metadata['found_artifacts'] = len(artifacts)
        
        # Get declared artifacts count
        meta_count = soup.find('meta', {'name': 'artifacts-count'})
        declared_count = int(meta_count.get('content', 0)) if meta_count else 0
        
        if len(artifacts) != declared_count:
            errors.append(f"Artifacts count mismatch: found {len(artifacts)}, declared {declared_count}")
        
        artifact_ids = set()
        for i, artifact in enumerate(artifacts):
            artifact_id = artifact.get('data-artifact-id')
            artifact_type = artifact.get('data-artifact-type')
            created_at = artifact.get('data-created-at')
            checksum = artifact.get('data-checksum')
            size_bytes = artifact.get('data-size-bytes')
            
            # Check required attributes
            if not artifact_id:
                errors.append(f"Artifact {i} missing data-artifact-id")
            elif artifact_id in artifact_ids:
                errors.append(f"Duplicate artifact ID: {artifact_id}")
            else:
                artifact_ids.add(artifact_id)
            
            if not artifact_type:
                errors.append(f"Artifact {i} missing data-artifact-type")
            
            if not created_at:
                errors.append(f"Artifact {i} missing data-created-at")
            elif not self._validate_iso_datetime(created_at):
                errors.append(f"Invalid datetime in artifact {i}: {created_at}")
            
            # Validate content structure
            content_div = artifact.find('div', {'class': 'artifact-content'})
            if not content_div:
                warnings.append(f"Artifact {i} missing content div")
    
    def _validate_assets(self, soup: BeautifulSoup, warnings: List[str], 
                        suggestions: List[str]):
        """Validate CSS and JavaScript assets."""
        # Check for inline styles
        style_tags = soup.find_all('style')
        if len(style_tags) > 1:
            suggestions.append("Consider consolidating multiple <style> tags")
        
        # Check for inline scripts
        script_tags = soup.find_all('script')
        if len(script_tags) > 2:
            suggestions.append("Consider consolidating JavaScript code")
        
        # Check for external resources
        external_css = soup.find_all('link', {'rel': 'stylesheet'})
        external_js = soup.find_all('script', {'src': True})
        
        if external_css:
            warnings.append("External CSS dependencies detected - may affect offline viewing")
        if external_js:
            warnings.append("External JavaScript dependencies detected - may affect offline viewing")
    
    def _validate_iso_datetime(self, datetime_str: str) -> bool:
        """Validate ISO datetime format."""
        try:
            from datetime import datetime
            datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False


class EnvFileValidator:
    """Validates .env configuration files."""
    
    REQUIRED_SECTIONS = [
        'Ollama Server Configuration',
        'Logging Configuration', 
        'Content Processing',
        'Security Settings',
        'Performance Settings',
        'Development Settings',
        'Bielik CLI Settings'
    ]
    
    CRITICAL_VARIABLES = [
        'OLLAMA_HOST',
        'LOG_LEVEL',
        'CONTENT_MAX_SIZE',
        'API_RATE_LIMIT',
        'BIELIK_MODEL'
    ]
    
    def validate_env_file(self, env_path: Union[str, Path]) -> ValidationResult:
        """
        Validate .env configuration file.
        
        Args:
            env_path: Path to .env file
            
        Returns:
            ValidationResult with detailed analysis
        """
        env_path = Path(env_path)
        errors = []
        warnings = []
        suggestions = []
        metadata = {}
        
        # Check file exists
        if not env_path.exists():
            return ValidationResult(
                is_valid=False,
                errors=[f".env file does not exist: {env_path}"],
                warnings=[],
                suggestions=[],
                metadata={}
            )
        
        # Parse .env file
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            errors.append(f"Failed to read .env file: {str(e)}")
            return ValidationResult(False, errors, warnings, suggestions, metadata)
        
        lines = content.split('\n')
        metadata['total_lines'] = len(lines)
        
        # Parse variables and sections
        variables = {}
        sections = []
        current_section = None
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check for section headers (comments starting with #)
            if line.startswith('#'):
                # Remove # and clean up
                section_name = line.lstrip('#').strip()
                if section_name and not section_name.startswith(' '):
                    sections.append(section_name)
                    current_section = section_name
                continue
            
            # Parse variable assignments
            if '=' in line:
                try:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    variables[key] = {
                        'value': value,
                        'line': line_num,
                        'section': current_section
                    }
                    
                except Exception:
                    errors.append(f"Invalid variable assignment at line {line_num}: {line}")
            else:
                warnings.append(f"Unrecognized line format at line {line_num}: {line}")
        
        metadata['variables_count'] = len(variables)
        metadata['sections_found'] = sections
        
        # Validate sections
        self._validate_sections(sections, errors, warnings, suggestions)
        
        # Validate variables
        self._validate_variables(variables, errors, warnings, suggestions, metadata)
        
        # Check for duplicates
        self._check_duplicates(content, errors, warnings)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            metadata=metadata
        )
    
    def _validate_sections(self, sections: List[str], errors: List[str],
                          warnings: List[str], suggestions: List[str]):
        """Validate presence of required sections."""
        found_sections = set(sections)
        
        for required_section in self.REQUIRED_SECTIONS:
            if not any(required_section in section for section in found_sections):
                warnings.append(f"Missing recommended section: {required_section}")
    
    def _validate_variables(self, variables: Dict[str, Dict], errors: List[str],
                           warnings: List[str], suggestions: List[str],
                           metadata: Dict[str, Any]):
        """Validate individual variables."""
        found_vars = set(variables.keys())
        
        # Check critical variables
        for critical_var in self.CRITICAL_VARIABLES:
            if critical_var not in found_vars:
                errors.append(f"Missing critical variable: {critical_var}")
        
        # Validate specific variable formats
        for var_name, var_info in variables.items():
            value = var_info['value']
            
            # Validate URLs
            if var_name.endswith('_HOST') or var_name.endswith('_URL'):
                if not self._validate_url_format(value):
                    errors.append(f"Invalid URL format for {var_name}: {value}")
            
            # Validate log levels
            if var_name == 'LOG_LEVEL':
                valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
                if value.upper() not in valid_levels:
                    errors.append(f"Invalid log level: {value}")
            
            # Validate boolean values
            if var_name.startswith('ENABLE_') or var_name.endswith('_ENABLED'):
                if value.lower() not in ['true', 'false', '1', '0', 'yes', 'no']:
                    warnings.append(f"Potentially invalid boolean value for {var_name}: {value}")
            
            # Validate numeric values
            if any(keyword in var_name for keyword in ['SIZE', 'LIMIT', 'TIMEOUT', 'PORT']):
                try:
                    float(value)
                except ValueError:
                    errors.append(f"Invalid numeric value for {var_name}: {value}")
        
        metadata['critical_vars_found'] = sum(1 for var in self.CRITICAL_VARIABLES if var in found_vars)
    
    def _check_duplicates(self, content: str, errors: List[str], warnings: List[str]):
        """Check for duplicate variable definitions."""
        lines = content.split('\n')
        variables_seen = {}
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key = line.split('=', 1)[0].strip()
                if key in variables_seen:
                    errors.append(f"Duplicate variable definition '{key}' at lines {variables_seen[key]} and {line_num}")
                else:
                    variables_seen[key] = line_num
    
    def _validate_url_format(self, url: str) -> bool:
        """Validate URL format."""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))


class CommandScriptValidator:
    """Validates command scripts in the commands/ directory."""
    
    REQUIRED_IMPORTS = [
        'from bielik.cli.command_api import'
    ]
    
    REQUIRED_CLASSES = [
        'ContextProviderCommand', 'CommandBase'
    ]
    
    def validate_command_script(self, script_path: Union[str, Path]) -> ValidationResult:
        """
        Validate command script for compliance and correctness.
        
        Args:
            script_path: Path to command script file
            
        Returns:
            ValidationResult with detailed analysis
        """
        script_path = Path(script_path)
        errors = []
        warnings = []
        suggestions = []
        metadata = {}
        
        # Check file exists and is Python file
        if not script_path.exists():
            return ValidationResult(
                is_valid=False,
                errors=[f"Script file does not exist: {script_path}"],
                warnings=[],
                suggestions=[],
                metadata={}
            )
        
        if script_path.suffix != '.py':
            errors.append(f"Script file should have .py extension: {script_path}")
        
        # Parse Python code
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST for structural analysis
            tree = ast.parse(content)
        except SyntaxError as e:
            errors.append(f"Python syntax error: {str(e)}")
            return ValidationResult(False, errors, warnings, suggestions, metadata)
        except Exception as e:
            errors.append(f"Failed to parse Python file: {str(e)}")
            return ValidationResult(False, errors, warnings, suggestions, metadata)
        
        # Analyze code structure
        self._analyze_imports(tree, content, errors, warnings, suggestions, metadata)
        self._analyze_classes(tree, content, errors, warnings, suggestions, metadata)
        self._analyze_methods(tree, content, errors, warnings, suggestions, metadata)
        self._check_code_quality(content, warnings, suggestions)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            metadata=metadata
        )
    
    def _analyze_imports(self, tree: ast.AST, content: str, errors: List[str],
                        warnings: List[str], suggestions: List[str], 
                        metadata: Dict[str, Any]):
        """Analyze import statements."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for name in node.names:
                    imports.append(f"from {module} import {name.name}")
        
        metadata['imports'] = imports
        
        # Check for required imports
        has_required_import = False
        for required in self.REQUIRED_IMPORTS:
            if any(required in imp for imp in imports):
                has_required_import = True
                break
        
        if not has_required_import:
            errors.append("Missing required import from bielik.cli.command_api")
        
        # Check import order (PEP 8)
        import_lines = [line.strip() for line in content.split('\n') 
                       if line.strip().startswith(('import ', 'from '))]
        if import_lines:
            # Standard library should come first
            std_imports = [imp for imp in import_lines if not any(
                keyword in imp for keyword in ['bielik', 'third_party', '.'])]
            third_party = [imp for imp in import_lines if imp not in std_imports 
                          and 'bielik' not in imp]
            local_imports = [imp for imp in import_lines if 'bielik' in imp]
            
            if len(std_imports) > 0 and len(local_imports) > 0:
                # Check if there's proper separation
                suggestions.append("Consider organizing imports: standard library, third-party, local imports")
    
    def _analyze_classes(self, tree: ast.AST, content: str, errors: List[str],
                        warnings: List[str], suggestions: List[str],
                        metadata: Dict[str, Any]):
        """Analyze class definitions."""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                base_classes = [base.id for base in node.bases 
                               if hasattr(base, 'id')]
                classes.append({
                    'name': node.name,
                    'bases': base_classes,
                    'methods': [method.name for method in node.body 
                               if isinstance(method, ast.FunctionDef)]
                })
        
        metadata['classes'] = classes
        
        # Check for required base class
        has_valid_base = False
        main_command_class = None
        
        for cls in classes:
            if any(base in self.REQUIRED_CLASSES for base in cls['bases']):
                has_valid_base = True
                main_command_class = cls
                break
        
        if not has_valid_base:
            errors.append("No class inheriting from ContextProviderCommand or CommandBase found")
        
        # Validate main command class
        if main_command_class:
            if 'ContextProviderCommand' in main_command_class['bases']:
                if 'provide_context' not in main_command_class['methods']:
                    errors.append("ContextProviderCommand must implement provide_context method")
            
            if '__init__' not in main_command_class['methods']:
                warnings.append("Command class should have __init__ method")
    
    def _analyze_methods(self, tree: ast.AST, content: str, errors: List[str],
                        warnings: List[str], suggestions: List[str],
                        metadata: Dict[str, Any]):
        """Analyze method implementations."""
        methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                methods.append({
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'has_docstring': ast.get_docstring(node) is not None,
                    'line_count': node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                })
        
        metadata['methods'] = methods
        
        # Check for docstrings
        methods_without_docs = [m for m in methods if not m['has_docstring'] and not m['name'].startswith('_')]
        if methods_without_docs:
            suggestions.append(f"Consider adding docstrings to: {', '.join(m['name'] for m in methods_without_docs)}")
    
    def _check_code_quality(self, content: str, warnings: List[str], 
                           suggestions: List[str]):
        """Check general code quality metrics."""
        lines = content.split('\n')
        
        # Check line length (PEP 8)
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 88]
        if long_lines:
            suggestions.append(f"Lines exceed 88 characters: {', '.join(map(str, long_lines[:5]))}")
        
        # Check for TODO/FIXME comments
        todo_lines = [i+1 for i, line in enumerate(lines) 
                     if any(keyword in line.upper() for keyword in ['TODO', 'FIXME', 'HACK'])]
        if todo_lines:
            warnings.append(f"Found TODO/FIXME comments at lines: {', '.join(map(str, todo_lines))}")


# Convenience functions
def validate_html_artifact(html_path: Union[str, Path]) -> ValidationResult:
    """Validate HTML artifact file."""
    return HTMLArtifactValidator().validate_html_file(html_path)


def validate_env_file(env_path: Union[str, Path]) -> ValidationResult:
    """Validate .env configuration file."""
    return EnvFileValidator().validate_env_file(env_path)


def validate_command_script(script_path: Union[str, Path]) -> ValidationResult:
    """Validate command script file."""
    return CommandScriptValidator().validate_command_script(script_path)
