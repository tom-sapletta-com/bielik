.PHONY: install dev lint test build publish clean setup-dev bump-patch bump-minor bump-major publish-patch publish-minor publish-major docker-test docker-test-ubuntu docker-test-debian docker-test-alpine docker-test-centos docker-test-arch docker-test-oneliner docker-build docker-clean test-all

install:
	#rm -rf .venv
	#python3 -m venv .venv
	source .venv/bin/activate
	@python3 -m pip install --upgrade pip
	@python3 -m pip install -e .

setup-dev:
	python3 -m pip install --upgrade pip
	python3 -m pip install -e .[ollama] pytest flake8 build twine httpx

# Version management
bump-patch:
	@python3 scripts/bump-version.py patch

bump-minor:
	@python3 scripts/bump-version.py minor

bump-major:
	@python3 scripts/bump-version.py major

dev: setup-dev
	@echo "✅ Development environment ready!"
	@echo ""
	@echo "📋 Available commands:"
	@echo "🧪 Testing:"
	@echo "  make test           - Run Python unit tests"
	@echo "  make docker-test    - Run complete Docker multiplatform test suite"
	@echo "  make test-all       - Run both Python and Docker tests"
	@echo ""
	@echo "🐳 Docker Testing (Individual):"
	@echo "  make docker-test-ubuntu   - Test Ubuntu 22.04"
	@echo "  make docker-test-debian   - Test Debian 12"
	@echo "  make docker-test-alpine   - Test Alpine Linux 3.19"
	@echo "  make docker-test-centos   - Test CentOS Stream 9"
	@echo "  make docker-test-arch     - Test Arch Linux"
	@echo "  make docker-test-oneliner - Test one-liner installation"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make lint           - Run linting"
	@echo "  make build          - Build package"
	@echo "  make publish        - Publish to PyPI"
	@echo "  make docker-build   - Build Docker test images"
	@echo "  make docker-clean   - Clean Docker artifacts"

lint:
	@echo "🔍 Running flake8..."
	flake8 bielik
	@echo "✅ Linting passed!"

# Python Unit Tests
test:
	@echo "🧪 Running Python unit tests..."
	pytest
	@echo "✅ Python tests passed!"

# Complete test suite (Python + Docker)
test-all: test docker-test
	@echo "🎉 All tests completed successfully!"

# Docker Testing Framework
docker-build:
	@echo "🐳 Building Docker test images..."
	@docker-compose -f docker/test-multiplatform.yml build
	@echo "✅ Docker images built!"

docker-clean:
	@echo "🧹 Cleaning Docker test artifacts..."
	@docker-compose -f docker/test-multiplatform.yml down --volumes --remove-orphans 2>/dev/null || true
	@docker system prune -f 2>/dev/null || true
	@echo "✅ Docker cleanup completed!"

# Individual distribution tests
docker-test-ubuntu:
	@echo "🐧 Testing Ubuntu installation..."
	@docker-compose -f docker/test-multiplatform.yml run --rm test-ubuntu
	@echo "✅ Ubuntu test completed!"

docker-test-debian:
	@echo "🐧 Testing Debian installation..."
	@docker-compose -f docker/test-multiplatform.yml run --rm test-debian
	@echo "✅ Debian test completed!"

docker-test-alpine:
	@echo "🏔️ Testing Alpine Linux installation..."
	@docker-compose -f docker/test-multiplatform.yml run --rm test-alpine
	@echo "✅ Alpine test completed!"

docker-test-centos:
	@echo "🎩 Testing CentOS/RHEL installation..."
	@docker-compose -f docker/test-multiplatform.yml run --rm test-centos
	@echo "✅ CentOS test completed!"

docker-test-arch:
	@echo "🏛️ Testing Arch Linux installation..."
	@docker-compose -f docker/test-multiplatform.yml run --rm test-arch
	@echo "✅ Arch test completed!"

docker-test-oneliner:
	@echo "🚀 Testing one-liner installation..."
	@docker-compose -f docker/test-multiplatform.yml run --rm test-oneliner
	@echo "✅ One-liner test completed!"

# Complete Docker test suite
docker-test: docker-clean docker-build
	@echo "🐳 Running complete Docker multiplatform test suite..."
	@echo ""
	@echo "📋 Testing on all supported Linux distributions:"
	@echo "  • Ubuntu 22.04"
	@echo "  • Debian 12"
	@echo "  • Alpine Linux 3.19"
	@echo "  • CentOS Stream 9"
	@echo "  • Arch Linux"
	@echo "  • One-liner installation"
	@echo ""
	@make docker-test-ubuntu
	@make docker-test-debian
	@make docker-test-alpine
	@make docker-test-centos
	@make docker-test-arch
	@make docker-test-oneliner
	@echo ""
	@echo "🎉 All Docker multiplatform tests passed!"
	@make docker-clean

build:
	@bash scripts/build.sh

publish-patch: clean
	@bash scripts/publish.sh patch

publish-minor: clean
	@bash scripts/publish.sh minor

publish-major: clean  
	@bash scripts/publish.sh major

publish: clean
	@bash scripts/publish.sh patch

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build dist *.egg-info .pytest_cache __pycache__ */__pycache__
	@echo "✅ Clean completed!"
