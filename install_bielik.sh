#!/bin/bash
# Bielik Installation Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
ENV_NAME="bielik-env"
PYTHON_VERSION="3.11"

# Function to print section headers
section() {
    echo -e "\n${GREEN}=== $1 ===${NC}"
}

# Function to print info messages
info() {
    echo -e "${YELLOW}$1${NC}"
}

# Function to print error messages
error() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

# Check if Conda is installed
check_conda() {
    if ! command -v conda &> /dev/null; then
        error "Conda is not installed. Please install Miniconda first."
    fi
    info "Found Conda: $(conda --version)"
}

# Create Conda environment
create_environment() {
    section "Creating Conda environment"
    
    # Remove existing environment if it exists
    if conda env list | grep -q "^$ENV_NAME\s"; then
        info "Removing existing environment '$ENV_NAME'..."
        conda env remove -n $ENV_NAME -y
    fi
    
    info "Creating new environment '$ENV_NAME' with Python $PYTHON_VERSION"
    conda create -n $ENV_NAME python=$PYTHON_VERSION -y
}

# Install dependencies
install_dependencies() {
    section "Installing dependencies"
    
    # Activate the environment
    eval "$(conda shell.bash hook)"
    conda activate $ENV_NAME || error "Failed to activate environment"
    
    # Verify we're using the correct Python
    PYTHON_PATH=$(which python)
    if [[ ! "$PYTHON_PATH" == *"$ENV_NAME"* ]]; then
        error "Not using the correct Python environment. Please run this script in a new terminal."
    fi
    info "Using Python from: $PYTHON_PATH"
    
    # Install system dependencies
    info "Installing system dependencies..."
    conda install -y -c conda-forge \
        cmake \
        make \
        gcc_linux-64 \
        gxx_linux-64 \
        libgcc \
        libstdcxx-ng
    
    # Install PyTorch with CPU support
    info "Installing PyTorch..."
    conda install -y -c pytorch \
        pytorch \
        torchvision \
        torchaudio \
        cpuonly
    
    # Install Hugging Face libraries
    info "Installing Hugging Face libraries..."
    pip install --upgrade \
        transformers \
        accelerate \
        sentencepiece \
        huggingface-hub \
        bitsandbytes
    
    # Install llama-cpp-python
    info "Installing llama-cpp-python..."
    CMAKE_ARGS="-DLLAMA_NO_METAL=on" FORCE_CMAKE=1 \
    pip install llama-cpp-python --no-cache-dir
    
    # Install Bielik in development mode
    info "Installing Bielik..."
    if [ -f "setup.py" ]; then
        pip install -e ".[local]"
    else
        error "Could not find setup.py. Please run this script from the Bielik root directory."
    fi
}

# Verify installation
verify_installation() {
    section "Verifying Installation"
    
    # Check if we can import all required packages
    if python -c "
import sys
try:
    import torch
    import transformers
    from llama_cpp import Llama
    import bielik
    print('✅ All dependencies are properly installed')
    sys.exit(0)
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"; then
        info "Verification successful!"
    else
        error "Verification failed. Some dependencies are not properly installed."
    fi
}

# Main function
main() {
    echo -e "${GREEN}🦅 Bielik Installation${NC}"
    echo -e "${GREEN}======================${NC}\n"
    
    check_conda
    create_environment
    
    echo -e "\n${YELLOW}Please run the following commands to complete the installation:${NC}"
    echo -e "1. Activate the environment:"
    echo -e "   ${GREEN}conda activate $ENV_NAME${NC}"
    echo -e "2. Run the installation script again:"
    echo -e "   ${GREEN}./install_bielik.sh --install${NC}"
    
    # If --install flag is provided, install dependencies
    if [ "$1" == "--install" ]; then
        install_dependencies
        verify_installation
        
        echo -e "\n${GREEN}✨ Installation completed successfully!${NC}"
        echo -e "\nTo get started, activate the environment and run Bielik:"
        echo -e "  conda activate $ENV_NAME"
        echo -e "  bielik"
    fi
}

# Run main function
main "$@"
