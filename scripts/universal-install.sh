#!/bin/bash
# Universal Bielik Installer
# Works on any Linux/macOS system, installs conda if needed

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Check if conda is installed
check_conda() {
    if command -v conda &> /dev/null; then
        log_success "Conda found: $(conda --version)"
        return 0
    else
        log_warning "Conda not found, will install Miniconda"
        return 1
    fi
}

# Install Miniconda
install_miniconda() {
    local os=$(detect_os)
    local installer_url
    local installer_name
    
    log_info "Installing Miniconda for $os..."
    
    case $os in
        "linux")
            installer_url="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
            installer_name="Miniconda3-latest-Linux-x86_64.sh"
            ;;
        "macos")
            installer_url="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
            installer_name="Miniconda3-latest-MacOSX-x86_64.sh"
            ;;
        *)
            log_error "Unsupported operating system: $OSTYPE"
            exit 1
            ;;
    esac
    
    # Download installer
    log_info "Downloading Miniconda installer..."
    curl -L -o "$installer_name" "$installer_url"
    
    # Install silently
    log_info "Installing Miniconda..."
    bash "$installer_name" -b -p "$HOME/miniconda3"
    
    # Initialize conda
    log_info "Initializing conda..."
    "$HOME/miniconda3/bin/conda" init bash
    
    # Source the bashrc to make conda available
    if [ -f "$HOME/.bashrc" ]; then
        source "$HOME/.bashrc"
    fi
    
    # Add conda to PATH for this session
    export PATH="$HOME/miniconda3/bin:$PATH"
    
    # Clean up installer
    rm -f "$installer_name"
    
    log_success "Miniconda installed successfully!"
}

# Create or update Bielik conda environment
setup_bielik_environment() {
    log_info "Setting up Bielik conda environment..."
    
    # Check if bielik environment exists
    if conda env list | grep -q "^bielik "; then
        log_info "Bielik environment exists, updating..."
        conda env update -f environment.yml -n bielik
    else
        log_info "Creating new Bielik environment..."
        conda env create -f environment.yml
    fi
    
    log_success "Bielik environment ready!"
}

# Install Bielik package in development mode
install_bielik_package() {
    log_info "Installing Bielik package in development mode..."
    
    # Activate bielik environment and install package
    conda run -n bielik pip install -e .
    
    log_success "Bielik package installed!"
}

# Create conda-aware bielik wrapper script with CPU optimizations
create_bielik_wrapper() {
    log_info "Creating conda-aware bielik wrapper script with CPU optimizations..."
    
    # Create wrapper script that uses conda environment
    local wrapper_script="$HOME/.local/bin/bielik"
    
    # Ensure directory exists
    mkdir -p "$HOME/.local/bin"
    
    # Detect optimal CPU settings
    local cpu_cores=$(nproc 2>/dev/null || echo "4")
    local optimal_threads=$((cpu_cores > 8 ? cpu_cores / 2 : cpu_cores))
    
    # Create optimized wrapper script
    cat > "$wrapper_script" << EOF
#!/bin/bash
# Bielik wrapper script - automatically uses conda environment with CPU optimizations

# CPU optimization environment variables for faster LLM inference
export OMP_NUM_THREADS=$optimal_threads           # OpenMP threads
export MKL_NUM_THREADS=$optimal_threads           # Intel MKL threads
export NUMEXPR_NUM_THREADS=$optimal_threads       # NumExpr threads
export OPENBLAS_NUM_THREADS=$optimal_threads      # OpenBLAS threads
export VECLIB_MAXIMUM_THREADS=$optimal_threads    # Apple vecLib threads

# Intel MKL optimizations
export MKL_DYNAMIC=FALSE                          # Disable dynamic thread adjustment
export MKL_ENABLE_INSTRUCTIONS=AVX2               # Use AVX2 instructions if available

# ONNX Runtime optimizations  
export ORT_NUM_THREADS=$optimal_threads           # ONNX Runtime thread count
export ORT_INTRA_OP_NUM_THREADS=$optimal_threads  # Intra-op parallelism
export ORT_INTER_OP_NUM_THREADS=1                 # Inter-op parallelism

# Memory optimization
export MALLOC_TRIM_THRESHOLD_=100000              # Aggressive memory trimming
export MALLOC_MMAP_THRESHOLD_=100000              # Use mmap for large allocations

# Run Bielik with conda environment
exec conda run -n bielik python -m bielik.cli.main "\$@"
EOF
    
    # Make executable
    chmod +x "$wrapper_script"
    
    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        export PATH="$HOME/.local/bin:$PATH"
        log_info "Added $HOME/.local/bin to PATH in .bashrc"
    fi
    
    log_success "Optimized Bielik wrapper script created at $wrapper_script"
    log_info "CPU optimization: Using $optimal_threads threads for $cpu_cores CPU cores"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    # Run verification script in bielik environment
    conda run -n bielik python scripts/verify_installation.py
    
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        log_success "Installation verification passed!"
        return 0
    else
        log_warning "Installation verification found issues"
        return 1
    fi
}

# Main installation function
main() {
    log_info "🦅 Starting Bielik Universal Installation"
    echo "========================================"
    
    # Step 1: Check/Install Conda
    if ! check_conda; then
        install_miniconda
        
        # Reload conda after installation
        if [ -f "$HOME/.bashrc" ]; then
            source "$HOME/.bashrc"
        fi
        export PATH="$HOME/miniconda3/bin:$PATH"
        
        # Verify conda is now available
        if ! command -v conda &> /dev/null; then
            log_error "Conda installation failed or not in PATH"
            log_info "Please restart your terminal and run this script again"
            exit 1
        fi
    fi
    
    # Step 2: Setup Bielik environment
    setup_bielik_environment
    
    # Step 3: Install Bielik package
    install_bielik_package
    
    # Step 4: Create conda wrapper script
    create_bielik_wrapper
    
    # Step 5: Verify installation
    if verify_installation; then
        echo ""
        log_success "🎉 Installation completed successfully! 🚀"
        echo ""
        log_info "To use Bielik:"
        echo "1. Activate the environment: conda activate bielik"
        echo "2. Run Bielik: bielik"
        echo ""
        log_info "Or run directly: conda run -n bielik bielik"
    else
        echo ""
        log_warning "Installation completed but with some issues"
        log_info "Run 'conda activate bielik && python scripts/verify_installation.py' to check"
    fi
}

# Handle help
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    echo "Bielik Universal Installer"
    echo "========================="
    echo ""
    echo "This script automatically:"
    echo "• Installs Miniconda if conda is not found"
    echo "• Creates/updates the 'bielik' conda environment"
    echo "• Installs all required dependencies"
    echo "• Verifies the installation"
    echo ""
    echo "Usage: $0"
    echo "       $0 --help"
    exit 0
fi

# Run installation
main "$@"
