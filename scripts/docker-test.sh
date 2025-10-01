#!/bin/bash
# Docker testing framework for Bielik

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

# Build Docker test images
build_images() {
    log_info "Building Docker test images..."
    docker-compose -f docker/test-multiplatform.yml build
    log_success "Docker images built!"
}

# Clean Docker resources
clean_docker() {
    log_info "Cleaning Docker test artifacts..."
    docker-compose -f docker/test-multiplatform.yml down --volumes --remove-orphans 2>/dev/null || true
    docker system prune -f 2>/dev/null || true
    log_success "Docker cleanup completed!"
}

# Test individual distributions
test_ubuntu() {
    log_info "Testing Ubuntu installation..."
    docker-compose -f docker/test-multiplatform.yml run --rm test-ubuntu
    log_success "Ubuntu test completed!"
}

test_debian() {
    log_info "Testing Debian installation..."
    docker-compose -f docker/test-multiplatform.yml run --rm test-debian
    log_success "Debian test completed!"
}

test_alpine() {
    log_info "Testing Alpine Linux installation..."
    docker-compose -f docker/test-multiplatform.yml run --rm test-alpine
    log_success "Alpine test completed!"
}

test_centos() {
    log_info "Testing CentOS/RHEL installation..."
    docker-compose -f docker/test-multiplatform.yml run --rm test-centos
    log_success "CentOS test completed!"
}

test_arch() {
    log_info "Testing Arch Linux installation..."
    docker-compose -f docker/test-multiplatform.yml run --rm test-arch
    log_success "Arch test completed!"
}

test_oneliner() {
    log_info "Testing one-liner installation..."
    docker-compose -f docker/test-multiplatform.yml run --rm test-oneliner
    log_success "One-liner test completed!"
}

# Run complete Docker test suite
test_all() {
    clean_docker
    build_images
    
    log_info "Running complete Docker multiplatform test suite..."
    echo ""
    log_info "Testing on all supported Linux distributions:"
    echo "  • Ubuntu 22.04"
    echo "  • Debian 12"
    echo "  • Alpine Linux 3.19"
    echo "  • CentOS Stream 9"
    echo "  • Arch Linux"
    echo "  • One-liner installation"
    echo ""
    
    test_ubuntu
    test_debian
    test_alpine
    test_centos
    test_arch
    test_oneliner
    
    echo ""
    log_success "All Docker multiplatform tests passed!"
    clean_docker
}

# Main function
main() {
    case "${1:-}" in
        build)
            build_images
            ;;
        clean)
            clean_docker
            ;;
        ubuntu)
            test_ubuntu
            ;;
        debian)
            test_debian
            ;;
        alpine)
            test_alpine
            ;;
        centos)
            test_centos
            ;;
        arch)
            test_arch
            ;;
        oneliner)
            test_oneliner
            ;;
        all|test)
            test_all
            ;;
        help|--help|-h)
            echo "Docker Testing Framework for Bielik"
            echo "Usage: $0 {build|clean|ubuntu|debian|alpine|centos|arch|oneliner|all|help}"
            echo ""
            echo "Commands:"
            echo "  build           - Build all Docker test images"
            echo "  clean           - Clean up Docker resources"
            echo "  ubuntu          - Test Ubuntu installation"
            echo "  debian          - Test Debian installation"
            echo "  alpine          - Test Alpine Linux installation"
            echo "  centos          - Test CentOS/RHEL installation"
            echo "  arch            - Test Arch Linux installation"
            echo "  oneliner        - Test one-liner installation"
            echo "  all, test       - Run complete Docker test suite"
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
