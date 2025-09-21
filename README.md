# 🦅 Bielik

**Bielik** is a groundbreaking Polish language model created by **[Speakleash](https://speakleash.org/)** - a foundation dedicated to the development of Polish artificial intelligence.
> 🇵🇱 **Bielik** is available on **[huggingface](https://huggingface.co/speakleash)**.
 
Now you can test it directly in the shell, using several features that allow you to build a multi-agent environment in your company 🚀 

- 🎯 **HuggingFace Integration** - Direct model downloads from HF Hub
- 💬 **Polish Language Optimized** - Built for Polish conversation and analysis  
- 🖼️ **Vision Capabilities** - Image analysis and visual question answering
- 📁 **Document Processing** - PDF, DOCX, web content analysis
- 🐳 **Docker Ready** - Containerized testing environments
- ⚡ **Lightweight** - Minimal (~50MB) or Full (~2GB) installation options

**Author:** Tom Sapletta  
**License:** Apache-2.0

[![PyPI](https://img.shields.io/pypi/v/bielik.svg)](https://pypi.org/project/bielik/)
[![Python](https://img.shields.io/pypi/pyversions/bielik.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/tom-sapletta-com/bielik/python-app.yml?branch=main)](https://github.com/tom-sapletta-com/bielik/actions)
[![Downloads](https://img.shields.io/pypi/dm/bielik.svg)](https://pypi.org/project/bielik/)
[![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-black.svg)](https://flake8.pycqa.org/)
[![Issues](https://img.shields.io/github/issues/tom-sapletta-com/bielik.svg)](https://github.com/tom-sapletta-com/bielik/issues)
[![Stars](https://img.shields.io/github/stars/tom-sapletta-com/bielik.svg)](https://github.com/tom-sapletta-com/bielik/stargazers)
[![Forks](https://img.shields.io/github/forks/tom-sapletta-com/bielik.svg)](https://github.com/tom-sapletta-com/bielik/network)


## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       🦅 BIELIK SYSTEM                          │
├─────────────────────┬───────────────────────┬───────────────────┤
│   🖥️  CLI Shell     │  🌐 FastAPI Server   │  🐳 Docker Tests   │
│  ┌─────────────────┐│ ┌───────────────────┐ │ ┌───────────────┐ │
│  │ • Interactive   ││ │ • REST /chat      │ │ │ • Minimal     │ │
│  │ • Personalized  ││ │ • WebSocket /ws   │ │ │ • Full        │ │
│  │ • Multi-modal   ││ │ • Port 8000       │ │ │ • CI/CD       │ │
│  └─────────────────┘│ └───────────────────┘ │ └───────────────┘ │
└─────────────────────┴───────────────────────┴───────────────────┘
            │                       │                       │
            ▼                       ▼                       ▼
┌───────────────────────────────────────────────────────────────┐
│                🤗 HUGGINGFACE INTEGRATION                     │
│  ┌──────────────────────┐    ┌─────────────────────────────┐  │
│  │   Direct Downloads   │◄──►│     Local Model Execution   │  │
│  │ ┌─ HF Hub API        │    │ ┌─ Transformers Pipeline    │  │
│  │ └─ Model Management  │    │ └─ Vision Models (optional) │  │
│  └──────────────────────┘    └─────────────────────────────┘  │
└─────────────────────┬─────────────────────────────────────────┘
                      ▼
┌───────────────────────────────────────────────────────────────┐
│                 📚 POLISH LANGUAGE MODELS                     │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ 🤖 Speakleash/Bielik Models (HuggingFace Hub)           │  │
│  │ 🔗 Direct: HuggingFace → Local Storage → Execution      │  │
│  │ 🎯 Polish-optimized conversation and analysis           │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

![terminal](terminal.png)

## 🤖 About Bielik Model

**Bielik** is a groundbreaking Polish language model created by **[Speakleash](https://speakleash.org/)** - a foundation dedicated to the development of Polish artificial intelligence.

### 🔗 External Dependencies & Links:
- **[HuggingFace Hub](https://huggingface.co)** - Primary source for Polish language models
- **[Bielik Models on HuggingFace](https://huggingface.co/speakleash)** - Official model repository
- **[Speakleash Foundation](https://speakleash.org/)** - Creators of the Bielik models
- **[Polish AI Initiative](https://www.gov.pl/web/ai)** - Government support for Polish AI

### 🚀 How it Works:
1. **Bielik CLI** connects directly to **HuggingFace Hub**
2. **Models** are downloaded from **Speakleash** organization on HuggingFace
3. **Local execution** uses **Transformers** library (optional for vision)
4. **Chat interface** (CLI/Web) → **Local Models** → **Polish responses**
5. **Modular design** supports text-only or full vision capabilities

---

## 📌 Features

- **🎯 HuggingFace Integration** — Direct model downloads and management
  - **🔍 Model Discovery** — Browse available Polish language models
  - **📦 Smart Downloads** — Automatic model caching and versioning
  - **🚀 Auto-Switch** — Automatically switches to newly downloaded models
  - **🛠️ Interactive** — User-friendly model selection on first startup
- **🖥️ Enhanced CLI** `python -m bielik` — Personalized chat experience
  - **📋 Commands** — `:help`, `:models`, `:download`, `:delete`, `:switch`, `:settings`, `:name`
  - **⚙️ Personalization** — Custom user names, dynamic assistant names
  - **🤗 HF Management** — Direct HuggingFace model operations
  - **📁 Content Analysis** — Folder scanning, document processing
  - **🌍 Cross-platform** — Windows, macOS, Linux support
- **🖼️ Vision Capabilities** (Full version only)
  - **🔍 Image Analysis** — Automatic image captioning in Polish
  - **❓ Visual QA** — Ask questions about images
  - **🎨 Multi-modal** — Combined text and image understanding
  - **⚡ GPU Support** — Hardware acceleration for faster processing
- **🐍 Python API** — Programmatic access via `BielikClient` class
  - **💬 Chat methods** — `chat()`, `query()`, conversation management
  - **🔧 Model control** — Download, switch, and manage models
  - **🤗 HF Models** — Full HuggingFace integration
  - **📤 Export** — Conversation history in multiple formats
- **🌐 Web Server** (FastAPI on port 8000):  
  - **📡 REST** — `POST /chat` endpoint for JSON communication
  - **⚡ WebSocket** — `WS /ws` for real-time chat
  - **🖼️ Multi-modal** — Support for text and image inputs
- **🐳 Docker Support** — Complete containerized testing
  - **📦 Minimal Version** — Lightweight text-only container (~50MB)
  - **🎯 Full Version** — Complete vision-enabled container (~2GB)
  - **🔧 CI/CD** — Automated testing environments  

---

## ⚙️ Installation Options

Bielik supports **universal multiplatform installation** that works seamlessly on **Windows**, **Linux**, and **macOS**.

## 🌍 **Universal Multiplatform Installation** ⭐ **RECOMMENDED**

**Cross-platform automated installer** with smart dependency detection:

### ⚡ **One-Liner Installation** (Fastest)

**Unix/Linux/macOS:**
```bash
curl -sSL https://raw.githubusercontent.com/tom-sapletta-com/bielik/main/quick-install.sh | bash
```

**Windows PowerShell:**
```powershell
iwr https://raw.githubusercontent.com/tom-sapletta-com/bielik/main/quick-install.bat -OutFile quick-install.bat; .\quick-install.bat
```

### 📥 **Manual Installation (Any Platform)**

```bash
# 1. Clone repository
git clone https://github.com/tom-sapletta-com/bielik.git
cd bielik

# 2. Run universal installer
python install.py
```

### 🪟 **Windows Users**
```batch
REM Double-click install.bat or run:
install.bat

REM Launch Bielik:
run.bat
```

### 🐧 **Linux/macOS Users**
```bash
# Run installer:
./install.sh

# Launch Bielik:
./run.sh
```

### ⚙️ **Installation Options**
```bash
# Basic installation (recommended)
python install.py

# Skip AI models (fastest installation)
python install.py --skip-ai

# Use conda/mamba instead of pip
python install.py --conda

# Development installation
python install.py --dev

# Show all options
python install.py --help
```

### 🎯 **What the Universal Installer Does:**
- ✅ **Auto-detects** your operating system and Python version
- ✅ **Creates** isolated virtual environment 
- ✅ **Installs** all dependencies with smart fallback strategies
- ✅ **Attempts** multiple llama-cpp-python installation methods
- ✅ **Creates** platform-specific launcher scripts
- ✅ **Works** even if AI models fail to install (Context Provider Commands still work)
- ✅ **Provides** clear next steps and troubleshooting

### 🚀 **After Installation**
```bash
# Universal launcher (any platform)
python run.py

# Platform-specific launchers
./run.sh        # Linux/macOS
run.bat         # Windows

# Or direct activation
.venv/bin/python -m bielik.cli.main     # Linux/macOS
.venv\Scripts\python -m bielik.cli.main # Windows
```

---

## 📦 **Alternative: PyPI Installation** 

For users who prefer traditional pip installation:

### 🪶 **Minimal Version** (Text-only)

```bash
# Install minimal version (text-only)
pip install bielik

# Start CLI and download your first model
python -m bielik
```

**What's included:**
- ✅ Polish conversation and text analysis
- ✅ HuggingFace model downloads and management  
- ✅ Document processing (PDF, DOCX, TXT)
- ✅ Web content analysis
- ✅ Context Provider Commands (folder:, calc:, pdf:)
- ✅ Personalized CLI experience
- ❌ Local AI models (requires manual llama-cpp-python installation)

### 🎯 **Full Version** (With vision)

```bash
# Install full version (text + vision)
pip install bielik[vision]

# Start CLI with image analysis support
python -m bielik
```

**What's included:**
- ✅ **Everything from minimal version**
- ✅ **Image analysis and captioning**
- ✅ **Visual question answering**
- ✅ **GPU acceleration support**
- ✅ **Multi-modal document processing**

### 🔄 **Upgrade Options**

```bash
# Upgrade minimal → full
pip install bielik[vision]

# Or install specific optional features
pip install bielik[local]    # Local model execution
pip install bielik[gpu]      # GPU acceleration
pip install bielik[dev]      # Development tools
```

---

## 🚀 Quick Start Guide

### 🎯 **Instant Start** (No setup required!)

Bielik now works **without any external dependencies**. Just install and start chatting:

```bash
# Install minimal version
pip install bielik

# Start CLI and choose your first model
python -m bielik
```

**What happens on first run:**
- 🔍 **Model Selection** — Choose from available Polish models
- 📥 **Auto Download** — Selected model downloads from HuggingFace
- 🔄 **Auto Switch** — Automatically switches to the new model
- 💬 **Ready to Chat** — Start conversing in Polish immediately!

### 📱 **Choose Your Experience**

#### 🪶 **Minimal Setup** (Recommended)
Perfect for text conversations and document analysis:
```bash
# 1. Install
pip install bielik

# 2. Start and download your first model
python -m bielik
:download speakleash/bielik-4.5b-v3.0-instruct

# 3. Start chatting in Polish!
Cześć! Jak mogę Ci pomóc?
```

#### 🎯 **Full Setup** (For image analysis)
Includes vision capabilities for image analysis:
```bash
# 1. Install with vision support
pip install bielik[vision]

# 2. Start and download models
python -m bielik
:download speakleash/bielik-4.5b-v3.0-instruct

# 3. Analyze images
Przeanalizuj to zdjęcie: image.jpg
```

#### 🐳 **Docker Setup** (For testing)
Use Docker for isolated testing environments:
```bash
# Clone repository
git clone https://github.com/tom-sapletta-com/bielik.git
cd bielik

# Test minimal version
docker-compose --profile minimal up bielik-minimal

# Test full version  
docker-compose --profile full up bielik-full
```

---

## 💻 Usage

### 🖥️ CLI Commands & Options

#### Starting Bielik

```bash
# Basic usage
python -m bielik                         # Start interactive chat
bielik                                   # Alternative (if in PATH)

# Advanced options  
python -m bielik --help                  # Show all options
```

#### Interactive Commands (inside chat session)

**📋 Model Management:**
```bash
:models                    # List available HuggingFace models
:download <model-name>     # Download model from HuggingFace
:switch <model-name>       # Switch to downloaded model
:delete <model-name>       # Delete model from local storage
```

**⚙️ Personalization:**
```bash
:name <your-name>          # Set your display name
:settings                  # Show current configuration
```

**🛠️ Utilities:**
```bash
:help                      # Show all commands
:clear                     # Clear conversation history
:exit                      # Quit (or Ctrl+C)
```

#### Usage Examples

**First Time Setup:**
```bash
$ python -m bielik
# Choose from recommended models:
# 1. speakleash/bielik-4.5b-v3.0-instruct (Recommended)
# 2. speakleash/bielik-7b-instruct-v0.1
# Enter choice: 1

🔄 Downloading speakleash/bielik-4.5b-v3.0-instruct...
✅ Model ready! Switching to bielik-4.5b-v3.0-instruct

👤 You: Cześć! Jak się masz?
🤖 bielik-4.5b: Cześć! Mam się dobrze, dziękuję...
```

**Everyday Usage:**
```bash
👤 You: :name Jan
✅ Display name set to: Jan

👤 Jan: Przeanalizuj folder ~/dokumenty
🤖 bielik-4.5b: [Analyzes folder structure and contents]

👤 Jan: Opisz to zdjęcie: vacation.jpg  # (Full version only)
🤖 bielik-4.5b: [Describes image in Polish]
```

### 🐍 Python API

Use Bielik programmatically in your Python applications:

```python
from bielik.client import BielikClient

# Create client (auto-downloads model if needed)
client = BielikClient()

# Send a Polish message
response = client.chat("Napisz krótki wiersz o Polsce")
print(response)

# Get model status
status = client.get_status()
print(f"Current model: {status['current_model']}")
print(f"Models available: {status['models_available']}")

# Export conversation
history = client.export_conversation(format="markdown")
```

**Quick functions:**
```python
from bielik.client import quick_chat

# One-off Polish query
response = quick_chat("Co to jest sztuczna inteligencja?")
print(response)
```

**BielikClient Options:**
- `model`: Specific HuggingFace model to use
- `auto_download`: Auto-download model if missing (default: True)

### 🌐 Web Server

```bash
# Start web server
uvicorn bielik.server:app --port 8000

# Or with Docker
docker-compose --profile minimal up bielik-minimal
```

**Endpoints:**
- `POST /chat` - JSON chat endpoint
- `WS /ws` - WebSocket real-time chat
- `GET /models` - List available models

**Example request:**
```json
{"messages": [{"role":"user","content":"Cześć! Jak się masz?"}]}
```

### 🐳 Docker Usage

**Quick Testing:**
```bash
# Test minimal version
docker run -it bielik:minimal

# Test full version with GPU
docker run --gpus all -it bielik:full
```

**With persistent storage:**
```bash
# Minimal with model persistence
docker run -it -v $(pwd)/models:/app/models bielik:minimal

# Full with models and images
docker run -it \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/images:/app/images \
  bielik:full
```

**Development setup:**
```bash
# Clone and test
git clone https://github.com/tom-sapletta-com/bielik.git
cd bielik

# Run automated tests
docker-compose --profile test up test-runner

# Interactive development
docker-compose --profile minimal run --rm bielik-minimal bash
```

---

## 🔧 Environment Variables

**Core Settings:**
* `BIELIK_CLI_USERNAME` — Your display name in CLI (auto-detected from system)
* `BIELIK_CLI_CURRENT_MODEL` — Currently selected model
* `BIELIK_CLI_ASSISTANT_NAME` — Assistant display name (auto-set from model)
* `BIELIK_CLI_AUTO_SWITCH` — Auto-switch to newly downloaded models (default: true)

**Storage & Cache:**
* `BIELIK_MODELS_DIR` — Local model storage directory
* `BIELIK_DATA_DIR` — User data and settings directory
* `HF_HOME` — HuggingFace cache directory

**Docker Environment:**
* `BIELIK_MODE` — `minimal` or `full` (Docker only)
* `BIELIK_IMAGES_DIR` — Images directory for analysis (full version)

---

## 🛠️ Troubleshooting

### Installation Issues

**Problem:** Minimal version works but vision features don't
```bash
# Upgrade to full version
pip install bielik[vision]

# Verify vision packages
python -c "import PIL, transformers; print('Vision packages OK')"
```

**Problem:** Model download fails or times out
```bash
# Check HuggingFace connectivity
python -c "from huggingface_hub import HfApi; print('HF connection OK')"

# Check available disk space (models are 2-8GB)
df -h

# Manual download with timeout
:download speakleash/bielik-4.5b-v3.0-instruct
```

**Problem:** "No models available" on first startup
```bash
# Download a model manually
python -m bielik
:models
:download speakleash/bielik-4.5b-v3.0-instruct
```

### Runtime Issues

**Problem:** Model responses are slow or use too much memory
```bash
# Use smaller model
:switch speakleash/bielik-4.5b-v3.0-instruct  # instead of 7b

# Check system resources
htop      # Linux/macOS
taskmgr   # Windows

# Enable GPU acceleration (full version)
pip install bielik[gpu]
```

**Problem:** Image analysis not working
```bash
# Check if vision packages installed
python -c "from bielik.image_analyzer import ImageAnalyzer; ia = ImageAnalyzer(); print(f'Available: {ia.is_available()}')"

# Install vision support
pip install bielik[vision]
```

**Problem:** CLI settings not persisting
```bash
# Check .env file creation
ls -la ~/.bielik/ || ls -la ./

# Reset settings
:name YourName
:settings
```

### Docker Issues

**Problem:** Docker containers fail to start
```bash
# Build images manually
docker build -f docker/Dockerfile.minimal -t bielik:minimal .
docker build -f docker/Dockerfile.full -t bielik:full .

# Check container logs
docker logs bielik-minimal
```

**Problem:** Models not persisting between Docker runs
```bash
# Use volume mounts
docker run -v $(pwd)/models:/app/models bielik:minimal

# Or use Docker Compose
docker-compose --profile minimal up
```

### Getting Help

- **GitHub Issues:** [Report bugs and feature requests](https://github.com/tom-sapletta-com/bielik/issues)
- **Command Help:** `python -m bielik --help` or `:help` in CLI
- **Test Environment:** Use Docker for isolated testing
- **Check Status:** Use `:settings` command for current configuration

---

## 🛠️ **Creating Custom Context Provider Commands**

Bielik CLI supports **extensible Context Provider Commands** that allow you to create custom `name:` commands that generate structured context data for AI analysis.

### 📋 **Quick Setup Guide**

**1. Create command directory:**
```bash
mkdir -p commands/mycommand
cd commands/mycommand
```

**2. Create your command files:**
- `main.py` - Your command implementation
- `config.json` - Command configuration and metadata

### 🐍 **Python Code Examples**

#### **Basic Context Provider Command Template**

```python
# commands/mycommand/main.py
from typing import List, Dict, Any
from bielik.cli.command_api import ContextProviderCommand

class MyCommand(ContextProviderCommand):
    def __init__(self):
        super().__init__(
            name="mycommand",
            description="Custom context provider that analyzes something",
            usage="mycommand: <path_or_input>"
        )
    
    def provide_context(self, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate context data from the provided arguments.
        
        Args:
            args: List of arguments after 'mycommand:'
            context: Additional context data
            
        Returns:
            Dict containing structured context data
        """
        if not args:
            return {
                "error": "Please provide input after 'mycommand:'",
                "usage": self.get_usage()
            }
        
        input_data = " ".join(args)
        
        # Your custom logic here
        analysis_result = self._analyze_input(input_data)
        
        return {
            "command": "mycommand",
            "input": input_data,
            "analysis": analysis_result,
            "timestamp": context.get("timestamp", ""),
            "context_type": "custom_analysis"
        }
    
    def _analyze_input(self, input_data: str) -> Dict[str, Any]:
        """Custom analysis logic - implement your functionality here."""
        return {
            "input_length": len(input_data),
            "word_count": len(input_data.split()),
            "type": "text_analysis",
            "summary": f"Analyzed text with {len(input_data)} characters"
        }

# Required: Command instance for the registry
command = MyCommand()
```

#### **Advanced Example: Git Repository Analyzer**

```python
# commands/git/main.py
import os
import subprocess
from typing import List, Dict, Any
from bielik.cli.command_api import ContextProviderCommand

class GitCommand(ContextProviderCommand):
    def __init__(self):
        super().__init__(
            name="git",
            description="Analyzes Git repository information and recent commits",
            usage="git: [path_to_repo]"
        )
    
    def provide_context(self, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        repo_path = args[0] if args else "."
        
        if not self._is_git_repo(repo_path):
            return {
                "error": f"Not a git repository: {repo_path}",
                "suggestion": "Run this command in a git repository directory"
            }
        
        return {
            "command": "git",
            "repository_path": os.path.abspath(repo_path),
            "branch_info": self._get_branch_info(repo_path),
            "recent_commits": self._get_recent_commits(repo_path),
            "status": self._get_status(repo_path),
            "remote_info": self._get_remote_info(repo_path),
            "context_type": "git_analysis"
        }
    
    def _is_git_repo(self, path: str) -> bool:
        """Check if directory is a git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=path, capture_output=True, text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _get_branch_info(self, path: str) -> Dict[str, str]:
        """Get current branch information."""
        try:
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=path, capture_output=True, text=True
            )
            return {
                "current_branch": branch_result.stdout.strip(),
                "status": "active"
            }
        except:
            return {"error": "Could not determine branch info"}
    
    def _get_recent_commits(self, path: str, limit: int = 5) -> List[Dict[str, str]]:
        """Get recent commit information."""
        try:
            result = subprocess.run([
                "git", "log", "--oneline", f"-{limit}",
                "--pretty=format:%h|%an|%ar|%s"
            ], cwd=path, capture_output=True, text=True)
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    hash_id, author, date, message = line.split('|', 3)
                    commits.append({
                        "hash": hash_id,
                        "author": author,
                        "date": date,
                        "message": message
                    })
            return commits
        except:
            return [{"error": "Could not fetch commit history"}]
    
    def _get_status(self, path: str) -> Dict[str, Any]:
        """Get git status information."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=path, capture_output=True, text=True
            )
            
            modified_files = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    status, filename = line[:2], line[3:]
                    modified_files.append({
                        "file": filename,
                        "status": status.strip()
                    })
            
            return {
                "modified_files": modified_files,
                "clean": len(modified_files) == 0
            }
        except:
            return {"error": "Could not get status"}
    
    def _get_remote_info(self, path: str) -> Dict[str, str]:
        """Get remote repository information."""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=path, capture_output=True, text=True
            )
            return {
                "origin_url": result.stdout.strip(),
                "has_remote": True
            }
        except:
            return {"has_remote": False}

# Required: Command instance for the registry
command = GitCommand()
```

### 📄 **Configuration File (config.json)**

```json
{
  "name": "mycommand",
  "description": "Custom context provider for specialized analysis",
  "version": "1.0.0",
  "author": "Your Name",
  "category": "analysis",
  "usage_examples": [
    {
      "command": "mycommand: sample input text",
      "description": "Analyzes the provided text input"
    },
    {
      "command": "mycommand: /path/to/file",
      "description": "Analyzes content from a file path"
    }
  ],
  "requirements": [
    "python>=3.8"
  ],
  "optional_dependencies": [
    "numpy",
    "requests"
  ],
  "tags": ["analysis", "custom", "text"]
}
```

### 🚀 **Using Your Custom Command**

After creating your command, restart Bielik CLI to load it:

```bash
# Restart Bielik CLI
./run.py

# Your command will now be available:
mycommand: analyze this text

# Check if it's loaded:
:help
```

### 🔍 **Context Provider Command Features**

**Built-in capabilities:**
- ✅ **Automatic loading** from `commands/` directory
- ✅ **Error handling** and validation
- ✅ **Help generation** from docstrings and config
- ✅ **Context integration** with AI prompts
- ✅ **Argument parsing** from `name: args` format
- ✅ **Multiple command support** in single session

**What makes a good Context Provider:**
- 📊 **Structured output** - Return organized, meaningful data
- 🎯 **Specific purpose** - Focus on one type of analysis
- ⚡ **Fast execution** - Avoid long-running operations
- 📝 **Clear documentation** - Good descriptions and examples
- 🛡️ **Error handling** - Graceful failure with helpful messages

### 🌟 **Real-world Examples**

**Available Context Providers:**
```bash
folder: .              # Analyze directory structure and files
calc: 2+3*4           # Mathematical calculations  
pdf: document.pdf     # PDF document analysis
git: /path/to/repo    # Git repository information (example above)
```

**Example workflow:**
```bash
👤 You: folder: ~/projects
✅ Context loaded! Directory analysis complete.

👤 You: What are the largest Python files in this project?
🤖 AI: [Uses folder context to identify and analyze Python files]

👤 You: git: .
✅ Context loaded! Git repository analysis complete.

👤 You: Summarize recent commits and current status
🤖 AI: [Uses git context to provide commit summaries and status]
```

---

## 📝 Development

```bash
git clone https://github.com/tom-sapletta-com/bielik.git
cd bielik
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -e .[local]
pip install -e .[dev]
pip install -e .[gpu]
pip install -e .[vision]
```


# 🐳 Docker Testing Framework

Bielik CLI includes a comprehensive Docker testing framework for multiplatform installation verification across all major Linux distributions.

## Available Docker Tests

```bash
# Complete multiplatform test suite (all distributions)
make docker-test

# Individual distribution tests
make docker-test-ubuntu    # Ubuntu 22.04
make docker-test-debian    # Debian 12
make docker-test-alpine    # Alpine Linux 3.19
make docker-test-centos    # CentOS Stream 9
make docker-test-arch      # Arch Linux
make docker-test-oneliner  # One-liner installation simulation

# Docker management
make docker-build          # Build all test images
make docker-clean          # Clean Docker artifacts

# Complete test suite (Python + Docker)
make test-all              # Run both unit tests and Docker tests
```

## What Docker Tests Verify

✅ **Installation Success**: Bielik CLI installs without errors  
✅ **Context Provider Commands**: `folder:`, `calc:`, `pdf:` work correctly  
✅ **Cross-platform Compatibility**: Works on Ubuntu, Debian, Alpine, CentOS, Arch  
✅ **One-liner Installation**: `curl | bash` installation process  
✅ **Dependency Management**: Python packages install correctly  
✅ **Virtual Environment**: `.venv` setup and activation  

## Docker Test Architecture

```
docker/
├── test-multiplatform.yml     # Docker Compose configuration
├── Dockerfile.test-ubuntu     # Ubuntu 22.04 test environment
├── Dockerfile.test-debian     # Debian 12 test environment  
├── Dockerfile.test-alpine     # Alpine Linux 3.19 test environment
├── Dockerfile.test-centos     # CentOS Stream 9 test environment
├── Dockerfile.test-arch       # Arch Linux test environment
└── Dockerfile.test-oneliner   # One-liner installation test
```

Each test environment:
1. **Sets up clean Linux distribution**
2. **Installs system dependencies** (Python, git, build tools)
3. **Runs `python3 install.py --skip-ai`** to install Bielik with Context Provider Commands
4. **Verifies installation** with `python3 run.py --info`
5. **Tests Context Provider Commands** (folder analysis, calculations)

## Running Docker Tests in CI/CD

```yaml
# GitHub Actions example
- name: Run multiplatform Docker tests
  run: make docker-test

- name: Run specific distribution test
  run: make docker-test-ubuntu
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
│   │   ├── command_api.py   # Context Provider Commands API
│   │   ├── models.py        # HF model management CLI
│   │   ├── setup.py         # Interactive setup manager
│   │   └── send_chat.py     # Chat communication handling
│   └── client/              # Modular client components
│       ├── __init__.py      # Client package exports
│       ├── core.py          # Core BielikClient class
│       ├── model_manager.py # HF model operations for client
│       └── utils.py         # Client utility functions
├── commands/                # Context Provider Commands
│   ├── folder/             # Directory analysis command
│   ├── calc/               # Advanced calculator command
│   └── pdf/                # Document processing command
├── docker/                 # Docker testing framework
│   ├── test-multiplatform.yml
│   └── Dockerfile.test-*   # Test environments
├── tests/
│   ├── __init__.py
│   ├── test_cli.py          # CLI unit tests (updated for local HF models)
│   └── test_server.py       # Server unit tests
├── install.py              # Universal Python installer
├── run.py                  # Universal launcher
├── quick-install.sh        # Unix one-liner installer
├── quick-install.bat       # Windows one-liner installer
├── pyproject.toml          # Modern Python packaging
├── setup.cfg               # Package configuration
├── MANIFEST.in             # Package manifest
├── LICENSE                 # Apache 2.0 license
├── README.md               # This comprehensive documentation
├── Makefile                # Development automation with Docker tests
├── todo.md                 # Project specifications
└── .github/workflows/      # CI/CD automation
    └── python-publish.yml
```



## 📜 License

[Apache License 2.0](LICENSE)


