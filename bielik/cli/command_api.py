#!/usr/bin/env python3
"""
Bielik CLI Command API SDK - Framework for creating extensible commands.

This module provides the base classes and utilities for creating custom
commands that can be dynamically loaded by the CLI.
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path


class CommandBase(ABC):
    """Base class for all CLI commands."""
    
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace('command', '')
        self.description = getattr(self, '__doc__', 'No description available')
        self.is_context_provider = False  # False = direct command (:calc), True = context provider (folder:)
    
    @abstractmethod
    def execute(self, args: List[str], context: Dict[str, Any]) -> str:
        """
        Execute the command with given arguments.
        
        Args:
            args: Command line arguments (e.g., [':calc', '2', '+', '3'] or ['folder:', '~/documents'])
            context: Context data including current_model, messages, etc.
            
        Returns:
            Command output as string (direct) or context data (for context providers)
        """
        pass
    
    @abstractmethod
    def get_help(self) -> str:
        """Return help text for this command."""
        pass
    
    def get_usage(self) -> str:
        """Return usage example for this command."""
        if self.is_context_provider:
            return f"{self.name}: <args>"
        return f":{self.name} <args>"


class ContextProviderCommand(CommandBase):
    """Base class for context provider commands (format: 'name: args')."""
    
    def __init__(self):
        super().__init__()
        self.is_context_provider = True
    
    @abstractmethod
    def provide_context(self, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate context data from the given arguments.
        
        Args:
            args: Command arguments (e.g., ['folder:', '~/documents'])
            context: Current context data
            
        Returns:
            Dictionary with context data to be used by AI
        """
        pass
    
    def execute(self, args: List[str], context: Dict[str, Any]) -> str:
        """
        Execute context provider command - generates context data.
        
        Returns formatted context data as string for AI consumption.
        """
        context_data = self.provide_context(args, context)
        
        # Format context data for AI consumption
        if context_data:
            formatted = "\n=== Context from " + self.name + ": ===\n"
            for key, value in context_data.items():
                formatted += key + ": " + str(value) + "\n"
            formatted += "=== End Context ===\n"
            
            # Auto-add artifact to current project if one exists
            try:
                from bielik.project_manager import get_project_manager
                project_manager = get_project_manager()
                
                if project_manager.current_project_id:
                    # Create command string from args
                    command_str = " ".join(args) if args else f"{self.name}:"
                    
                    # Add artifact to current project
                    artifact_id = project_manager.add_artifact(
                        command_type=self.name,
                        command=command_str,
                        content=formatted,
                        name=f"{self.name}_{len(project_manager.artifacts.get(project_manager.current_project_id, []))+1}"
                    )
                    
                    # Add project info to the output
                    project = project_manager.projects[project_manager.current_project_id]
                    formatted += "\n🎯 **Artifact Added to Project:** " + project.name + "\n"
                    formatted += "🆔 **Artifact ID:** " + artifact_id[:8] + "...\n"
                    formatted += "📊 **Total Artifacts:** " + str(project.artifacts_count) + "\n"
                    formatted += "💡 **View Project:** `:project open`\n"
                
                else:
                    formatted += "\n💡 **Create a project to save this artifact:** `:project create \"My Analysis\"`\n"
                    
            except ImportError:
                # Project manager not available, continue without it
                pass
            except Exception as e:
                # Don't fail the command if project management fails
                formatted += "\n⚠️ **Project management error:** " + str(e) + "\n"
            
            return formatted
        
        return f"No context data generated from {self.name}: command"
    
    def get_help(self) -> str:
        """Default help implementation for context providers."""
        return f"""📊 {self.name.title()} Context Provider

{self.description}

Usage: {self.get_usage()}

This is a context provider command that generates structured data 
for AI analysis. After running this command, you can ask the AI 
questions related to the generated context.
"""


class MCPCommand(CommandBase):
    """Base class for commands that use MCP protocol."""
    
    def __init__(self):
        super().__init__()
        self.mcp_client = None
    
    def init_mcp(self, server_name: str, resource_uri: Optional[str] = None):
        """Initialize MCP client connection."""
        try:
            # This will be implemented when MCP integration is ready
            self.mcp_client = f"mcp://{server_name}"
            if resource_uri:
                self.mcp_client += f"/{resource_uri}"
        except Exception as e:
            print(f"⚠️ MCP initialization failed: {e}")
    
    def call_mcp_resource(self, resource_path: str, params: Dict[str, Any] = None) -> Any:
        """Call MCP resource."""
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized")
        
        # Placeholder for MCP protocol implementation
        return {"status": "success", "data": f"MCP call to {resource_path}"}


class FileCommand(CommandBase):
    """Base class for commands that work with files."""
    
    def validate_file_path(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate file path exists and is readable.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_path:
            return False, "File path is required"
        
        path = Path(file_path)
        if not path.exists():
            return False, f"File not found: {file_path}"
        
        if not path.is_file():
            return False, f"Path is not a file: {file_path}"
        
        if not os.access(path, os.R_OK):
            return False, f"File is not readable: {file_path}"
        
        return True, ""
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        return Path(file_path).stat().st_size
    
    def get_file_extension(self, file_path: str) -> str:
        """Get file extension (lowercase)."""
        return Path(file_path).suffix.lower()


class CommandRegistry:
    """Registry for managing dynamic commands."""
    
    def __init__(self, commands_dir: str):
        self.commands_dir = Path(commands_dir)
        self.commands: Dict[str, CommandBase] = {}
        self.command_metadata: Dict[str, Dict[str, Any]] = {}
    
    def discover_commands(self) -> List[str]:
        """Discover available commands in the commands directory."""
        discovered = []
        
        if not self.commands_dir.exists():
            return discovered
        
        for command_dir in self.commands_dir.iterdir():
            if command_dir.is_dir() and not command_dir.name.startswith('.'):
                main_file = command_dir / 'main.py'
                if main_file.exists():
                    discovered.append(command_dir.name)
        
        return discovered
    
    def load_command(self, command_name: str) -> Optional[CommandBase]:
        """Load a command dynamically."""
        if command_name in self.commands:
            return self.commands[command_name]
        
        command_path = self.commands_dir / command_name / 'main.py'
        if not command_path.exists():
            return None
        
        try:
            # Dynamic import
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                f"bielik_command_{command_name}", 
                command_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for a class that inherits from CommandBase
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, CommandBase) and 
                    attr not in (CommandBase, ContextProviderCommand) and
                    (not hasattr(attr, '__abstractmethods__') or len(attr.__abstractmethods__) == 0)):
                    
                    command_instance = attr()
                    self.commands[command_name] = command_instance
                    
                    # Load metadata if available
                    self._load_command_metadata(command_name)
                    
                    return command_instance
            
            print(f"⚠️ No CommandBase subclass found in {command_path}")
            return None
            
        except Exception as e:
            print(f"❌ Failed to load command '{command_name}': {e}")
            return None
    
    def _load_command_metadata(self, command_name: str):
        """Load command metadata from config.json if it exists."""
        config_path = self.commands_dir / command_name / 'config.json'
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.command_metadata[command_name] = json.load(f)
            except Exception as e:
                print(f"⚠️ Failed to load metadata for '{command_name}': {e}")
    
    def get_command(self, command_name: str) -> Optional[CommandBase]:
        """Get a command by name, loading it if necessary."""
        return self.load_command(command_name)
    
    def list_commands(self) -> List[str]:
        """List all available commands."""
        return self.discover_commands()
    
    def get_command_help(self, command_name: str) -> str:
        """Get help text for a command."""
        command = self.get_command(command_name)
        if command:
            return command.get_help()
        return f"Command '{command_name}' not found"
    
    def execute_command(self, command_name: str, args: List[str], context: Dict[str, Any]) -> str:
        """Execute a command with given arguments."""
        command = self.get_command(command_name)
        if not command:
            return f"❌ Command '{command_name}' not found"
        
        try:
            return command.execute(args, context)
        except Exception as e:
            return f"❌ Command execution failed: {e}"


# Global command registry instance
_command_registry = None


def get_command_registry(commands_dir: str = None) -> CommandRegistry:
    """Get or create the global command registry."""
    global _command_registry
    if _command_registry is None:
        if commands_dir is None:
            # Default to commands directory at project root
            base_dir = Path(__file__).parent.parent.parent  # Go up to project root
            commands_dir = base_dir / 'commands'
        _command_registry = CommandRegistry(commands_dir)
    return _command_registry
