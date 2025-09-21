#!/bin/bash
# Bielik CLI Installation Script for Unix/Linux/macOS
# Universal installer with automatic dependency detection

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="$(basename "$SCRIPT_DIR")"

log_info "🚀 Bielik CLI Universal Installer for Unix/Linux/macOS"
log_info "Project directory: $SCRIPT_DIR"

# Check if Python 3 is available
check_python() {
    log_info "Checking Python installation..."
    
    for python_cmd in python3 python; do
        if command -v "$python_cmd" >/dev/null 2>&1; then
            PYTHON_VERSION=$("$python_cmd" --version 2>&1 | cut -d' ' -f2)
            PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
            PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
            
            if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
                PYTHON_CMD="$python_cmd"
                log_success "Found Python $PYTHON_VERSION at $(which "$python_cmd")"
                return 0
            else
                log_warning "Python $PYTHON_VERSION is too old (need 3.8+)"
            fi
        fi
    done
    
    log_error "Python 3.8+ not found. Please install Python 3.8 or newer."
    echo ""
    echo "Installation instructions:"
    echo "• Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "• CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "• macOS: brew install python3"
    echo "• Or download from: https://www.python.org/downloads/"
    exit 1
}

# Check if we can use the Python installer
check_python_installer() {
    if [ -f "$SCRIPT_DIR/install.py" ]; then
        log_info "Found Python installer, delegating to install.py..."
        
        # Parse command line arguments
        ARGS=""
        for arg in "$@"; do
            case $arg in
                --conda)
                    ARGS="$ARGS --conda"
                    ;;
                --skip-ai)
                    ARGS="$ARGS --skip-ai"
                    ;;
                --dev)
                    ARGS="$ARGS --dev"
                    ;;
                --help|-h)
                    echo "Bielik CLI Installation Script"
                    echo ""
                    echo "Usage: $0 [OPTIONS]"
                    echo ""
                    echo "Options:"
                    echo "  --conda      Use conda/mamba instead of pip"
                    echo "  --skip-ai    Skip llama-cpp-python installation"
                    echo "  --dev        Development installation"
                    echo "  --help, -h   Show this help message"
                    exit 0
                    ;;
            esac
        done
        
        # Run Python installer
        "$PYTHON_CMD" "$SCRIPT_DIR/install.py" $ARGS
        return $?
    else
        log_warning "install.py not found, using shell-based installation"
        return 1
    fi
}

# Fallback shell installation
install_with_shell() {
    log_info "Performing shell-based installation..."
    
    # Create virtual environment
    VENV_DIR="$SCRIPT_DIR/.venv"
    
    if [ -d "$VENV_DIR" ]; then
        log_info "Virtual environment already exists"
    else
        log_info "Creating virtual environment..."
        "$PYTHON_CMD" -m venv "$VENV_DIR"
        log_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    log_info "Upgrading pip..."
    python -m pip install --upgrade pip
    
    # Install basic dependencies
    log_info "Installing basic dependencies..."
    
    pip install "fastapi>=0.88.0,<1.0.0" \
                "uvicorn[standard]>=0.20.0,<1.0.0" \
                "requests>=2.25.0,<3.0.0" \
                "python-dotenv>=0.19.0,<2.0.0" \
                "beautifulsoup4>=4.9.0,<5.0.0" \
                "html2text>=2020.1.16,<2025.0.0" \
                "python-magic>=0.4.24,<1.0.0" \
                "pypdf>=3.0.0,<4.0.0" \
                "python-docx>=0.8.11,<1.0.0" \
                "huggingface_hub>=0.16.0,<1.0.0"
    
    log_success "Basic dependencies installed"
    
    # Try to install llama-cpp-python (optional)
    if [[ "$*" != *"--skip-ai"* ]]; then
        log_info "Attempting to install llama-cpp-python..."
        
        # Try multiple strategies
        if pip install llama-cpp-python --no-cache-dir; then
            log_success "llama-cpp-python installed successfully"
        elif command -v conda >/dev/null 2>&1; then
            log_info "Trying conda installation..."
            if conda install -c conda-forge llama-cpp-python -y; then
                log_success "llama-cpp-python installed via conda"
            else
                log_warning "Failed to install llama-cpp-python, continuing without AI support"
            fi
        else
            log_warning "Failed to install llama-cpp-python, continuing without AI support"
        fi
    else
        log_info "Skipping AI model support (--skip-ai)"
    fi
    
    # Install Bielik in development mode
    log_info "Installing Bielik CLI..."
    pip install -e .
    log_success "Bielik CLI installed"
    
    # Deactivate virtual environment
    deactivate
}

# Create launcher script
create_launcher() {
    LAUNCHER="$SCRIPT_DIR/run.sh"
    
    cat > "$LAUNCHER" << 'EOF'
#!/bin/bash
# Bielik CLI Launcher

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment not found. Please run install.sh first."
    exit 1
fi

"$VENV_PYTHON" -m bielik.cli.main "$@"
EOF

    chmod +x "$LAUNCHER"
    log_success "Created launcher script: run.sh"
}

# Show installation summary
show_summary() {
    echo ""
    echo "================================================================"
    log_success "🎉 BIELIK CLI INSTALLATION COMPLETED!"
    echo "================================================================"
    
    log_success "✅ System: $(uname -s) $(uname -r)"
    log_success "✅ Python: $PYTHON_VERSION"
    log_success "✅ Project: $SCRIPT_DIR"
    log_success "✅ Virtual Environment: $SCRIPT_DIR/.venv"
    log_success "✅ Bielik CLI with Context Provider Commands"
    
    echo ""
    log_info "📋 NEXT STEPS:"
    echo "   • Launch: ./run.sh"
    echo "   • Or: python run.py"
    echo "   • Or: .venv/bin/python -m bielik.cli.main"
    echo ""
    log_info "🚀 TEST CONTEXT PROVIDER COMMANDS:"
    echo "   • Try: folder: ."
    echo "   • Help: :help"
    echo "   • Calculator: :calc 2+3"
    echo ""
    echo "🔗 For more info: https://github.com/tom-sapletta-com/bielik"
}

# Main installation flow
main() {
    check_python
    
    # Try Python installer first, fallback to shell
    if ! check_python_installer "$@"; then
        install_with_shell "$@"
        create_launcher
        show_summary
    fi
}

# Run main function with all arguments
main "$@"
