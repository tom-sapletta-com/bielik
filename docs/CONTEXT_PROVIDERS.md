# 🎯 Context Provider Commands

Guide for creating and using Context Provider Commands in Bielik CLI.

## 📋 **Navigation Menu**
- [🏠 Documentation Home](README.md)
- [📥 Installation](INSTALLATION.md)
- [🏗️ Architecture](ARCHITECTURE.md)
- [⚡ Usage Guide](USAGE.md)
- [🤝 Contributing](CONTRIBUTING.md)

---

## 🌟 **What are Context Provider Commands?**

Context Provider Commands are extensible `name:` commands that generate structured data for AI analysis. They work **independently** of AI models, providing instant results for data processing and analysis.

### **Key Features**
- **⚡ Instant execution** - No AI model loading required
- **🔧 Standardized format** - All commands use `name:` syntax
- **📊 Structured output** - Generate organized data for AI consumption
- **🔌 Extensible** - Easy to create custom commands
- **🏗️ Project integration** - Automatically save to active projects

---

## 📋 **Available Commands**

| Command | Format | Description | Example |
|---------|--------|-------------|---------|
| **📁 folder:** | `folder: <path>` | Directory analysis | `folder: ~/Documents` |
| **🧮 calc:** | `calc: <expression>` | Mathematical calculations | `calc: 2 + 3 * 4` |
| **📄 pdf:** | `pdf: <file>` | Document processing | `pdf: report.pdf` |

---

## 🚀 **Using Context Provider Commands**

### **Command Line Usage**
```bash
# Instant calculations
bielik -p "calc: 2^8 + sqrt(49)"

# Directory analysis  
bielik -p "folder: . --recursive"

# Document processing
bielik -p "pdf: document.pdf --pages=1-5"
```

### **Interactive Usage**
```bash
bielik

# Use commands to load context
👤 You: folder: ~/projects
✅ Context loaded! Directory analysis complete.

# Ask AI about the loaded context
👤 You: What are the largest Python files?
🤖 AI: [Uses folder context to answer]
```

---

## 🛠️ **Creating Custom Commands**

### **Quick Setup**
```bash
# 1. Create command directory
mkdir -p commands/mycommand
cd commands/mycommand

# 2. Create implementation file
touch main.py

# 3. Create configuration
touch config.json
```

### **Implementation Template**
```python
# commands/mycommand/main.py
from bielik.cli.command_api import ContextProviderCommand

class MyCommand(ContextProviderCommand):
    """Custom context provider for specialized analysis."""
    
    name = "mycommand"
    description = "Analyze custom data sources"
    is_context_provider = True
    
    def provide_context(self, args, context):
        """Generate context from command arguments.
        
        Args:
            args: List of command arguments ['mycommand:', 'input']
            context: CLI context dictionary
            
        Returns:
            Dict with structured context data
        """
        if len(args) < 2:
            return {"error": "Usage: mycommand: <input>"}
        
        user_input = args[1]
        
        # Your custom processing logic here
        processed_data = self.process_input(user_input)
        
        return {
            "type": "custom_analysis",
            "input": user_input,
            "result": processed_data,
            "metadata": {
                "command": "mycommand",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
    
    def process_input(self, input_data):
        """Custom processing logic."""
        # Implement your analysis here
        return {"processed": input_data}
```

### **Configuration File**
```json
{
  "name": "mycommand",
  "description": "Custom context provider for specialized analysis",
  "version": "1.0.0",
  "author": "Your Name",
  "category": "analysis",
  "usage_examples": [
    {
      "command": "mycommand: sample input",
      "description": "Analyzes the provided input"
    }
  ],
  "requirements": ["python>=3.8"],
  "tags": ["analysis", "custom"]
}
```

---

## 🔧 **Advanced Examples**

### **Git Repository Analyzer**
```python
# commands/git/main.py
import subprocess
import json
from pathlib import Path
from bielik.cli.command_api import ContextProviderCommand

class GitCommand(ContextProviderCommand):
    name = "git"
    description = "Analyze Git repository information"
    is_context_provider = True
    
    def provide_context(self, args, context):
        if len(args) < 2:
            return {"error": "Usage: git: <repository_path>"}
        
        repo_path = Path(args[1]).expanduser().resolve()
        
        if not (repo_path / '.git').exists():
            return {"error": f"No git repository found at {repo_path}"}
        
        try:
            # Get repository information
            repo_info = {
                "path": str(repo_path),
                "commits": self.get_commit_info(repo_path),
                "branches": self.get_branches(repo_path),
                "status": self.get_status(repo_path),
                "files": self.get_file_stats(repo_path)
            }
            
            return {
                "type": "git_analysis",
                "repository": repo_info,
                "summary": f"Repository at {repo_path} with {len(repo_info['commits'])} recent commits"
            }
            
        except Exception as e:
            return {"error": f"Git analysis failed: {str(e)}"}
    
    def get_commit_info(self, repo_path):
        """Get recent commit information."""
        result = subprocess.run([
            'git', 'log', '--oneline', '-10'
        ], cwd=repo_path, capture_output=True, text=True)
        
        if result.returncode == 0:
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    hash_msg = line.split(' ', 1)
                    commits.append({
                        "hash": hash_msg[0],
                        "message": hash_msg[1] if len(hash_msg) > 1 else ""
                    })
            return commits
        return []
```

### **System Monitor Command**
```python
# commands/system/main.py
import psutil
import platform
from datetime import datetime
from bielik.cli.command_api import ContextProviderCommand

class SystemCommand(ContextProviderCommand):
    name = "system"
    description = "System resource monitoring and analysis"
    is_context_provider = True
    
    def provide_context(self, args, context):
        try:
            system_info = {
                "platform": {
                    "system": platform.system(),
                    "version": platform.version(),
                    "architecture": platform.architecture()[0]
                },
                "cpu": {
                    "count": psutil.cpu_count(),
                    "usage_percent": psutil.cpu_percent(interval=1),
                    "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                "memory": {
                    "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                    "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                    "usage_percent": psutil.virtual_memory().percent
                },
                "disk": self.get_disk_info(),
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "type": "system_monitoring",
                "system": system_info,
                "summary": f"System: {system_info['platform']['system']}, "
                          f"CPU: {system_info['cpu']['usage_percent']}%, "
                          f"RAM: {system_info['memory']['usage_percent']}%"
            }
            
        except Exception as e:
            return {"error": f"System monitoring failed: {str(e)}"}
    
    def get_disk_info(self):
        """Get disk usage information."""
        disk_info = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info[partition.device] = {
                    "mountpoint": partition.mountpoint,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "usage_percent": round((usage.used / usage.total) * 100, 1)
                }
            except PermissionError:
                continue
        return disk_info
```

---

## 📊 **Best Practices**

### **1. Structure Output Consistently**
```python
def provide_context(self, args, context):
    return {
        "type": "command_type",           # Always include type
        "input": user_input,              # Echo input for reference
        "result": processed_data,         # Main result data
        "metadata": {                     # Additional context
            "command": self.name,
            "timestamp": current_time,
            "version": "1.0.0"
        },
        "summary": "Brief description"    # Human-readable summary
    }
```

### **2. Handle Errors Gracefully**
```python
def provide_context(self, args, context):
    try:
        # Main processing logic
        result = self.process_data(args)
        return {"type": "success", "result": result}
    except FileNotFoundError as e:
        return {"error": f"File not found: {e}"}
    except PermissionError as e:
        return {"error": f"Permission denied: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}
```

### **3. Validate Input Arguments**
```python
def provide_context(self, args, context):
    if len(args) < 2:
        return {
            "error": f"Usage: {self.name}: <required_argument>",
            "help": self.description
        }
    
    argument = args[1]
    if not self.validate_argument(argument):
        return {"error": f"Invalid argument: {argument}"}
    
    # Continue with processing
```

---

## 🧪 **Testing Context Providers**

### **Unit Testing**
```python
# tests/test_context_providers.py
import pytest
from bielik.cli.command_api import CommandRegistry

class TestMyCommand:
    def setup_method(self):
        self.registry = CommandRegistry()
    
    def test_command_registration(self):
        """Test that custom command is registered."""
        commands = self.registry.list_commands()
        assert "mycommand" in commands
    
    def test_command_execution(self):
        """Test command execution with valid input."""
        result = self.registry.execute_command(
            "mycommand", 
            ["mycommand:", "test-input"], 
            {}
        )
        assert result is not None
        assert result["type"] == "custom_analysis"
        assert result["input"] == "test-input"
    
    def test_error_handling(self):
        """Test error handling with invalid input."""
        result = self.registry.execute_command(
            "mycommand",
            ["mycommand:"],  # Missing argument
            {}
        )
        assert "error" in result
```

### **Integration Testing**
```bash
# Test command via CLI
bielik -p "mycommand: test-input"

# Test with project integration
bielik
:project create "Test Project"
mycommand: test-input
:project open  # Verify artifact was saved
```

---

## 🔌 **Integration Patterns**

### **With Python API**
```python
from bielik.client import BielikClient
from bielik.cli.command_api import CommandRegistry

client = BielikClient()
registry = CommandRegistry()

# Execute Context Provider Command
context_data = registry.execute_command("mycommand", ["mycommand:", "input"], {})

# Send to AI for analysis
response = client.chat(f"Analyze this data: {context_data}")
```

### **With Project System**
Commands automatically integrate with the project system when used in interactive mode:

```bash
bielik
:project create "Analysis Project"
mycommand: data-to-analyze  # Automatically saved to project
folder: .                   # Additional context
:project open              # View all collected artifacts
```

---

## 📚 **Command Development Resources**

### **Available Base Classes**
- `ContextProviderCommand` - Base class for all context providers
- `FileCommand` - Specialized for file processing
- `NetworkCommand` - For network-based operations
- `DataCommand` - For data analysis operations

### **Utility Functions**
```python
from bielik.cli.command_api import CommandUtils

# File validation
CommandUtils.validate_file_path(path)

# JSON formatting
CommandUtils.format_json_output(data)

# Size formatting
CommandUtils.format_file_size(bytes)

# Time formatting
CommandUtils.format_timestamp(datetime_obj)
```

### **Context Dictionary Structure**
```python
context = {
    "current_model": "bielik-4.5b-v3.0-instruct",
    "messages": [],  # Current conversation history
    "cli_settings": {
        "username": "User",
        "assistant_name": "Bielik-4.5B"
    },
    "project_id": "abc123...",  # If project is active
    "working_directory": "/path/to/current/dir"
}
```

---

## 🚀 **Publishing Custom Commands**

### **1. Package Structure**
```
my-bielik-commands/
├── commands/
│   ├── mycommand/
│   │   ├── main.py
│   │   └── config.json
│   └── anothercmd/
│       ├── main.py
│       └── config.json
├── tests/
├── README.md
└── setup.py
```

### **2. Installation**
```bash
# Install custom command package
pip install my-bielik-commands

# Commands automatically available in Bielik CLI
bielik -p "mycommand: test"
```

---

**Next Steps:** [Docker Testing](DOCKER.md) | [API Documentation](API.md) | [Usage Guide](USAGE.md)
