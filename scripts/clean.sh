#!/bin/bash
# Clean build artifacts for Bielik

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

# Clean build artifacts
clean_build() {
    log_info "Cleaning build artifacts..."
    
    # Remove Python build artifacts
    rm -rf build dist *.egg-info .pytest_cache __pycache__ */__pycache__
    
    # Remove Python bytecode files
    find . -name "*.pyc" -delete
    find . -name "*.pyo" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    log_success "Build artifacts cleaned!"
}

# Clean test artifacts
clean_test() {
    log_info "Cleaning test artifacts..."
    
    # Remove test output files
    rm -f /tmp/test_output
    rm -rf /tmp/test_bielik_*
    rm -f /tmp/test_document.*
    
    # Remove coverage files
    rm -f .coverage
    rm -rf htmlcov/
    
    log_success "Test artifacts cleaned!"
}

# Clean all
clean_all() {
    clean_build
    clean_test
    log_success "All cleanup completed!"
}

# Main function
main() {
    case "${1:-}" in
        build)
            clean_build
            ;;
        test)
            clean_test
            ;;
        all|"")
            clean_all
            ;;
        help|--help|-h)
            echo "Clean Build Artifacts for Bielik"
            echo "Usage: $0 {build|test|all|help}"
            echo ""
            echo "Commands:"
            echo "  build           - Clean build artifacts (dist, build, __pycache__, etc.)"
            echo "  test            - Clean test artifacts (temp files, coverage, etc.)"
            echo "  all             - Clean all artifacts (default)"
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
