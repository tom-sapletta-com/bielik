# 🏗️ System Architecture

Technical architecture and design documentation for Bielik Polish AI Assistant CLI.

## 📋 **Navigation Menu**
- [🏠 Documentation Home](README.md)
- [📥 Installation](INSTALLATION.md)
- [⚡ Usage Guide](USAGE.md)
- [🤝 Contributing](CONTRIBUTING.md)

---

## 🎯 **System Overview**

Bielik is designed as a modular, extensible Polish AI assistant with three main interfaces: CLI, Python API, and Web Server. The system prioritizes local model execution for privacy and performance.

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
│  │ ┌─ HF Hub API        │    │ ┌─ llama-cpp-python         │  │
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

---

## 🧱 **Core Components**

### 1. **CLI Interface** (`bielik/cli/`)

**Purpose**: Primary user interface for Polish AI conversations

**Components:**
- `main.py` - Entry point, argument parsing, prompt execution
- `commands.py` - Built-in CLI commands (`:help`, `:models`, `:setup`)
- `command_api.py` - Context Provider Commands registry and execution
- `send_chat.py` - Chat communication with local models
- `models.py` - HuggingFace model management
- `setup.py` - Interactive system configuration

**Key Features:**
- ✅ Personalized user experience with names and settings
- ✅ Context Provider Commands (`folder:`, `calc:`, `pdf:`)
- ✅ Model management (download, switch, delete)
- ✅ Project-based artifact collection
- ✅ Multi-modal support (text + images)

### 2. **Python Client** (`bielik/client/`)

**Purpose**: Programmatic access to Bielik functionality

**Components:**
- `core.py` - Main BielikClient class
- `model_manager.py` - HuggingFace model operations
- `utils.py` - Utility functions and helpers

**Key Features:**
- ✅ Simple `chat()` and `query()` methods
- ✅ Automatic model management
- ✅ Conversation export functionality
- ✅ Status and configuration access

### 3. **Web Server** (`bielik/server.py`)

**Purpose**: REST API and WebSocket interface

**Endpoints:**
- `POST /chat` - JSON chat endpoint
- `WS /ws` - WebSocket real-time chat
- `GET /models` - List available models
- `GET /health` - Health check

### 4. **Context Provider Commands** (`commands/`)

**Purpose**: Extensible command system for data analysis

**Architecture:**
```
commands/
├── folder/          # Directory analysis
│   ├── main.py      # Implementation
│   └── config.json  # Metadata
├── calc/           # Mathematical calculations
│   ├── main.py
│   └── config.json
└── pdf/           # Document processing
    ├── main.py
    └── config.json
```

**Features:**
- ✅ Standardized `name:` command format
- ✅ Automatic registration and loading
- ✅ Independent operation (no AI model required)
- ✅ Structured context generation for AI analysis

---

## 🔄 **Data Flow Architecture**

### **CLI Chat Flow**
```
User Input → Prompt Processing → Context Provider Check → Model Loading → Response Generation
     ↓              ↓                    ↓                    ↓              ↓
[bielik -p]    [main.py]         [command_api.py]     [local_runner.py]  [send_chat.py]
     ↓              ↓                    ↓                    ↓              ↓
  "calc: 2+3"  → Parse command    → Execute calc:     → Skip (direct)    → Return "5"
  "Hello"      → Regular prompt   → No command        → Load model       → AI response
```

### **Context Provider Flow**
```
Context Command → Parse Arguments → Execute Provider → Generate Context → Return Result
       ↓               ↓                   ↓                ↓              ↓
   "folder: ."    ["folder:", "."]    FolderCommand    File listing    Structured data
   "calc: 2+3"    ["calc:", "2+3"]    CalcCommand     Evaluation       "Result: 5"
   "pdf: doc.pdf" ["pdf:", "doc.pdf"] PdfCommand      Text extraction  Document content
```

### **Model Management Flow**
```
User Command → HF Hub Check → Download → Local Storage → Model Registration → Switch Active
     ↓              ↓            ↓           ↓                ↓                  ↓
:download model → API call → .safetensors  ~/.cache/    model_registry.json  Update .env
```

---

## 🏛️ **Package Structure**

```
bielik/
├── bielik/                      # Main package
│   ├── __init__.py             # Package exports
│   ├── cli.py                  # CLI entry point wrapper
│   ├── client.py               # Client API wrapper
│   ├── server.py               # FastAPI web server
│   ├── config.py               # Configuration management
│   ├── content_processor.py    # Content analysis utilities
│   ├── cli/                    # Modular CLI components
│   │   ├── main.py            # Main CLI logic
│   │   ├── commands.py        # Built-in commands
│   │   ├── command_api.py     # Context Provider API
│   │   ├── models.py          # Model management
│   │   ├── setup.py           # Interactive setup
│   │   └── send_chat.py       # Chat communication
│   ├── client/                 # Client API components
│   │   ├── core.py            # BielikClient class
│   │   ├── model_manager.py   # Model operations
│   │   └── utils.py           # Utilities
│   └── models/                 # Model execution
│       ├── model_manager.py   # Local model management
│       └── local_runner.py    # llama-cpp-python interface
├── commands/                   # Context Provider Commands
│   ├── folder/                 # Directory analysis
│   ├── calc/                   # Calculator
│   └── pdf/                    # Document processing
├── docker/                     # Docker testing framework
├── scripts/                    # Utility scripts
└── tests/                      # Unit tests
```

---

## 🔧 **Technical Specifications**

### **Core Dependencies**
- **Python 3.11+** - Modern Python features and performance
- **llama-cpp-python** - Local model execution (CPU/GPU)
- **huggingface-hub** - Model downloads and management
- **typer** - CLI framework with rich features
- **rich** - Beautiful terminal output
- **fastapi** - Web server framework
- **uvicorn** - ASGI server

### **Optional Dependencies**
- **transformers** - Vision model support
- **torch** - GPU acceleration
- **PIL/Pillow** - Image processing
- **pypdf** - PDF document processing
- **python-docx** - DOCX document processing

### **Performance Optimizations**
- **Lazy Loading** - Models loaded only when needed
- **Model Caching** - HuggingFace cache management
- **CPU Acceleration** - MKL, OpenBLAS, Intel optimizations
- **Memory Management** - Efficient tokenization and batching

---

## 🎯 **Design Principles**

### **1. Modularity**
- **Separation of Concerns** - CLI, Client, Server are independent
- **Plugin Architecture** - Context Provider Commands are extensible
- **Interface Consistency** - Common patterns across all components

### **2. Privacy First**
- **Local Execution** - All model processing happens locally
- **No External APIs** - No data sent to external services
- **Offline Capable** - Works without internet after model download

### **3. Polish Language Focus**
- **Native Polish Support** - Optimized for Polish conversations
- **Cultural Context** - Understanding of Polish context and nuances
- **Speakleash Integration** - Direct access to Speakleash models

### **4. Developer Experience**
- **Simple APIs** - Easy-to-use Python interfaces
- **Comprehensive Documentation** - Detailed guides and examples
- **Testing Framework** - Docker-based multiplatform testing
- **Type Safety** - Full type hints and mypy compatibility

---

## 🔄 **Extension Points**

### **1. Context Provider Commands**
Create custom commands by implementing `ContextProviderCommand`:
```python
class MyCommand(ContextProviderCommand):
    name = "mycommand"
    is_context_provider = True
    
    def provide_context(self, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        # Your logic here
        return {"type": "custom", "data": "processed"}
```

### **2. Model Backends**
Extend model support by implementing model runners:
```python
class CustomModelRunner:
    def load_model(self, model_path: str):
        # Custom model loading
        pass
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        # Custom inference
        pass
```

### **3. Output Formatters**
Add custom output formatting:
```python
class CustomFormatter:
    def format_response(self, response: str, context: Dict) -> str:
        # Custom formatting logic
        return formatted_response
```

---

## 🛡️ **Security Architecture**

### **Data Protection**
- ✅ **Local Processing** - No external API calls
- ✅ **Sandboxed Execution** - Context Provider Commands run safely
- ✅ **Input Validation** - All user inputs validated and sanitized
- ✅ **Path Restrictions** - File access limited to safe directories

### **Model Security**
- ✅ **Verified Sources** - Only trusted HuggingFace models
- ✅ **Checksum Validation** - Model integrity verification
- ✅ **Safe Loading** - Secure model deserialization

### **Network Security**
- ✅ **HTTPS Downloads** - Secure model downloads from HF Hub
- ✅ **No Telemetry** - No usage data collection
- ✅ **Local Servers** - Web server binds to localhost only

---

## 🚀 **Performance Characteristics**

### **Startup Time**
- **Cold Start**: ~2-3 seconds (without model loading)
- **Model Loading**: ~10-30 seconds (first time, then cached)
- **Warm Start**: ~1 second (subsequent runs)

### **Memory Usage**
- **Base CLI**: ~50MB RAM
- **With 4.5B Model**: ~3-5GB RAM
- **With 7B Model**: ~6-8GB RAM
- **Context Provider Commands**: ~10-50MB RAM

### **Response Times**
- **Context Provider Commands**: <1 second
- **AI Responses**: 0.3-2 tokens/second (CPU), 10-50 tokens/second (GPU)
- **Model Switching**: ~5-15 seconds

---

## 🔮 **Future Architecture**

### **Planned Enhancements**
- **Plugin System** - Dynamic plugin loading and management
- **Distributed Models** - Support for model sharding and distribution
- **Advanced Caching** - Intelligent response caching and retrieval
- **Multi-language** - Support for additional languages beyond Polish

### **Scalability Considerations**
- **Horizontal Scaling** - Multiple server instances
- **Load Balancing** - Request distribution across models
- **Resource Management** - Dynamic resource allocation
- **Container Orchestration** - Kubernetes deployment support

---

**Next Steps:** [Usage Guide](USAGE.md) | [API Documentation](API.md) | [Context Providers](CONTEXT_PROVIDERS.md)
