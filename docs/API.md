# 🔧 Python API Documentation

Complete Python API reference for Bielik Polish AI Assistant.

## 📋 **Navigation Menu**
- [🏠 Documentation Home](README.md)
- [📥 Installation](INSTALLATION.md)
- [🏗️ Architecture](ARCHITECTURE.md)
- [⚡ Usage Guide](USAGE.md)
- [🤝 Contributing](CONTRIBUTING.md)

---

## 🐍 **Python Client API**

The Bielik Python API provides programmatic access to Polish AI models through a simple, intuitive interface.

### **Quick Start**
```python
from bielik.client import BielikClient

# Create client instance
client = BielikClient()

# Simple chat
response = client.chat("Napisz krótki wiersz o Polsce")
print(response)
```

---

## 📚 **BielikClient Class**

### **Constructor**
```python
from bielik.client import BielikClient

client = BielikClient(
    model: Optional[str] = None,
    auto_download: bool = True,
    config_path: Optional[str] = None
)
```

**Parameters:**
- `model` - Specific HuggingFace model to use
- `auto_download` - Automatically download model if missing (default: True)
- `config_path` - Path to custom configuration file

**Examples:**
```python
# Default client (uses recommended model)
client = BielikClient()

# Specific model
client = BielikClient(model="speakleash/bielik-7b-instruct-v0.1")

# Disable auto-download
client = BielikClient(auto_download=False)
```

### **Chat Methods**

#### **chat(message, maintain_context=True)**
Main chat method with conversation context.

```python
def chat(self, 
         message: str, 
         maintain_context: bool = True) -> str:
    """Send message and get AI response with context.
    
    Args:
        message: User message in Polish or English
        maintain_context: Keep conversation history (default: True)
        
    Returns:
        AI response string
    """
```

**Examples:**
```python
# Simple chat
response = client.chat("Jak się masz?")

# Chat without context (each message independent)
response = client.chat("Co to jest AI?", maintain_context=False)

# Multi-turn conversation
client.chat("Jak się nazywasz?")
response = client.chat("A ile masz lat?")  # Uses previous context
```

#### **query(question, model=None)**
One-off query without conversation context.

```python
def query(self, 
          question: str, 
          model: Optional[str] = None) -> str:
    """Send standalone query without conversation context.
    
    Args:
        question: Standalone question
        model: Optional specific model to use
        
    Returns:
        AI response string
    """
```

**Examples:**
```python
# Simple query
response = client.query("Co to jest sztuczna inteligencja?")

# Query with specific model
response = client.query("Przetłumacz: Hello world", 
                       model="bielik-7b-instruct")
```

### **Conversation Management**

#### **start_conversation()**
Start new conversation session.

```python
def start_conversation(self) -> None:
    """Start new conversation, clearing previous context."""
```

#### **clear_history()**
Clear conversation history.

```python
def clear_history(self) -> None:
    """Clear conversation history while maintaining session."""
```

#### **get_conversation_history()**
Get current conversation messages.

```python
def get_conversation_history(self) -> List[Dict[str, str]]:
    """Get conversation history as list of message dicts.
    
    Returns:
        List of {"role": "user/assistant", "content": "message"} dicts
    """
```

**Example:**
```python
client.chat("Cześć!")
client.chat("Jak się masz?")

history = client.get_conversation_history()
for message in history:
    print(f"{message['role']}: {message['content']}")
```

### **Model Management**

#### **get_available_models()**
List available HuggingFace models.

```python
def get_available_models(self) -> List[str]:
    """Get list of available Polish AI models.
    
    Returns:
        List of model names
    """
```

#### **download_model(model_name)**
Download model from HuggingFace.

```python
def download_model(self, model_name: str) -> bool:
    """Download model from HuggingFace Hub.
    
    Args:
        model_name: Name of model to download
        
    Returns:
        True if successful, False otherwise
    """
```

#### **switch_model(model_name)**
Switch to different model.

```python
def switch_model(self, model_name: str) -> bool:
    """Switch to different model.
    
    Args:
        model_name: Name of model to switch to
        
    Returns:
        True if successful, False otherwise
    """
```

**Example:**
```python
# List available models
models = client.get_available_models()
print("Available models:", models)

# Download new model
success = client.download_model("speakleash/bielik-7b-instruct-v0.1")
if success:
    client.switch_model("bielik-7b-instruct")
```

### **Status and Configuration**

#### **get_status()**
Get client status information.

```python
def get_status(self) -> Dict[str, Any]:
    """Get client status and configuration.
    
    Returns:
        Status dictionary with model info, settings, etc.
    """
```

**Example:**
```python
status = client.get_status()
print(f"Current model: {status['current_model']}")
print(f"Models available: {status['models_available']}")
print(f"Memory usage: {status['memory_mb']}MB")
```

#### **is_model_available(model_name)**
Check if model is downloaded and available.

```python
def is_model_available(self, model_name: str) -> bool:
    """Check if model is downloaded and ready to use.
    
    Args:
        model_name: Name of model to check
        
    Returns:
        True if available, False otherwise
    """
```

### **Export and Utilities**

#### **export_conversation(format="markdown")**
Export conversation history.

```python
def export_conversation(self, 
                       format: str = "markdown",
                       filename: Optional[str] = None) -> str:
    """Export conversation history to file or string.
    
    Args:
        format: Export format ("markdown", "json", "txt")
        filename: Optional file to save to
        
    Returns:
        Exported content as string
    """
```

**Example:**
```python
# Export to string
markdown_content = client.export_conversation(format="markdown")

# Export to file
client.export_conversation(format="json", filename="conversation.json")
```

---

## ⚡ **Quick Functions**

For simple one-off operations without client setup:

### **quick_chat(message)**
```python
from bielik.client import quick_chat

response = quick_chat("Co to jest machine learning?")
print(response)
```

### **quick_query(question, model=None)**
```python
from bielik.client import quick_query

response = quick_query("Przetłumacz: Hello world", 
                      model="bielik-4.5b-v3.0-instruct")
print(response)
```

---

## 🎯 **Context Provider Integration**

Integrate Context Provider Commands with Python API:

```python
from bielik.client import BielikClient
from bielik.cli.command_api import CommandRegistry

client = BielikClient()
registry = CommandRegistry()

# Execute Context Provider Commands
folder_analysis = registry.execute_command("folder", ["folder:", "."], {})
calculation = registry.execute_command("calc", ["calc:", "2+3*4"], {})
document_data = registry.execute_command("pdf", ["pdf:", "report.pdf"], {})

# Send context to AI for analysis
response = client.chat(f"""
Analyze this project based on the following data:

Directory structure: {folder_analysis}
Calculations: {calculation}
Document content: {document_data}

What insights can you provide?
""")

print(response)
```

---

## 🌐 **Web Server API**

FastAPI web server for HTTP and WebSocket access.

### **Starting the Server**
```python
# Start server programmatically
from bielik.server import app
import uvicorn

uvicorn.run(app, host="0.0.0.0", port=8000)
```

```bash
# Start from command line
uvicorn bielik.server:app --port 8000 --reload
```

### **REST API Endpoints**

#### **POST /chat**
Send chat message and get response.

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "Cześć! Jak się masz?"}
  ],
  "model": "bielik-4.5b-v3.0-instruct",
  "stream": false
}
```

**Response:**
```json
{
  "response": "Cześć! Mam się dobrze, dziękuję za pytanie...",
  "model": "bielik-4.5b-v3.0-instruct",
  "tokens_used": 47,
  "response_time": 2.34
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Napisz krótki wiersz o Polsce"}
    ]
  }'
```

#### **GET /models**
List available models.

**Response:**
```json
{
  "models": [
    {
      "name": "bielik-4.5b-v3.0-instruct",
      "size": "4.5B parameters",
      "downloaded": true,
      "active": true
    },
    {
      "name": "bielik-7b-instruct",
      "size": "7B parameters", 
      "downloaded": false,
      "active": false
    }
  ]
}
```

#### **GET /health**
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model": "bielik-4.5b-v3.0-instruct",
  "version": "0.2.6",
  "uptime": 3600
}
```

### **WebSocket API**

#### **WS /ws**
Real-time chat via WebSocket.

**JavaScript Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function(event) {
    console.log('Connected to Bielik WebSocket');
    
    // Send message
    ws.send(JSON.stringify({
        "message": "Napisz krótki wiersz o Polsce",
        "model": "bielik-4.5b-v3.0-instruct"
    }));
};

ws.onmessage = function(event) {
    const response = JSON.parse(event.data);
    console.log('AI Response:', response.message);
    console.log('Model:', response.model);
};

ws.onerror = function(error) {
    console.error('WebSocket error:', error);
};
```

**Python WebSocket Client:**
```python
import asyncio
import websockets
import json

async def chat_websocket():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        # Send message
        message = {
            "message": "Co to jest sztuczna inteligencja?",
            "model": "bielik-4.5b-v3.0-instruct"
        }
        await websocket.send(json.dumps(message))
        
        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        print(f"AI: {data['message']}")

# Run WebSocket client
asyncio.run(chat_websocket())
```

---

## 📊 **Advanced Usage Examples**

### **Batch Processing**
```python
from bielik.client import BielikClient

client = BielikClient()

# Process multiple queries
questions = [
    "Co to jest AI?",
    "Jak działa machine learning?",
    "Jakie są zastosowania NLP?"
]

responses = []
for question in questions:
    response = client.query(question)
    responses.append({"question": question, "answer": response})

# Export results
import json
with open("batch_results.json", "w", encoding="utf-8") as f:
    json.dump(responses, f, ensure_ascii=False, indent=2)
```

### **Document Analysis Pipeline**
```python
from bielik.client import BielikClient
from bielik.cli.command_api import CommandRegistry

def analyze_documents(document_paths):
    """Analyze multiple documents with AI."""
    client = BielikClient()
    registry = CommandRegistry()
    
    results = []
    
    for doc_path in document_paths:
        # Extract document content
        doc_content = registry.execute_command("pdf", ["pdf:", doc_path], {})
        
        # AI analysis
        analysis = client.query(f"""
        Przeanalizuj ten dokument i podaj kluczowe informacje:
        
        {doc_content}
        
        Podaj:
        1. Główne tematy
        2. Kluczowe wnioski  
        3. Ważne dane liczbowe
        """)
        
        results.append({
            "document": doc_path,
            "content": doc_content,
            "analysis": analysis
        })
    
    return results

# Usage
documents = ["report1.pdf", "report2.pdf", "summary.docx"]
analysis_results = analyze_documents(documents)
```

### **Interactive Chat Bot**
```python
from bielik.client import BielikClient

class PolishChatBot:
    def __init__(self):
        self.client = BielikClient()
        self.client.start_conversation()
    
    def chat_loop(self):
        """Interactive chat loop."""
        print("🤖 Polski Asystent AI - napisz 'quit' aby zakończyć")
        
        while True:
            user_input = input("👤 Ty: ")
            
            if user_input.lower() in ['quit', 'exit', 'koniec']:
                break
                
            try:
                response = self.client.chat(user_input)
                print(f"🤖 AI: {response}")
            except Exception as e:
                print(f"❌ Błąd: {e}")
        
        # Export conversation
        self.client.export_conversation("markdown", "conversation.md")
        print("💾 Konwersacja zapisana do conversation.md")

# Run chat bot
bot = PolishChatBot()
bot.chat_loop()
```

---

## 🔧 **Error Handling**

### **Common Exceptions**
```python
from bielik.client import BielikClient, BielikError, ModelNotFoundError

client = BielikClient()

try:
    response = client.chat("Test message")
except ModelNotFoundError as e:
    print(f"Model not available: {e}")
    # Download model
    client.download_model("speakleash/bielik-4.5b-v3.0-instruct")
    response = client.chat("Test message")
    
except BielikError as e:
    print(f"Bielik error: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

### **Graceful Degradation**
```python
def safe_chat(client, message, fallback="Przepraszam, nie mogę odpowiedzieć."):
    """Chat with fallback handling."""
    try:
        return client.chat(message)
    except Exception as e:
        print(f"Warning: {e}")
        return fallback

# Usage
client = BielikClient()
response = safe_chat(client, "Test message")
```

---

## 🚀 **Performance Optimization**

### **Connection Pooling**
```python
# Reuse client instance
client = BielikClient()

# Multiple queries with same client (faster)
for question in questions:
    response = client.query(question)
    # Process response
```

### **Async Operations**
```python
import asyncio
from bielik.client import BielikAsyncClient

async def async_chat():
    client = BielikAsyncClient()
    
    # Concurrent queries
    tasks = [
        client.query("Pytanie 1"),
        client.query("Pytanie 2"),
        client.query("Pytanie 3")
    ]
    
    responses = await asyncio.gather(*tasks)
    return responses

# Run async operations
responses = asyncio.run(async_chat())
```

### **Memory Management**
```python
# Clear conversation history for long sessions
if len(client.get_conversation_history()) > 50:
    client.clear_history()

# Use query() instead of chat() for independent messages
response = client.query(message)  # No context maintained
```

---

## 📚 **API Reference Summary**

| Method | Description | Returns |
|--------|-------------|---------|
| `BielikClient()` | Create client instance | BielikClient |
| `.chat(message)` | Chat with context | str |
| `.query(question)` | Standalone query | str |
| `.get_available_models()` | List models | List[str] |
| `.download_model(name)` | Download model | bool |
| `.switch_model(name)` | Switch model | bool |
| `.get_status()` | Get status info | Dict |
| `.export_conversation()` | Export history | str |
| `quick_chat(message)` | Quick one-off chat | str |
| `quick_query(question)` | Quick query | str |

---

**Next Steps:** [Context Providers](CONTEXT_PROVIDERS.md) | [Docker Testing](DOCKER.md) | [Usage Guide](USAGE.md)
