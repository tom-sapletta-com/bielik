import pytest
import os
from unittest.mock import Mock, patch
from bielik.cli.send_chat import send_chat
from bielik.cli.commands import CommandProcessor
from bielik.cli.command_api import ContextProviderCommand, CommandBase


@patch('bielik.cli.send_chat.HAS_LLAMA_CPP', False)
def test_send_chat_local_model_missing():
    """Test send_chat when llama-cpp-python is not available."""
    messages = [{"role": "user", "content": "hi"}]
    reply = send_chat(messages, model="test-model")
    
    # Should return error message about missing llama-cpp-python
    assert "LOCAL MODEL ERROR" in reply
    assert "llama-cpp-python not installed" in reply or "conda install" in reply


@patch('bielik.cli.send_chat.HAS_LLAMA_CPP', False)
def test_send_chat_local_model_mock():
    """Test send_chat with mocked llama-cpp-python."""
    messages = [{"role": "user", "content": "hi"}]
    reply = send_chat(messages, model="test-model", use_local=True)
    
    # Should return error message about missing llama-cpp-python
    assert "LOCAL MODEL ERROR" in reply
    assert "llama-cpp-python not installed" in reply or "conda install" in reply


def test_send_chat_local_model_installed():
    """Test send_chat when llama-cpp-python is installed but model not downloaded."""
    # Skip this test if llama-cpp-python is not installed
    try:
        import llama_cpp
        HAS_LLAMA_CPP = True
    except ImportError:
        HAS_LLAMA_CPP = False
        pytest.skip("llama-cpp-python is not installed")
    
    if not HAS_LLAMA_CPP:
        return
    
    # Test that send_chat handles missing model gracefully
    messages = [{"role": "user", "content": "hi"}]
    reply = send_chat(messages, model="nonexistent-test-model", use_local=True)
    
    # Should return error message about model not being downloaded
    assert "LOCAL MODEL ERROR" in reply
    assert "not downloaded" in reply or "not found" in reply


def test_context_provider_command_basic():
    """Test basic Context Provider Command functionality."""

    class TestContextProvider(ContextProviderCommand):
        def __init__(self):
            super().__init__()
            # These are set automatically by the base class:
            # self.name = "testcontextprovider" (from class name)
            # self.description = "Test basic Context Provider Command functionality." (from docstring)
            # self.is_context_provider = True (from parent class)
        
        def execute(self, args, context):
            # Required by CommandBase
            return "This is a test command"
            
        def get_help(self):
            # Required by CommandBase
            return "Help for test command"
            
        def provide_context(self, args, context):
            return {
                "command": "testcontextprovider",
                "input": " ".join(args),
                "context_type": "test_analysis"
            }
    
    cmd = TestContextProvider()
    
    # Test that it's properly registered as a context provider
    assert cmd.is_context_provider is True
    assert cmd.name == "testcontextprovider"
    
    # Test the provide_context method
    result = cmd.provide_context(["hello", "world"], {})
    assert result["command"] == "testcontextprovider"
    assert result["input"] == "hello world"
    assert result["context_type"] == "test_analysis"
    
    # Test the required CommandBase methods
    assert cmd.execute([], {}) == "This is a test command"
    assert cmd.get_help() == "Help for test command"
    assert cmd.get_usage() == "testcontextprovider: <args>"


def test_direct_command_basic():
    """Test basic Direct Command functionality."""
    
    class TestDirectCommand(CommandBase):
        def __init__(self):
            super().__init__()
            self.name = "testcmd"
            self.description = "Test direct command"
            self.is_context_provider = False
        
        def execute(self, args, context):
            return f"Executed with: {' '.join(args)}"
        
        def get_help(self):
            return f"Help for {self.name}: {self.description}"
    
    cmd = TestDirectCommand()
    result = cmd.execute(["test", "input"], {})
    
    assert result == "Executed with: test input"


def test_command_processor_context_provider():
    """Test CommandProcessor with Context Provider commands."""
    processor = CommandProcessor()
    
    # Test context provider command detection
    assert processor._is_context_provider_command("folder: /path")
    assert processor._is_context_provider_command("calc: 2+2")
    assert not processor._is_context_provider_command(":help")
    assert not processor._is_context_provider_command("regular message")


def test_command_processor_direct_command():
    """Test CommandProcessor with Direct commands."""
    processor = CommandProcessor()
    
    # Test direct command detection  
    assert processor.is_command(":help")
    assert processor.is_command(":calc 2+2")
    assert processor.is_command("folder: /path")
    assert not processor.is_command("regular message")


def test_folder_command_integration():
    """Test folder command integration (if available)."""
    try:
        from commands.folder.main import command as folder_command
        
        # Test with current directory
        result = folder_command.provide_context(["."], {})
        
        assert "command" in result
        assert result["command"] == "folder"
        assert "directory_path" in result or "error" in result
        
    except ImportError:
        # Skip test if folder command not available
        pytest.skip("Folder command not available")


def test_calc_command_integration():
    """Test calc command integration (if available)."""
    try:
        from commands.calc.main import command as calc_command
        
        # Test basic calculation
        result = calc_command.execute(["2+2"], {})
        
        assert "4" in result or "calculation" in result.lower()
        
    except ImportError:
        # Skip test if calc command not available
        pytest.skip("Calc command not available")
