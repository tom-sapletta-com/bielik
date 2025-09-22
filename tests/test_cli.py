import pytest
import os
from unittest.mock import Mock, patch
from bielik.cli.send_chat import send_chat
from bielik.cli.commands import CommandProcessor
from bielik.cli.command_api import ContextProviderCommand, CommandBase


def test_send_chat_local_model_missing():
    """Test send_chat when llama-cpp-python is not available."""
    messages = [{"role": "user", "content": "hi"}]
    reply = send_chat(messages, model="test-model")
    
    # Should return error message about missing llama-cpp-python
    assert "LOCAL MODEL ERROR" in reply
    assert "llama-cpp-python not installed" in reply


@patch('bielik.cli.send_chat.HAS_LLAMA_CPP', True)
@patch('bielik.hf_models.HAS_LLAMA_CPP', True)  
def test_send_chat_local_model_mock():
    """Test send_chat with mocked llama-cpp-python."""
    
    # Mock the Llama class to avoid import errors
    mock_llama_class = Mock()
    mock_llama_instance = Mock()
    mock_llama_class.return_value = mock_llama_instance
    
    # Mock the LocalLlamaRunner to use our mocked response
    mock_runner = Mock()
    mock_runner.chat.return_value = "Hello from local HF model"
    
    # Mock the model manager
    mock_manager = Mock()
    mock_manager.is_model_downloaded.return_value = True
    mock_manager.get_model_path.return_value = "/fake/path/model.gguf"
    mock_manager.get_available_models.return_value = ["test-model"]
    
    with patch('llama_cpp.Llama', mock_llama_class), \
         patch('bielik.hf_models.LocalLlamaRunner', return_value=mock_runner), \
         patch('bielik.cli.send_chat.get_model_manager', return_value=mock_manager), \
         patch('bielik.hf_models.get_model_manager', return_value=mock_manager):
        messages = [{"role": "user", "content": "hi"}]
        reply = send_chat(messages, model="test-model", use_local=True)
        
        assert "Hello from local HF model" in reply


def test_context_provider_command_basic():
    """Test basic Context Provider Command functionality."""
    
    class TestContextProvider(ContextProviderCommand):
        def __init__(self):
            super().__init__(
                name="test", 
                description="Test context provider",
                usage="test: <input>"
            )
        
        def provide_context(self, args, context):
            return {
                "command": "test",
                "input": " ".join(args),
                "context_type": "test_analysis"
            }
    
    cmd = TestContextProvider()
    result = cmd.provide_context(["hello", "world"], {})
    
    assert result["command"] == "test"
    assert result["input"] == "hello world"
    assert result["context_type"] == "test_analysis"


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
    assert not processor.is_command("folder: /path")
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
