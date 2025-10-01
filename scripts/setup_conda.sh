#!/bin/bash
# Bielik Conda Setup Script
# This script sets up a Conda environment for Bielik with all required dependencies

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
ENV_NAME="bielik"
PYTHON_VERSION="3.11"
MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"

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
        info "Conda not found. Installing Miniconda..."
        wget $MINICONDA_URL -O miniconda.sh
        bash miniconda.sh -b -p $HOME/miniconda
        rm miniconda.sh
        
        # Initialize conda for the current shell
        eval "$($HOME/miniconda/bin/conda shell.$(basename $SHELL) hook)"
        conda init
        
        info "Please restart your shell and run this script again."
        exit 0
    fi
    
    info "Found Conda: $(conda --version)"
}

# Create Conda environment
create_environment() {
    section "Setting up Conda environment"
    
    if conda env list | grep -q "^$ENV_NAME\s"; then
        info "Environment '$ENV_NAME' already exists. Updating..."
        conda env update -f environment.yml --prune
    else
        info "Creating new environment '$ENV_NAME' with Python $PYTHON_VERSION"
        conda env create -f environment.yml
    fi
    
    # Activate the environment
    conda activate $ENV_NAME || error "Failed to activate environment"
}

# Install Bielik in development mode
install_bielik() {
    section "Installing Bielik"
    
    # Check if we're in the Bielik directory
    if [ ! -f "pyproject.toml" ]; then
        error "Please run this script from the Bielik project root directory"
    fi
    
    # Install in development mode with all extras
    pip install -e ".[local,dev,test]" || error "Failed to install Bielik"
    
    info "Bielik installed in development mode"
}

# Verify installation
verify_installation() {
    section "Verifying Installation"
    
    if python -c "import bielik" &> /dev/null; then
        info "✅ Bielik is properly installed"
    else
        error "Bielik installation verification failed"
    fi
    
    if command -v bielik &> /dev/null; then
        info "✅ Bielik CLI is available"
    else
        error "Bielik CLI is not in PATH"
    fi
}

# Main function
main() {
    echo -e "${GREEN}🦅 Bielik Conda Setup${NC}"
    echo -e "${GREEN}====================${NC}\n"
    
    check_conda
    create_environment
    install_bielik
    verify_installation
    
    echo -e "\n${GREEN}✨ Setup completed successfully!${NC}"
    echo -e "\nTo get started, activate the environment and run Bielik:"
    echo -e "  conda activate $ENV_NAME"
    echo -e "  bielik"
    echo -e "\nFor development, install pre-commit hooks:"
    echo -e "  pre-commit install"
}

# Run main function
main
