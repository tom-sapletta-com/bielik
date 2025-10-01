# 🛠️ Installation Guide

Complete installation guide for Bielik Polish AI Assistant CLI.

## 📋 **Navigation Menu**
- [🏠 Documentation Home](README.md)
- [⚡ Quick Start](USAGE.md#quick-start)
- [🏗️ Architecture](ARCHITECTURE.md)
- [🤝 Contributing](CONTRIBUTING.md)

---

## 🚀 **Recommended Installation (Conda)**

### Prerequisites
- Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/download/)
- For GPU support: Install appropriate NVIDIA drivers and CUDA toolkit

### 📦 **One-Command Installation**

```bash
# Clone repository and run universal installer
git clone https://github.com/tom-sapletta-com/bielik.git
cd bielik
make install
```

The `make install` command will:
- ✅ Create optimized conda environment with CPU acceleration
- ✅ Install all dependencies including llama-cpp-python
- ✅ Set up Bielik package in development mode
- ✅ Create optimized wrapper script at `~/.local/bin/bielik`
- ✅ Verify installation with comprehensive checks

### 🖥️ **Manual Conda Setup**

If you prefer manual setup:

```bash
# 1. Create conda environment from configuration
conda env create -f environment.yml
conda activate bielik

# 2. Install Bielik in development mode
pip install -e .

# 3. Verify installation
python scripts/verify_installation.py
```

---

## ⚡ **Alternative Installation Methods**

### 📦 **PyPI Installation**

#### 🪶 **Minimal Version** (Text-only, ~50MB)

```bash
# Install minimal version
pip install bielik

# Manual llama-cpp-python installation (required for local models)
conda install -c conda-forge llama-cpp-python

# Start CLI and download your first model
python -m bielik
```

**What's included:**
- ✅ Polish conversation and text analysis
- ✅ HuggingFace model downloads and management  
- ✅ Document processing (PDF, DOCX, TXT)
- ✅ Context Provider Commands (folder:, calc:, pdf:)
- ✅ Personalized CLI experience
- ❌ Local AI models (requires manual llama-cpp-python installation)

#### 🎯 **Full Version** (With vision, ~2GB)

```bash
# Install full version (text + vision)
pip install bielik[vision]

# Manual llama-cpp-python installation
conda install -c conda-forge llama-cpp-python

# Start CLI with image analysis support
python -m bielik
```

**Additional features:**
- ✅ **Everything from minimal version**
- ✅ **Image analysis and captioning**
- ✅ **Visual question answering**
- ✅ **GPU acceleration support**

### 🔄 **Upgrade Options**

```bash
# Upgrade minimal → full
pip install bielik[vision]

# Or install specific optional features
pip install bielik[local]    # Local model execution
pip install bielik[gpu]      # GPU acceleration
pip install bielik[dev]      # Development tools
pip install bielik[vision]   # Vision capabilities
```

---

## 🖥️ **Platform-Specific Setup**

### 🪟 **Windows**
```batch
REM Use Anaconda Prompt with Administrator privileges
REM Install Visual Studio Build Tools with C++ workload

REM Quick install
install.bat

REM Or manual
git clone https://github.com/tom-sapletta-com/bielik.git
cd bielik
python install.py
```

### 🐧 **Linux**
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update && sudo apt-get install -y \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    python-openssl \
    git

# Quick install
./install.sh

# Or use universal installer
git clone https://github.com/tom-sapletta-com/bielik.git
cd bielik
python install.py
```

### 🍎 **macOS (Intel/Apple Silicon)**
```bash
# For Apple Silicon with Metal acceleration:
conda install -c conda-forge llama-cpp-python

# Or use pip with Metal flags (if conda not available):
CMAKE_ARGS="-DLLAMA_METAL=on" FORCE_CMAKE=1 \
pip install llama-cpp-python --no-cache-dir

# Quick install
./install.sh
```

---

## ⚙️ **Installation Options**

### 🎯 **Universal Installer Options**
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

### 🚀 **What the Universal Installer Does:**
- ✅ **Auto-detects** your operating system and Python version
- ✅ **Creates** isolated virtual environment 
- ✅ **Installs** all dependencies with smart fallback strategies
- ✅ **Attempts** multiple llama-cpp-python installation methods
- ✅ **Creates** platform-specific launcher scripts
- ✅ **Works** even if AI models fail to install (Context Provider Commands still work)
- ✅ **Provides** clear next steps and troubleshooting

---

## 🚀 **After Installation**

### 📱 **Launch Options**
```bash
# Universal launcher (any platform)
python run.py

# Platform-specific launchers
./run.sh        # Linux/macOS
run.bat         # Windows

# Direct activation
.venv/bin/python -m bielik.cli.main     # Linux/macOS
.venv\Scripts\python -m bielik.cli.main # Windows

# If installed with conda/make
bielik          # Direct command (added to PATH)
```

### ✅ **Verify Installation**
```bash
# Run verification script
python scripts/verify_installation.py

# Quick test
bielik --help

# Test Context Provider Commands (work without AI models)
bielik -p "calc: 2 + 3 * 4"
bielik -p "folder: ."
```

---

## ⚙️ **Environment Variables**

### **Core Settings:**
* `BIELIK_CLI_USERNAME` — Your display name in CLI (auto-detected from system)
* `BIELIK_CLI_CURRENT_MODEL` — Currently selected model
* `BIELIK_CLI_ASSISTANT_NAME` — Assistant display name (auto-set from model)
* `BIELIK_CLI_AUTO_SWITCH` — Auto-switch to newly downloaded models (default: true)

### **Storage & Cache:**
* `BIELIK_MODELS_DIR` — Local model storage directory
* `BIELIK_DATA_DIR` — User data and settings directory
* `HF_HOME` — HuggingFace cache directory

### **Performance Optimization:**
* `BIELIK_DEBUG` — Enable debug mode (default: false)
* `BIELIK_LOAD_TIMEOUT` — Model loading timeout in seconds (default: 10)

### **Docker Environment:**
* `BIELIK_MODE` — `minimal` or `full` (Docker only)
* `BIELIK_IMAGES_DIR` — Images directory for analysis (full version)

---

## 🛠️ **Troubleshooting**

### **Common Issues**

#### 1. **Conda Environment Issues**

**Problem**: Conda command not found  
**Solution**:
```bash
# Add Conda to PATH
export PATH="$HOME/miniconda3/bin:$PATH"
# Initialize Conda for your shell
eval "$(conda shell.bash hook)"
```

#### 2. **llama-cpp-python Installation Issues**

**Problem**: C++ compilation errors  
**Solution**: Use conda instead of pip
```bash
# Recommended approach (avoids compilation)
conda install -c conda-forge llama-cpp-python

# Alternative with specific flags
CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" \
pip install llama-cpp-python --no-cache-dir
```

#### 3. **CUDA/GPU Support**

**Problem**: CUDA not detected  
**Solution**: Install CUDA toolkit and configure Conda:
```bash
conda install -c nvidia cuda-toolkit
conda install -c conda-forge cudatoolkit-dev
```

#### 4. **Slow Model Loading**

**Problem**: First load is slow  
**Solution**: This is normal for the first load. Subsequent loads will be faster thanks to lazy loading.

**Enable debug mode:**
```bash
BIELIK_DEBUG=1 bielik
```

#### 5. **Model Download Issues**

**Problem**: Model download fails or times out  
**Solutions**:
```bash
# Check HuggingFace connectivity
python -c "from huggingface_hub import HfApi; print('HF connection OK')"

# Check available disk space (models are 2-8GB)
df -h

# Manual download with timeout
python -m bielik
:download speakleash/bielik-4.5b-v3.0-instruct
```

#### 6. **Missing Dependencies**

**Problem**: Missing system libraries  
**Solution**: Install required system packages:
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libjpeg-dev

# CentOS/RHEL
sudo yum groupinstall -y "Development Tools"
sudo yum install -y cmake openblas-devel lapack-devel libjpeg-turbo-devel
```

### **Performance Issues**

**Problem**: Model responses are slow or use too much memory
```bash
# Use smaller model
:switch speakleash/bielik-4.5b-v3.0-instruct  # instead of 7b

# Check system resources
htop      # Linux/macOS
taskmgr   # Windows

# Enable GPU acceleration (full version)
pip install bielik[gpu]
```

**Problem**: Image analysis not working
```bash
# Check if vision packages installed
python -c "from bielik.image_analyzer import ImageAnalyzer; ia = ImageAnalyzer(); print(f'Available: {ia.is_available()}')"

# Install vision support
pip install bielik[vision]
```

---

## 🚀 **Performance Tips**

1. **First Run**: The first run will be slower as models are loaded and cached
2. **Subsequent Runs**: Enjoy faster startup times thanks to lazy loading
3. **Memory Usage**: Close other memory-intensive applications when running Bielik
4. **GPU Acceleration**: For best performance, use a system with CUDA-compatible GPU
5. **CPU Optimization**: Conda installation includes optimized CPU libraries (MKL, OpenBLAS)

### **Optimizing Model Loading**

```bash
# Start Bielik with debug mode (shows detailed loading information)
BIELIK_DEBUG=1 bielik

# Set a custom timeout (in seconds)
BIELIK_LOAD_TIMEOUT=15 bielik
```

If a model takes longer than the timeout to load, the debugger will automatically activate and show detailed logs to help diagnose the issue.

---

## 🆘 **Getting Help**

If you encounter any issues, please:

1. **Check the [GitHub Issues](https://github.com/tom-sapletta-com/bielik/issues)** for known problems
2. **Run the verification script** and include its output when reporting issues:
   ```bash
   python scripts/verify_installation.py
   ```
3. **Provide details** about your system and the exact error message
4. **Use the `:help` command** in CLI for built-in assistance
5. **Check Docker** for isolated testing environment

### **Test Environment**
Use Docker for isolated testing if you encounter persistent issues:
```bash
git clone https://github.com/tom-sapletta-com/bielik.git
cd bielik
make docker-test-ubuntu  # Test on clean Ubuntu environment
```

---

**Next Steps:** [Usage Guide](USAGE.md) | [Architecture](ARCHITECTURE.md) | [Contributing](CONTRIBUTING.md)
