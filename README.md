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

> 🇵🇱 **Bielik** to lokalny klient chat do **[Ollama](https://ollama.com)** z interfejsem CLI i web, stworzony specjalnie dla polskiego modelu językowego **[Bielik](https://huggingface.co/speakleash)** od **[Speakleash](https://speakleash.org/)**.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          🦅 BIELIK                             │
├─────────────────────┬───────────────────────┬───────────────────┤
│   🖥️  CLI Shell     │  🌐 FastAPI Server   │  🧪 Test Suite   │
│  ┌─────────────────┐│ ┌───────────────────┐ │ ┌───────────────┐ │
│  │ • Interactive   ││ │ • REST /chat      │ │ │ • Unit tests  │ │
│  │ • Help system   ││ │ • WebSocket /ws   │ │ │ • Mock API    │ │
│  │ • Cross-platform││ │ • Port 8888       │ │ │ • CI/CD       │ │
│  └─────────────────┘│ └───────────────────┘ │ └───────────────┘ │
└─────────────────────┴───────────────────────┴───────────────────┘
            │                       │                       │
            ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    🔄 CONNECTION LAYER                         │
│  ┌──────────────────────┐    ┌─────────────────────────────┐   │
│  │    REST API (main)   │◄──►│   Ollama Library (fallback) │   │
│  │ ┌─ HTTP requests     │    │ ┌─ ollama.chat()           │   │
│  │ └─ /v1/chat/...     │    │ └─ Direct integration      │   │
│  └──────────────────────┘    └─────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   🦙 OLLAMA SERVER                              │
│  ┌─────────────────────────────────────────────────────────────┤
│  │ 📍 localhost:11434 (default)                              │
│  │ 🤖 Model: bielik (Polish LLM)                             │
│  │ 🔗 Links: Speakleash → HuggingFace → Ollama               │
│  └─────────────────────────────────────────────────────────────┤
└─────────────────────────────────────────────────────────────────┘
```

---

## 🤖 About Bielik Model

**Bielik** to przełomowy polski model językowy stworzony przez **[Speakleash](https://speakleash.org/)** - fundację zajmującą się rozwojem polskiej sztucznej inteligencji.

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

- **🖥️ CLI** `bielik` — interactive chat shell with smart fallback system
- **🌐 Web server** (FastAPI on port 8888):  
  - `POST /chat` — RESTful chat endpoint  
  - `WS /ws` — real-time WebSocket chat
- **🔄 Dual connectivity** — REST API primary, ollama lib fallback
- **🧪 Full test coverage** — unit tests with mocked APIs
- **🔧 Developer tools** — Makefile automation, CI/CD ready  

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

## 🚀 Usage

### CLI

```bash
bielik
```

Wpisz wiadomości, zakończ `:exit`.

### Web API

```bash
uvicorn bielik.server:app --port 8888
```

* POST `/chat`:

```json
{"messages": [{"role":"user","content":"Hello!"}]}
```

* WebSocket `/ws`

---

## 🔧 Environment Variables

* `OLLAMA_HOST` — default: `http://localhost:11434`
* `BIELIK_MODEL` — default: `bielik`

---

## 📝 Development

```bash
git clone https://github.com/tomsapletta/bielik.git
cd bielik
python -m venv .venv
source .venv/bin/activate
pip install -e .[ollama]
```


# 📂 Struktura

```
bielik/
├── bielik/
│   ├── __init__.py
│   ├── cli.py
│   └── server.py
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   └── test_server.py
├── pyproject.toml
├── setup.cfg
├── MANIFEST.in
├── LICENSE
├── README.md
├── Makefile
└── .github/workflows/python-publish.yml
```



## 📜 License

[Apache License 2.0](LICENSE)


