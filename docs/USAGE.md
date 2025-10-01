# 💻 Usage Guide

Complete usage guide with examples and workflows for Bielik Polish AI Assistant CLI.

## 📋 **Navigation Menu**
- [🏠 Documentation Home](README.md)
- [📥 Installation](INSTALLATION.md)
- [🏗️ Architecture](ARCHITECTURE.md)
- [🤝 Contributing](CONTRIBUTING.md)

---

## ⚡ **Quick Start**

### 🚀 **First Time Setup**

```bash
# 1. Start Bielik CLI
bielik

# 2. Choose your first model (interactive selection)
# Available models:
# 1. speakleash/bielik-4.5b-v3.0-instruct (Recommended)
# 2. speakleash/bielik-7b-instruct-v0.1
# Enter choice: 1

# 3. Model downloads automatically
🔄 Downloading speakleash/bielik-4.5b-v3.0-instruct...
✅ Model ready! Switching to bielik-4.5b-v3.0-instruct

# 4. Start chatting in Polish!
👤 You: Cześć! Jak się masz?
🤖 bielik-4.5b: Cześć! Mam się dobrze, dziękuję za pytanie...
```

### 🎯 **Instant Context Provider Commands** (No AI model needed)

```bash
# Mathematical calculations (instant results)
bielik -p "calc: 2 + 3 * 4"
# Output: 🧮 2 + 3 * 4 = 14

# Directory analysis
bielik -p "folder: ."
# Output: Structured directory listing with file analysis

# Document processing
bielik -p "pdf: document.pdf"
# Output: Extracted text and metadata from PDF
```

---

## 🖥️ **CLI Interface**

### **Starting Bielik**

```bash
# Interactive chat session
bielik                           # or python -m bielik
python run.py                    # Universal launcher
./run.sh                         # Linux/macOS
run.bat                         # Windows

# Single prompt execution (non-interactive)
bielik -p "napisz wiersz o Polsce"
bielik --prompt "What is 2+2?" --model bielik-4.5b

# Show help and options
bielik --help
```

### **Command Line Options**

```bash
# Model selection
bielik -m bielik-7b-instruct                    # Use specific model
bielik --local-model bielik-4.5b-v3.0-instruct # Force local model

# System configuration
bielik --setup                                  # Run interactive setup
bielik --no-setup                              # Skip auto-configuration

# Testing and debugging
bielik --test-model                            # Run model performance tests
bielik --test-model -m bielik-4.5b-v3.0       # Test specific model
```

---

## 💬 **Interactive Chat Commands**

### **📋 Model Management**
```bash
:models                    # List all available HuggingFace models
:download <model-name>     # Download model from HuggingFace
:switch <model-name>       # Switch to downloaded model
:delete <model-name>       # Delete model from local storage
:model <model-name>        # Alias for :switch
```

**Example:**
```bash
👤 You: :models
📋 Available HuggingFace Models:
✅ bielik-4.5b-v3.0-instruct (active)
📥 bielik-7b-instruct (available for download)

👤 You: :download bielik-7b-instruct
🔄 Downloading bielik-7b-instruct from HuggingFace...
✅ Model downloaded! Automatically switching to bielik-7b-instruct

👤 You: :switch bielik-4.5b-v3.0-instruct
✅ Switched to model: bielik-4.5b-v3.0-instruct
```

### **⚙️ Personalization**
```bash
:name <your-name>          # Set your display name
:settings                  # Show current configuration
:clear                     # Clear conversation history
```

**Example:**
```bash
👤 You: :name Anna
✅ Display name set to: Anna

👤 Anna: :settings
⚙️ Current Settings:
👤 Username: Anna
🤖 Assistant: bielik-4.5b
🔧 Model: speakleash/bielik-4.5b-v3.0-instruct
🔄 Auto-switch: enabled
```

### **🛠️ Utilities**
```bash
:help                      # Show all commands and usage
:storage                   # Show storage statistics and model sizes
:download-bielik          # Download recommended Polish Bielik models
:exit                      # Quit session (or Ctrl+C)
```

### **🔧 Extension Commands**
```bash
:project                   # Session-based project management
:project create "My Analysis"  # Create new project
:project list              # List all projects
:project open              # Open current project in browser
```

---

## 🎯 **Context Provider Commands**

Context Provider Commands provide instant, structured data analysis without requiring AI model loading.

### **📁 Directory Analysis**
```bash
# Basic directory listing
bielik -p "folder: ."
bielik -p "folder: ~/Documents"

# Recursive analysis
bielik -p "folder: . --recursive"
bielik -p "folder: ~/projects --depth=2"

# Filter by file types
bielik -p "folder: . --include=*.py,*.md"
bielik -p "folder: ~/code --exclude=*.pyc,__pycache__"
```

**Output Example:**
```
=== Context from folder: ===
type: directory_analysis
path: /home/user/project
total_files: 25
total_size: 2.3MB
file_types: {'.py': 15, '.md': 5, '.json': 3, '.txt': 2}
largest_files: [
  {'name': 'main.py', 'size': '125KB'},
  {'name': 'README.md', 'size': '45KB'}
]
=== End Context ===
```

### **🧮 Advanced Calculator**
```bash
# Basic arithmetic
bielik -p "calc: 2 + 3 * 4"
bielik -p "calc: (15 + 25) / 2"

# Mathematical functions
bielik -p "calc: sqrt(144) + sin(pi/2)"
bielik -p "calc: factorial(5)"
bielik -p "calc: log(100, 10)"

# Complex expressions
bielik -p "calc: 2^8 + sqrt(49) * cos(0)"
bielik -p "calc: abs(-42) + max(1, 5, 3)"
```

**Output Example:**
```
🧮 sqrt(144) + sin(pi/2) = 13.0

=== Context from calc: ===
type: calculation
expression: sqrt(144) + sin(pi/2)
result: 13.0
steps: [
  'sqrt(144) = 12.0',
  'sin(pi/2) = 1.0', 
  '12.0 + 1.0 = 13.0'
]
=== End Context ===
```

### **📄 Document Processing**
```bash
# PDF text extraction
bielik -p "pdf: document.pdf"
bielik -p "pdf: report.pdf --pages=1-5"

# DOCX processing
bielik -p "pdf: document.docx"
bielik -p "pdf: letter.docx --metadata"

# Text file analysis
bielik -p "pdf: readme.txt"
bielik -p "pdf: code.py --syntax-highlight"
```

**Output Example:**
```
=== Context from pdf: ===
type: document
filename: report.pdf
pages: 12
word_count: 2847
language: polish
content: "Raport roczny za 2024 rok..."
metadata: {
  'author': 'Jan Kowalski',
  'created': '2024-01-15',
  'title': 'Raport Roczny'
}
=== End Context ===
```

---

## 🚀 **Project Management System**

Bielik features a comprehensive project management system that organizes analysis artifacts into beautiful HTML projects.

### **📋 Project Commands**
```bash
# Create new project
:project create "Website Analysis"
:project create "ML Research" "Machine learning project" --tags ml,research

# Project navigation
:project list                    # List all projects
:project switch website-analysis # Switch to project
:project info                    # Show current project details

# Project actions
:project open                    # Open in browser
:project validate               # Validate project integrity
```

### **🎨 Complete Project Workflow**

```bash
# 1. Start interactive session
bielik

# 2. Create project
👤 You: :project create "Company Analysis" "Analyzing company structure and files"
✅ Project Created Successfully
🎯 Project is now active. Use Context Provider Commands to add artifacts.

# 3. Add artifacts using Context Provider Commands
👤 You: folder: ~/company-data
🎯 Artifact Added to Project: Company Analysis
📊 Directory structure with 147 files analyzed

👤 You: calc: total_revenue * 0.15
🎯 Artifact Added to Project: Company Analysis  
🧮 Tax calculation: 45,750 PLN

👤 You: pdf: financial-report.pdf
🎯 Artifact Added to Project: Company Analysis
📄 Financial report processed (23 pages)

# 4. Use AI to analyze collected data
👤 You: Based on the analyzed files and calculations, what are the key financial trends?
🤖 bielik-4.5b: [Analyzes all collected artifacts and provides insights]

# 5. View project
👤 You: :project open
🌐 Project opened in browser: file:///home/user/bielik_projects/abc123.../index.html
```

### **📊 Project Features**

- **🎯 Automatic Artifact Collection** - Context Provider Commands automatically save to active project
- **🌐 Beautiful HTML Output** - Interactive project dashboards
- **📊 Rich Metadata** - Embedded project information and tracking
- **🔍 Validation System** - Comprehensive integrity checking
- **📁 Organized Storage** - Projects stored in `./bielik_projects/`

---

## 🖼️ **Multi-modal Features** (Full Version)

### **Image Analysis**
```bash
# Image description in Polish
👤 You: Opisz to zdjęcie: vacation.jpg
🤖 bielik-4.5b: To zdjęcie pokazuje piękny krajobraz górski...

# Visual question answering
👤 You: Co widzisz na tym obrazku: chart.png
👤 You: Ile osób jest na zdjęciu family.jpg?

# Combined analysis
👤 You: folder: ~/photos
👤 You: Przeanalizuj wszystkie zdjęcia w tym folderze
```

### **Document + Image Processing**
```bash
# PDF with images
👤 You: pdf: presentation.pdf
👤 You: Przeanalizuj tekst i obrazki z tej prezentacji

# Mixed content analysis
👤 You: folder: ~/project --include=*.pdf,*.jpg,*.png
👤 You: Stwórz podsumowanie wszystkich dokumentów i zdjęć
```

---

## 🌐 **Web Server Usage**

### **Starting the Server**
```bash
# Start FastAPI server
uvicorn bielik.server:app --port 8000

# Or with Docker
docker-compose --profile minimal up bielik-minimal
```

### **REST API Endpoints**

#### **POST /chat** - Chat Endpoint
```bash
# Simple chat request
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Cześć! Jak się masz?"}
    ]
  }'

# Response
{
  "response": "Cześć! Mam się dobrze, dziękuję...",
  "model": "bielik-4.5b-v3.0-instruct",
  "tokens_used": 47
}
```

#### **WS /ws** - WebSocket Chat
```javascript
// JavaScript WebSocket example
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function(event) {
    ws.send(JSON.stringify({
        "message": "Napisz krótki wiersz o Polsce"
    }));
};

ws.onmessage = function(event) {
    const response = JSON.parse(event.data);
    console.log('AI Response:', response.message);
};
```

#### **GET /health** - Health Check
```bash
curl http://localhost:8000/health

# Response
{
  "status": "healthy",
  "model": "bielik-4.5b-v3.0-instruct",
  "version": "0.2.6"
}
```

---

## 🐍 **Python API Usage**

### **Basic Client Usage**
```python
from bielik.client import BielikClient

# Create client (auto-downloads model if needed)
client = BielikClient()

# Simple chat
response = client.chat("Napisz krótki wiersz o Polsce")
print(response)

# Query with specific model
response = client.query("Co to jest sztuczna inteligencja?", 
                       model="bielik-7b-instruct")
print(response)
```

### **Advanced Client Features**
```python
from bielik.client import BielikClient

client = BielikClient()

# Get model status
status = client.get_status()
print(f"Current model: {status['current_model']}")
print(f"Available models: {status['models_available']}")

# Model management
client.download_model("speakleash/bielik-7b-instruct-v0.1")
client.switch_model("bielik-7b-instruct")

# Conversation management
client.start_conversation()
response1 = client.chat("Jak się nazywasz?")
response2 = client.chat("A ile masz lat?")  # Maintains context

# Export conversation
history = client.export_conversation(format="markdown")
with open("conversation.md", "w") as f:
    f.write(history)
```

### **Quick Functions**
```python
from bielik.client import quick_chat, quick_query

# One-off queries without client setup
response = quick_chat("Co to jest machine learning?")
print(response)

# Quick query with model specification
response = quick_query("Przetłumacz: Hello world", 
                      model="bielik-4.5b-v3.0-instruct")
print(response)
```

### **Context Provider Integration**
```python
from bielik.client import BielikClient
from bielik.cli.command_api import CommandRegistry

client = BielikClient()
registry = CommandRegistry()

# Use Context Provider Commands programmatically
folder_context = registry.execute_command("folder", ["folder:", "."], {})
calc_result = registry.execute_command("calc", ["calc:", "2+3*4"], {})

# Send context to AI for analysis
response = client.chat(f"Analyze this data: {folder_context}")
print(response)
```

---

## 🔧 **Environment Configuration**

### **Using .env File**
```bash
# Create .env file
BIELIK_CLI_USERNAME=Anna
BIELIK_CLI_CURRENT_MODEL=bielik-4.5b-v3.0-instruct
BIELIK_CLI_ASSISTANT_NAME=Bielik-4.5B
BIELIK_CLI_AUTO_SWITCH=true
BIELIK_MODELS_DIR=./models
HF_HOME=~/.cache/huggingface
```

### **Runtime Environment Variables**
```bash
# Debug mode with detailed logging
BIELIK_DEBUG=1 bielik

# Custom model loading timeout
BIELIK_LOAD_TIMEOUT=30 bielik

# Performance optimization
OMP_NUM_THREADS=8 bielik  # CPU threads
CUDA_VISIBLE_DEVICES=0 bielik  # GPU selection
```

---

## 📊 **Usage Patterns and Best Practices**

### **🎯 Efficient Workflows**

1. **Document Analysis Workflow**
```bash
# 1. Create project for document analysis
:project create "Legal Documents Review"

# 2. Analyze document structure
folder: ~/legal-docs

# 3. Process individual documents
pdf: contract.pdf
pdf: terms.pdf
pdf: agreement.pdf

# 4. Ask AI for comprehensive analysis
What are the key legal risks across all analyzed documents?
```

2. **Data Analysis Workflow**
```bash
# 1. Create analysis project
:project create "Sales Data Analysis"

# 2. Analyze data files
folder: ~/sales-data --include=*.csv,*.xlsx

# 3. Perform calculations
calc: monthly_average * 12
calc: growth_rate = (current - previous) / previous * 100

# 4. Get AI insights
Based on the sales data and calculations, what trends do you see?
```

3. **Code Review Workflow**
```bash
# 1. Project setup
:project create "Code Review" "Python project review"

# 2. Analyze codebase
folder: ~/my-project --include=*.py --recursive

# 3. Process key documents
pdf: README.md
pdf: requirements.txt

# 4. AI-powered review
Review this codebase for best practices and potential improvements.
```

### **⚡ Performance Tips**

1. **Model Selection**
   - Use `bielik-4.5b-v3.0-instruct` for general tasks (faster)
   - Use `bielik-7b-instruct` for complex analysis (more accurate)

2. **Context Provider Commands**
   - Use for instant results without model loading
   - Combine multiple commands in projects for comprehensive analysis

3. **Memory Management**
   - Close other applications when using large models
   - Use `:clear` to reset conversation history if needed

4. **Batch Operations**
   - Process multiple files in projects
   - Use folder analysis instead of individual file processing

---

## 🆘 **Common Usage Scenarios**

### **Scenario 1: Research Assistant**
```bash
# Set up research project
:project create "AI Research" "Artificial Intelligence literature review"

# Analyze research papers
pdf: paper1.pdf
pdf: paper2.pdf
pdf: paper3.pdf

# Ask for synthesis
Summarize the key findings from these AI research papers and identify common themes.
```

### **Scenario 2: Business Analysis**
```bash
# Business intelligence project
:project create "Q4 Analysis" "Fourth quarter business review"

# Analyze business documents
folder: ~/business-reports --include=*.pdf,*.xlsx
calc: revenue_growth = (q4_revenue - q3_revenue) / q3_revenue * 100

# Get business insights
What are the key performance indicators and trends for Q4?
```

### **Scenario 3: Educational Support**
```bash
# Study session
:name Student

# Analyze study materials
pdf: textbook-chapter.pdf
pdf: lecture-notes.pdf

# Get explanations
Explain the key concepts from these materials in simple terms.
What are the most important points I should remember for the exam?
```

---

**Next Steps:** [API Documentation](API.md) | [Context Providers](CONTEXT_PROVIDERS.md) | [Contributing](CONTRIBUTING.md)
