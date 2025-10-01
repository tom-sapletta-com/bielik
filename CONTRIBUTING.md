# 🛠 Contributing to Bielik

Thank you for your interest in contributing to Bielik! We welcome contributions from the community to help improve this project.

## 📋 Table of Contents
- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Setup](#-development-setup)
- [Pull Request Process](#-pull-request-process)
- [Coding Standards](#-coding-standards)
- [Testing](#-testing)
- [Documentation](#-documentation)
- [Reporting Issues](#-reporting-issues)

## ✨ Code of Conduct

This project adheres to the [Contributor Covenant](https://www.contributor-covenant.org/). By participating, you are expected to uphold this code.

## 🚀 Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. Set up the development environment (see below)
4. Create a new branch for your changes
5. Make your changes
6. Run tests to ensure nothing is broken
7. Submit a pull request

## 💻 Development Setup

### Prerequisites
- Python 3.11+
- Conda (recommended) or virtualenv
- Git

### Environment Setup

```bash
# 1. Create and activate conda environment
conda create -n bielik-dev python=3.11 -y
conda activate bielik-dev

# 2. Install development dependencies
conda install -c conda-forge -y \
    pytest \
    pytest-cov \
    black \
    flake8 \
    isort \
    mypy

# 3. Install Bielik in development mode
pip install -e ".[dev]"
```

## 🔄 Pull Request Process

1. Update the `CHANGELOG.md` with your changes
2. Make sure all tests pass
3. Ensure your code follows the coding standards
4. Update documentation as needed
5. Submit your pull request with a clear description of your changes

## 📏 Coding Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for all new code
- Write docstrings for all public functions and classes
- Keep lines under 88 characters (Black's default)
- Use absolute imports

### Code Formatting

We use the following tools to maintain code quality:

```bash
# Auto-format code
black .

# Sort imports
isort .

# Check for style issues
flake8 .

# Check type hints
mypy .
```

## 🧪 Testing

Write tests for all new functionality. We use `pytest` for testing.

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=bielik tests/

# Run a specific test file
pytest tests/test_file.py
```

## 📚 Documentation

- Update relevant documentation when adding new features
- Follow the existing documentation style
- Add docstrings to all new functions and classes
- Update README.md if necessary

## 🐛 Reporting Issues

When reporting issues, please include:

1. A clear title and description
2. Steps to reproduce the issue
3. Expected vs. actual behavior
4. Version information (Python, OS, etc.)
5. Any relevant error messages or logs

## 🤝 Getting Help

If you need help or have questions, please open an issue on GitHub or reach out to the maintainers.

Thank you for contributing to Bielik! 🎉
