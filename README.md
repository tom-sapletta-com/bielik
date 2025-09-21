![terminal](terminal.png)
# 🦅 bielik

[![PyPI](https://img.shields.io/pypi/v/bielik.svg)](https://pypi.org/project/bielik/)
[![Python](https://img.shields.io/pypi/pyversions/bielik.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/tomsapletta/bielik/python-app.yml?branch=main)](https://github.com/tomsapletta/bielik/actions)
[![Downloads](https://img.shields.io/pypi/dm/bielik.svg)](https://pypi.org/project/bielik/)
[![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-black.svg)](https://flake8.pycqa.org/)
[![Issues](https://img.shields.io/github/issues/tomsapletta/bielik.svg)](https://github.com/tomsapletta/bielik/issues)
[![Stars](https://img.shields.io/github/stars/tomsapletta/bielik.svg)](https://github.com/tomsapletta/bielik/stargazers)
[![Forks](https://img.shields.io/github/forks/tomsapletta/bielik.svg)](https://github.com/tomsapletta/bielik/network)

**Author:** Tom Sapletta  
**License:** Apache-2.0

> 🇵🇱 **Bielik** is a local chat client for **[Ollama](https://ollama.com)** with CLI and web interfaces, created specifically for the Polish language model **[Bielik](https://huggingface.co/speakleash)** from **[Speakleash](https://speakleash.org/)**.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          🦅 BIELIK                              │
├─────────────────────┬───────────────────────┬───────────────────┤
│   🖥️  CLI Shell     │  🌐 FastAPI Server   │  🧪 Test Suite     │
│  ┌─────────────────┐│ ┌───────────────────┐ │ ┌───────────────┐ │
│  │ • Interactive   ││ │ • REST /chat      │ │ │ • Unit tests  │ │
│  │ • Help system   ││ │ • WebSocket /ws   │ │ │ • Mock API    │ │
│  │ • Cross-platform││ │ • Port 8888       │ │ │ • CI/CD       │ │
│  └─────────────────┘│ └───────────────────┘ │ └───────────────┘ │
└─────────────────────┴───────────────────────┴───────────────────┘
            │                       │                       │
            ▼                       ▼                       ▼
┌───────────────────────────────────────────────────────────────┐
│                    🔄 CONNECTION LAYER                        │
│  ┌──────────────────────┐    ┌─────────────────────────────┐  │
│  │    REST API (main)   │◄──►│   Ollama Library (fallback) │  │
│  │ ┌─ HTTP requests     │    │ ┌─ ollama.chat()            │  │
│  │ └─ /v1/chat/...      │    │ └─ Direct integration       │  │
│  └──────────────────────┘    └─────────────────────────────┘  │
└─────────────────────┬─────────────────────────────────────────┘
                      ▼
┌───────────────────────────────────────────────────────────────┐
│                   🦙 OLLAMA SERVER                            │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ 📍 localhost:11434 (default)                            │  │
│  │ 🤖 Model: bielik (Polish LLM)                           │  │
│  │ 🔗 Links: Speakleash → HuggingFace → Ollama             │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

---

## 🤖 About Bielik Model

**Bielik** is a groundbreaking Polish language model created by **[Speakleash](https://speakleash.org/)** - a foundation dedicated to the development of Polish artificial intelligence.

### 🔗 External Dependencies & Links:
- **[Ollama](https://ollama.com)** - Local LLM runtime that hosts the Bielik model
- **[Bielik Model on HuggingFace](https://huggingface.co/speakleash)** - Official model repository
- **[Speakleash Foundation](https://speakleash.org/)** - Creators of the Bielik model
- **[Polish AI Initiative](https://www.gov.pl/web/ai)** - Government support for Polish AI

### 🚀 How it Works:
1. **Bielik package** connects to your local **Ollama server**
2. **Ollama** runs the **Bielik model** (downloaded from HuggingFace via Speakleash)
3. **Chat interface** (CLI/Web) sends queries → **Ollama API** → **Bielik model** → responses
4. **Fallback system** ensures connectivity (REST API → ollama library)

---

## 📌 Features

- **🎯 Auto-Setup System** — Intelligent first-time setup for beginners
  - **🔍 Detection** — Automatically detects missing components
  - **📦 Installation** — Cross-platform Ollama installation (Linux/macOS)
  - **🚀 Configuration** — Downloads and configures Bielik model
  - **🛠️ Interactive** — User-friendly prompts and error handling
- **🖥️ Enhanced CLI** `bielik` — Interactive chat shell with modular architecture
  - **📋 Commands** — `:help`, `:status`, `:setup`, `:clear`, `:exit`, `:models`, `:download`, `:delete`, `:switch`
  - **⚙️ Arguments** — `--setup`, `--no-setup`, `--model`, `--host`, `--use-local`, `--local-model`
  - **🤗 HF Integration** — Direct Hugging Face model management and local execution
  - **🔄 Fallback** — REST API primary, ollama lib secondary, local models tertiary
  - **🌍 Cross-platform** — Windows, macOS, Linux support
- **🐍 Python API** — Programmatic access via `BielikClient` class
  - **💬 Chat methods** — `chat()`, `query()`, conversation management
  - **🔧 System control** — Status checking, auto-setup, model management
  - **🤗 HF Models** — Download, manage, and run SpeakLeash models locally
  - **📤 Export** — Conversation history in JSON, text, markdown formats
- **🌐 Web Server** (FastAPI on port 8888):  
  - **📡 REST** — `POST /chat` endpoint for JSON communication
  - **⚡ WebSocket** — `WS /ws` for real-time chat
  - **🔄 Fallback** — Same dual connectivity as CLI
- **🧪 Quality Assurance** — Comprehensive testing and development tools
  - **✅ Unit tests** — Full coverage with mocked APIs
  - **🔧 CI/CD** — GitHub Actions automation
  - **📊 Code quality** — Flake8 linting, automated builds  

---

## ⚙️ Installation

```bash
pip install bielik
```

Optional dependency (official Ollama lib):

```bash
pip install "bielik[ollama]"
```

---

## 🚀 Quick Start Guide

### 🎯 **NEW: Automatic Setup (Recommended)**

The easiest way to get started is with the new automatic setup system:

```bash
# Install Bielik package
pip install bielik

# Start with automatic setup - it will handle everything!
bielik

# Or force setup mode:
bielik --setup
```

The auto-setup system will:
- ✅ **Detect** if Ollama is installed
- ✅ **Install Ollama** automatically (Linux/macOS) 
- ✅ **Start Ollama server** if not running
- ✅ **Download Bielik model** (`SpeakLeash/bielik-7b-instruct-v0.1-gguf`)
- ✅ **Configure** everything for optimal performance

### 📋 Manual Setup (Advanced Users)

If you prefer manual control:

#### 1️⃣ Install Ollama (Cross-platform)

**Windows:**
```powershell
# Download installer from ollama.com or use winget:
winget install Ollama.Ollama
```

**macOS:**
```bash
# Download .dmg from ollama.com or use Homebrew:
brew install ollama
```

**Linux:**
```bash
# Ubuntu/Debian:
curl -fsSL https://ollama.com/install.sh | sh

# Arch Linux:
sudo pacman -S ollama
```

#### 2️⃣ Setup Bielik Model

```bash
# Start Ollama service (Linux/macOS):
ollama serve

# Windows: Ollama starts automatically

# Install Bielik model (new full model name):
ollama pull SpeakLeash/bielik-7b-instruct-v0.1-gguf

# Verify installation:
ollama list
```

#### 3️⃣ Install & Use Bielik Package

```bash
# Install from PyPI:
pip install bielik

# Start CLI chat:
bielik

# Skip auto-setup if you prefer manual control:
bielik --no-setup

# Or start web server:
uvicorn bielik.server:app --port 8888
```

---

## 💻 Usage

### 🖥️ CLI Features & Options

#### Command-Line Arguments (when starting bielik)

```bash
# Basic usage
bielik                                    # Start interactive chat with auto-setup

# Advanced options
bielik --setup                           # Force setup mode
bielik --no-setup                        # Skip automatic setup
bielik --model other-model               # Use different model
bielik --host http://other-host:11434    # Use different Ollama server
bielik --use-local                       # Use local HuggingFace models (bypass Ollama)
bielik --local-model model-name          # Specify local model to use
bielik --help                            # Show all options
```

#### Interactive Commands (inside bielik chat session)

**⚠️ Important:** These commands only work **inside** the interactive chat session, not as command-line arguments.

```bash
# Start interactive session first
$ bielik

# Then use these commands inside the chat:
🧑 You: :help             # Show help and commands
🧑 You: :status           # Check Ollama connection and model availability
🧑 You: :setup            # Run interactive setup system
🧑 You: :models           # List available and downloaded HuggingFace models
🧑 You: :download <model> # Download a SpeakLeash model from Hugging Face
🧑 You: :delete <model>   # Delete a downloaded model
🧑 You: :switch <model>   # Switch to a different model for execution
🧑 You: :storage          # Show model storage statistics
🧑 You: :clear            # Clear conversation history
🧑 You: :exit             # Quit (or Ctrl+C)
```

#### Usage Examples

```bash
# ✅ Correct - Start with specific model
$ bielik --model SpeakLeash/Bielik-4.5B-v3.0-Instruct-GGUF

# ✅ Correct - Interactive commands inside session
$ bielik
🧑 You: :status
🧑 You: :switch SpeakLeash/Bielik-4.5B-v3.0-Instruct-GGUF

# ❌ Incorrect - Interactive commands as CLI arguments
$ bielik :status          # This won't work!
$ bielik :switch model    # This won't work!
```

### 🐍 Python API

**NEW:** Use Bielik programmatically in your Python applications:

```python
from bielik.client import BielikClient

# Create client with auto-setup
client = BielikClient()

# Send a message
response = client.chat("How are you?")
print(response)

# Get system status
status = client.get_status()
print(f"Ollama running: {status['ollama_running']}")
print(f"Model available: {status['model_available']}")

# Export conversation
history = client.export_conversation(format="markdown")
```

**Quick functions:**
```python
from bielik.client import quick_chat, get_system_status

# One-off query
response = quick_chat("What is artificial intelligence?")

# Check system without setup
status = get_system_status()
```

**BielikClient Options:**
- `model`: Model name to use
- `host`: Ollama server URL  
- `auto_setup`: Enable/disable automatic setup (default: True)

### Web API

```bash
uvicorn bielik.server:app --port 8888
```

**Endpoints:**
- `POST /chat` - JSON chat endpoint
- `WS /ws` - WebSocket real-time chat

**Example request:**
```json
{"messages": [{"role":"user","content":"Hello!"}]}
```

---

## 🔧 Environment Variables

* `OLLAMA_HOST` — default: `http://localhost:11434`
* `BIELIK_MODEL` — default: `SpeakLeash/bielik-7b-instruct-v0.1-gguf`

---

## 🛠️ Troubleshooting

### Auto-Setup Issues

**Problem:** Auto-setup fails to install Ollama
```bash
# Manual installation required for Windows
# Download from: https://ollama.com/download/windows

# Linux/macOS alternatives:
curl -fsSL https://ollama.com/install.sh | sh  # Linux
brew install ollama                             # macOS
```

**Problem:** Model download fails or times out
```bash
# Try manual download with longer timeout
ollama pull SpeakLeash/bielik-7b-instruct-v0.1-gguf

# Check available disk space (model is ~4GB)
df -h

# Check network connection
curl -I https://ollama.com
```

**Problem:** Ollama server won't start
```bash
# Check if port 11434 is in use
lsof -i :11434  # Linux/macOS
netstat -an | findstr 11434  # Windows

# Try different port
OLLAMA_HOST=http://localhost:11435 ollama serve --port 11435
```

### Runtime Issues

**Problem:** "Connection refused" errors
```bash
# Check Ollama status
bielik :status

bielik :switch SpeakLeash/Bielik-4.5B-v3.0-Instruct-GGUF

# Restart Ollama service
pkill ollama && ollama serve  # Linux/macOS

# Manual server start
ollama serve
```

**Problem:** Model responses are slow
```bash
# Check system resources
htop      # Linux/macOS
taskmgr   # Windows

# Use smaller model if needed
bielik --model llama2  # If available
```

**Problem:** Python API import errors
```bash
# Reinstall with dependencies
pip uninstall bielik
pip install bielik[ollama]

# Check Python path
python -c "import bielik.client; print('OK')"
```

### Getting Help

- **GitHub Issues:** [Report bugs and feature requests](https://github.com/tomsapletta/bielik/issues)
- **Command Help:** `bielik --help` or `:help` in CLI
- **System Status:** Use `:status` command or `get_system_status()` function

---

## 📝 Development

```bash
git clone https://github.com/tomsapletta/bielik.git
cd bielik
python -m venv .venv
source .venv/bin/activate
pip install -e .[ollama]
```


# 📂 Package Structure

```
bielik/
├── bielik/
│   ├── __init__.py          # Package initialization
│   ├── cli.py               # CLI entry point (wrapper)
│   ├── client.py            # Client entry point (wrapper)
│   ├── server.py            # FastAPI web server
│   ├── config.py            # Configuration management
│   ├── hf_models.py         # Hugging Face model management
│   ├── content_processor.py # Content processing utilities
│   ├── cli/                 # Modular CLI components
│   │   ├── __init__.py
│   │   ├── main.py          # Main CLI entry and argument parsing
│   │   ├── commands.py      # Command processing and execution
│   │   ├── models.py        # HF model management CLI
│   │   ├── setup.py         # Interactive setup manager
│   │   └── send_chat.py     # Chat communication handling
│   └── client/              # Modular client components
│       ├── __init__.py      # Client package exports
│       ├── core.py          # Core BielikClient class
│       ├── model_manager.py # HF model operations for client
│       └── utils.py         # Client utility functions
├── tests/
│   ├── __init__.py
│   ├── test_cli.py          # CLI unit tests
│   └── test_server.py       # Server unit tests
├── pyproject.toml           # Modern Python packaging
├── setup.cfg                # Package configuration
├── MANIFEST.in              # Package manifest
├── LICENSE                  # Apache 2.0 license
├── README.md                # This documentation
├── Makefile                 # Development automation
├── todo.md                  # Project specifications
└── .github/workflows/       # CI/CD automation
    └── python-publish.yml
```



## 📜 License

[Apache License 2.0](LICENSE)


