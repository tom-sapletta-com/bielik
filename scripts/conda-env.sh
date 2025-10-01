#!/bin/bash
# Conda environment management for Bielik

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

# Create Conda environment
create_env() {
    log_info "Setting up Conda environment..."
    conda env create -f environment.yml
    log_success "Conda environment created. Run 'conda activate bielik'"
}

# Install development dependencies
setup_dev() {
    log_info "Installing development dependencies..."
    conda install -c conda-forge -y \
        pytest \
        pytest-cov \
        black \
        flake8 \
        isort \
        mypy \
        build \
        twine
    log_success "Development environment ready!"
}

# Remove Conda environment
clean_env() {
    log_info "Removing Conda environment..."
    conda env remove -n bielik
    log_success "Conda environment removed"
}

# Main function
main() {
    case "${1:-}" in
        create|env)
            create_env
            ;;
        dev|setup-dev)
            create_env
            setup_dev
            ;;
        clean|remove)
            clean_env
            ;;
        help|--help|-h)
            echo "Conda Environment Management for Bielik"
            echo "Usage: $0 {create|dev|clean|help}"
            echo ""
            echo "Commands:"
            echo "  create, env     - Create Conda environment"
            echo "  dev, setup-dev  - Create environment + install dev dependencies"
            echo "  clean, remove   - Remove Conda environment"
            echo "  help            - Show this help"
            ;;
        *)
            log_error "Unknown command: ${1:-}"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run only if script is executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
