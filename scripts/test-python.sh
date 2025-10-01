#!/bin/bash
# Python testing and linting for Bielik

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

# Run linting
run_lint() {
    log_info "Running flake8..."
    flake8 bielik
    log_success "Linting passed!"
}

# Run Python unit tests
run_pytest() {
    log_info "Running Python unit tests..."
    pytest
    log_success "Python tests passed!"
}

# Run command tests
run_command_tests() {
    log_info "Running command tests..."
    ./scripts/test-commands.sh
    log_success "Command tests passed!"
}

# Install package in development mode
install_dev() {
    log_info "Installing Bielik in development mode..."
    pip install -e .
    log_success "Bielik installed in development mode"
}

# Run all tests
run_all() {
    run_lint
    run_pytest
    run_command_tests
    log_success "All Python tests completed successfully!"
}

# Main function
main() {
    case "${1:-}" in
        lint)
            run_lint
            ;;
        pytest|unit)
            run_pytest
            ;;
        commands|cmd)
            run_command_tests
            ;;
        install)
            install_dev
            ;;
        all|test)
            run_all
            ;;
        help|--help|-h)
            echo "Python Testing Framework for Bielik"
            echo "Usage: $0 {lint|pytest|commands|install|all|help}"
            echo ""
            echo "Commands:"
            echo "  lint            - Run code style checks (flake8)"
            echo "  pytest, unit    - Run Python unit tests"
            echo "  commands, cmd   - Run command functionality tests"
            echo "  install         - Install Bielik in development mode"
            echo "  all, test       - Run all tests (lint + pytest + commands)"
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
