#!/bin/bash
# Bielik CLI Docker Test Runner Script
# Comprehensive testing in isolated Docker environment

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "🐳 Bielik CLI Docker Testing Environment"
echo "========================================"
echo "Project root: $PROJECT_ROOT"
echo

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker and try again."
        exit 1
    fi
    echo "✅ Docker is running"
}

# Function to build Docker image
build_image() {
    echo "📦 Building Docker test image..."
    docker build -f Dockerfile.simple -t bielik-simple-test:latest .
    echo "✅ Docker image built successfully"
}

# Function to run automated tests
run_automated_tests() {
    echo "🧪 Running automated tests in Docker..."
    docker-compose -f docker-compose.simple.yml run --rm bielik-auto-test
    echo "✅ Automated tests completed"
}

# Function to start interactive testing environment
start_interactive() {
    echo "🖥️ Starting interactive Docker environment..."
    echo "You can now test all Bielik CLI commands manually."
    echo "Available commands:"
    echo "  - calc: 2 + 3 * 4"
    echo "  - pdf: help"
    echo "  - folder: ."
    echo "  - :project create 'Test Project' 'Testing in Docker'"
    echo "  - python /app/docker-test-runner.py  # Run automated tests"
    echo
    echo "Type 'exit' to leave the container."
    echo "Data will persist in Docker volumes."
    echo
    docker-compose -f docker-compose.simple.yml run --rm bielik-simple-test
}

# Function to clean up Docker resources
cleanup() {
    echo "🧹 Cleaning up Docker resources..."
    docker-compose -f docker-compose.simple.yml down -v
    docker image rm bielik-simple-test:latest 2>/dev/null || true
    echo "✅ Cleanup completed"
}

# Function to show test results
show_results() {
    echo "📊 Showing test results..."
    if docker-compose -f docker-compose.simple.yml run --rm bielik-simple-test cat /app/test-results.json 2>/dev/null; then
        echo "✅ Test results displayed"
    else
        echo "⚠️ No test results found. Run tests first."
    fi
}

# Function to copy test results from container
copy_results() {
    echo "📋 Copying test results from container..."
    CONTAINER_ID=$(docker-compose -f docker-compose.simple.yml run -d bielik-simple-test /bin/bash)
    docker cp "$CONTAINER_ID:/app/test-results.json" ./docker-test-results.json 2>/dev/null || echo "⚠️ No results to copy"
    docker rm "$CONTAINER_ID" > /dev/null 2>&1
    if [ -f "./docker-test-results.json" ]; then
        echo "✅ Results copied to docker-test-results.json"
    fi
}

# Main function
main() {
    case "${1:-help}" in
        "build")
            check_docker
            build_image
            ;;
        "test")
            check_docker
            build_image
            run_automated_tests
            copy_results
            ;;
        "interactive"|"shell")
            check_docker
            build_image
            start_interactive
            ;;
        "results")
            show_results
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            echo "Usage: $0 {build|test|interactive|results|cleanup}"
            echo
            echo "Commands:"
            echo "  build       - Build Docker test image"
            echo "  test        - Run automated tests in Docker"
            echo "  interactive - Start interactive testing shell"  
            echo "  results     - Show test results"
            echo "  cleanup     - Clean up Docker resources"
            echo "  help        - Show this help message"
            echo
            echo "Examples:"
            echo "  $0 test           # Run all automated tests"
            echo "  $0 interactive    # Start interactive shell for manual testing"
            echo "  $0 results        # View test results"
            ;;
    esac
}

main "$@"
