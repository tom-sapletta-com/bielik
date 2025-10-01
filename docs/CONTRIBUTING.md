# 🤝 Contributing Guide

Development setup and contribution guidelines for Bielik Polish AI Assistant CLI.

## 📋 **Navigation Menu**
- [🏠 Documentation Home](README.md)
- [📥 Installation](INSTALLATION.md)
- [🏗️ Architecture](ARCHITECTURE.md)
- [⚡ Usage Guide](USAGE.md)

---

## ✨ **Welcome Contributors!**

Thank you for your interest in contributing to Bielik! We welcome contributions from the community to help improve this groundbreaking Polish AI assistant.

### 🎯 **Contribution Areas**
- **🐛 Bug fixes** - Help us squash bugs and improve stability
- **✨ New features** - Add functionality and enhance user experience  
- **📚 Documentation** - Improve guides, examples, and API docs
- **🧪 Testing** - Add tests and improve coverage
- **🌍 Internationalization** - Support for additional languages
- **🎯 Context Provider Commands** - Create new analysis commands

---

## 📜 **Code of Conduct** 

This project adheres to the [Contributor Covenant](https://www.contributor-covenant.org/). By participating, you are expected to uphold this code.

**Key principles:**
- 🤝 **Be respectful** - Treat all community members with respect
- 🌟 **Be inclusive** - Welcome contributors from all backgrounds
- 🎯 **Be constructive** - Provide helpful feedback and suggestions
- 📚 **Be collaborative** - Work together to improve the project

---

## 🚀 **Quick Start for Contributors**

### **1. Fork and Clone**
```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork locally
git clone https://github.com/YOUR_USERNAME/bielik.git
cd bielik

# 3. Add upstream remote
git remote add upstream https://github.com/tom-sapletta-com/bielik.git
```

### **2. Development Setup**
```bash
# Create development environment
conda create -n bielik-dev python=3.11 -y
conda activate bielik-dev

# Install development dependencies
conda install -c conda-forge -y \
    pytest \
    pytest-cov \
    black \
    flake8 \
    isort \
    mypy \
    pre-commit

# Install Bielik in development mode
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install
```

### **3. Make Changes**
```bash
# Create feature branch
git checkout -b feature/my-new-feature

# Make your changes
# ... edit files ...

# Test your changes
pytest
make test-all  # Includes Docker tests

# Format code
black .
isort .
flake8 .
```

### **4. Submit Pull Request**
```bash
# Commit changes
git add .
git commit -m "Add new feature: brief description"

# Push to your fork
git push origin feature/my-new-feature

# Create pull request on GitHub
```

---

## 💻 **Development Environment Setup**

### **Prerequisites**
- **Python 3.11+** - Modern Python features and performance
- **Conda** (recommended) or virtualenv for environment management
- **Git** for version control
- **Docker** (optional) for testing framework

### **Detailed Setup Instructions**

#### **1. Conda Environment (Recommended)**
```bash
# Create isolated development environment
conda create -n bielik-dev python=3.11 -y
conda activate bielik-dev

# Install system dependencies for compilation
conda install -c conda-forge -y \
    cmake \
    make \
    gcc_linux-64 \
    gxx_linux-64 \
    libgcc \
    libstdcxx-ng

# Install development and testing tools
conda install -c conda-forge -y \
    pytest \
    pytest-cov \
    pytest-asyncio \
    black \
    flake8 \
    isort \
    mypy \
    pre-commit \
    sphinx \
    sphinx-rtd-theme

# Install Bielik with all optional dependencies
pip install -e ".[dev,vision,local,gpu]"
```

#### **2. Alternative: Virtual Environment**
```bash
# Create virtual environment
python -m venv .venv-dev
source .venv-dev/bin/activate  # Linux/macOS
# .venv-dev\Scripts\activate     # Windows

# Upgrade pip and install development dependencies
pip install --upgrade pip
pip install -e ".[dev]"
pip install pytest pytest-cov black flake8 isort mypy pre-commit
```

### **3. Pre-commit Hooks Setup**
```bash
# Install pre-commit hooks (runs automatically on git commit)
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate
```

---

## 🏗️ **Project Structure for Contributors**

### **Understanding the Codebase**
```
bielik/
├── bielik/                     # Main package
│   ├── cli/                   # CLI components (most active development)
│   │   ├── main.py           # Entry point and prompt processing
│   │   ├── commands.py       # Built-in CLI commands
│   │   ├── command_api.py    # Context Provider Commands API
│   │   ├── models.py         # HuggingFace model management
│   │   └── send_chat.py      # Chat communication
│   ├── client/               # Python API components
│   │   ├── core.py          # BielikClient class
│   │   └── model_manager.py # Model operations
│   ├── models/              # Model execution
│   │   ├── model_manager.py # Local model management
│   │   └── local_runner.py  # llama-cpp-python interface
│   └── server.py            # FastAPI web server
├── commands/                 # Context Provider Commands (extensible)
│   ├── folder/              # Directory analysis
│   ├── calc/               # Calculator
│   └── pdf/                # Document processing
├── docker/                 # Docker testing framework
├── docs/                   # Documentation (this directory)
├── scripts/                # Utility scripts
└── tests/                  # Unit tests
```

### **Key Components to Understand**

1. **CLI System** (`bielik/cli/`)
   - Entry point for user interactions
   - Command processing and routing
   - Context Provider Commands integration

2. **Context Provider Commands** (`commands/`)
   - Extensible plugin system
   - Independent data analysis tools
   - Template for new command development

3. **Model Management** (`bielik/models/`)
   - HuggingFace integration
   - Local model execution
   - Performance optimization

---

## 🧪 **Testing Framework**

### **Running Tests**

#### **Unit Tests**
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=bielik tests/

# Run specific test file
pytest tests/test_cli.py

# Run with verbose output
pytest -v

# Run tests and generate HTML coverage report
pytest --cov=bielik --cov-report=html tests/
```

#### **Docker Integration Tests**
```bash
# Run complete multiplatform test suite
make docker-test

# Test specific distributions
make docker-test-ubuntu     # Ubuntu 22.04
make docker-test-debian     # Debian 12
make docker-test-alpine     # Alpine Linux 3.19
make docker-test-centos     # CentOS Stream 9
make docker-test-arch       # Arch Linux

# Test one-liner installation
make docker-test-oneliner

# Run all tests (unit + docker)
make test-all
```

### **Writing Tests**

#### **Unit Test Example**
```python
# tests/test_new_feature.py
import pytest
from bielik.cli.commands import SomeCommand

class TestSomeCommand:
    def test_command_execution(self):
        """Test command executes correctly."""
        command = SomeCommand()
        result = command.execute(["arg1", "arg2"])
        assert result is not None
        assert "expected" in result
    
    @pytest.mark.asyncio
    async def test_async_feature(self):
        """Test async functionality."""
        # Async test code here
        pass
```

#### **Context Provider Command Test**
```python
# tests/test_context_providers.py
from bielik.cli.command_api import CommandRegistry

def test_new_context_provider():
    """Test new context provider command."""
    registry = CommandRegistry()
    
    # Test command registration
    assert "mynewcommand" in registry.list_commands()
    
    # Test command execution
    result = registry.execute_command("mynewcommand", 
                                    ["mynewcommand:", "test-input"], 
                                    {})
    assert result is not None
    assert result["type"] == "expected_type"
```

---

## 📏 **Coding Standards**

### **Code Style**
- **Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)** style guide
- **Use type hints** for all new code
- **Write docstrings** for all public functions and classes
- **Keep lines under 88 characters** (Black's default)
- **Use absolute imports** for clarity

### **Code Formatting Tools**
```bash
# Auto-format code (required before commit)
black .

# Sort imports
isort .

# Check for style issues
flake8 .

# Check type hints
mypy bielik/

# Run all formatting tools
make format
```

### **Type Hints Example**
```python
from typing import List, Dict, Optional, Union

def process_messages(messages: List[Dict[str, str]], 
                    model: Optional[str] = None) -> str:
    """Process chat messages and return response.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model: Optional model name to use for processing
        
    Returns:
        Generated response string
        
    Raises:
        ValueError: If messages format is invalid
    """
    # Implementation here
    pass
```

### **Docstring Format**
```python
def example_function(param1: str, param2: int = 10) -> Dict[str, Any]:
    """Brief description of what the function does.
    
    Longer description with more details about the function's purpose,
    behavior, and any important notes.
    
    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter with default value
        
    Returns:
        Description of what the function returns
        
    Raises:
        ValueError: When and why this exception might be raised
        TypeError: Another potential exception
        
    Example:
        >>> result = example_function("test", 20)
        >>> print(result["key"])
        "value"
    """
    return {"key": "value"}
```

---

## 🔄 **Pull Request Process**

### **Before Submitting**
1. **✅ Update CHANGELOG.md** with your changes
2. **✅ Ensure all tests pass** (`pytest` and `make docker-test`)
3. **✅ Follow coding standards** (`black`, `isort`, `flake8`, `mypy`)
4. **✅ Update documentation** as needed
5. **✅ Add tests** for new functionality
6. **✅ Verify Docker tests** pass on clean environments

### **Pull Request Template**
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass (`pytest`)
- [ ] Docker tests pass (`make docker-test`)
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines (`black`, `flake8`)
- [ ] Self-review of code completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Corresponding changes to documentation made
- [ ] Changes generate no new warnings
```

### **Review Process**
1. **🔍 Automated checks** run on every PR (GitHub Actions)
2. **👥 Code review** by maintainers
3. **✅ Approval** required before merge
4. **🚀 Merge** to main branch after approval

---

## 🎯 **Contribution Ideas**

### **🐛 Bug Fixes**
- Fix model loading issues on specific platforms
- Improve error handling and user messages
- Memory optimization for large models
- CLI responsiveness improvements

### **✨ New Features**
- Additional Polish language models support
- Enhanced Context Provider Commands
- Better project management features
- Performance monitoring and metrics

### **📚 Documentation**
- More usage examples and tutorials
- API documentation improvements
- Video tutorials and guides
- Translation to Polish

### **🌍 Internationalization**
- Support for additional languages
- Localized error messages
- Cultural context improvements
- Regional model variants

### **🧪 Testing & Quality**
- Increase test coverage
- Add integration tests
- Performance benchmarks
- Security testing

### **🎯 Context Provider Commands**
Create new analysis commands:
```bash
# Ideas for new commands:
git:        # Git repository analysis
web:        # Web scraping and analysis
image:      # Image analysis without AI model
database:   # Database query and analysis
network:    # Network connectivity testing
system:     # System resource monitoring
```

---

## 🔧 **Development Workflows**

### **Feature Development**
```bash
# 1. Sync with upstream
git checkout main
git pull upstream main

# 2. Create feature branch
git checkout -b feature/context-provider-git

# 3. Develop iteratively
# Make changes → test → commit → repeat

# 4. Run comprehensive tests
pytest
make docker-test

# 5. Format and lint
black .
isort .
flake8 .

# 6. Push and create PR
git push origin feature/context-provider-git
```

### **Bug Fix Workflow**
```bash
# 1. Create bug fix branch
git checkout -b fix/model-loading-timeout

# 2. Write failing test first
# Add test that reproduces the bug

# 3. Fix the bug
# Implement the fix

# 4. Verify fix works
pytest tests/test_specific_bug.py

# 5. Run full test suite
make test-all
```

### **Documentation Updates**
```bash
# 1. Update documentation
# Edit files in docs/ directory

# 2. Test documentation locally
# Preview markdown files

# 3. Update main README if needed
# Keep main README concise with links to docs/

# 4. Submit documentation PR
```

---

## 🛠️ **Debugging and Development Tools**

### **Debugging CLI Issues**
```bash
# Enable debug mode
BIELIK_DEBUG=1 bielik

# Run with detailed logging
python -m bielik.cli.main --help

# Test specific components
python -c "from bielik.cli.commands import *; print('CLI imports OK')"
```

### **Model Development**
```bash
# Test model loading
python -c "from bielik.models.local_runner import LocalModelRunner; runner = LocalModelRunner()"

# Test HuggingFace integration
python -c "from bielik.models.model_manager import HFModelManager; manager = HFModelManager()"
```

### **Context Provider Development**
```bash
# Test command registry
python -c "from bielik.cli.command_api import CommandRegistry; registry = CommandRegistry(); print(registry.list_commands())"

# Test specific command
bielik -p "mynewcommand: test-input"
```

---

## 📊 **Performance Guidelines**

### **Code Performance**
- **Lazy loading** - Load resources only when needed
- **Caching** - Use appropriate caching strategies
- **Memory management** - Clean up resources properly
- **Async operations** - Use async/await for I/O operations

### **Model Performance**
- **Efficient tokenization** - Minimize token overhead
- **Batch processing** - Group operations when possible
- **GPU utilization** - Optimize GPU memory usage
- **Context management** - Manage conversation context efficiently

---

## 📝 **Documentation Standards**

### **Code Documentation**
- **Docstrings** for all public functions and classes
- **Type hints** for all function parameters and returns
- **Inline comments** for complex logic
- **README updates** for new features

### **User Documentation**
- **Usage examples** for new features
- **Installation notes** for new dependencies
- **Troubleshooting guides** for common issues
- **API documentation** for client libraries

---

## 🆘 **Getting Help**

### **Development Support**
- **GitHub Issues** - Ask questions and report problems
- **Discussions** - General development discussions
- **Code Reviews** - Get feedback on your contributions
- **Documentation** - Comprehensive guides and examples

### **Community Resources**
- **Contributing Guide** - This document
- **Architecture Documentation** - Technical design details
- **API Documentation** - Client library reference
- **Usage Examples** - Practical implementation guides

---

## 🎉 **Recognition**

Contributors are recognized in:
- **CHANGELOG.md** - Credit for each release
- **README.md** - Contributors section
- **GitHub** - Contributor statistics and graphs
- **Releases** - Special thanks in release notes

---

Thank you for contributing to Bielik! Your efforts help make Polish AI more accessible to everyone. 🇵🇱

**Next Steps:** [API Documentation](API.md) | [Context Providers](CONTEXT_PROVIDERS.md) | [Docker Testing](DOCKER.md)
