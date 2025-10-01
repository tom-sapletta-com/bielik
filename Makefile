.PHONY: help install install-dev verify conda-env conda-dev conda-clean lint test build publish clean bump-patch bump-minor bump-major docker-test docker-test-ubuntu docker-test-debian docker-test-alpine docker-test-centos docker-test-arch docker-test-oneliner docker-build docker-clean test-all

# Default target when running just 'make'
help:
	@echo "\n🦅 Bielik Development Commands"
	@echo "=========================="
	@echo "\n📦 Installation & Setup:"
	@echo "  make install       - Universal installation (auto-installs conda if needed)"
	@echo "  make install-dev   - Quick dev install (assumes conda env exists)"
	@echo "  make verify        - Verify installation and dependencies"
	@echo "  make conda-env     - Create Conda environment with all dependencies"
	@echo "  make conda-dev     - Set up development environment (run after conda-env)"
	@echo "  make conda-clean   - Remove Conda environment"
	@echo "\n🧪 Testing:"
	@echo "  make test          - Run Python unit tests"
	@echo "  make test-commands - Test all command modules (calc, folder, pdf, project)"
	@echo "  make test-all      - Run all tests (Python + Commands + Docker)"
	@echo "  make lint          - Run code style checks"
	@echo "\n🐳 Docker Testing:"
	@echo "  make docker-build  - Build all Docker test images"
	@echo "  make docker-test   - Run complete Docker test suite"
	@echo "  make docker-clean  - Clean up Docker resources"

# Conda environment management
conda-env:
	@bash scripts/conda-env.sh create

conda-dev:
	@bash scripts/conda-env.sh dev

conda-clean:
	@bash scripts/conda-env.sh clean

# Version management
bump-patch:
	@python scripts/bump-version.py patch

bump-minor:
	@python scripts/bump-version.py minor

bump-major:
	@python scripts/bump-version.py major

# Install package in development mode with full conda setup
install:
	@echo "🦅 Running universal Bielik installation..."
	@bash scripts/universal-install.sh

# Quick install for development (assumes conda env exists)
install-dev:
	@bash scripts/test-python.sh install

verify:
	@python scripts/verify_installation.py

lint:
	@bash scripts/test-python.sh lint

# Python Unit Tests
test:
	@bash scripts/test-python.sh pytest

# Command Tests
test-commands:
	@bash scripts/test-commands.sh

# Complete test suite (Python + Docker)
test-all: test test-commands docker-test
	@echo "🎉 All tests completed successfully!"

# Docker Testing Framework
docker-build:
	@bash scripts/docker-test.sh build

docker-clean:
	@bash scripts/docker-test.sh clean

# Individual distribution tests
docker-test-ubuntu:
	@bash scripts/docker-test.sh ubuntu

docker-test-debian:
	@bash scripts/docker-test.sh debian

docker-test-alpine:
	@bash scripts/docker-test.sh alpine

docker-test-centos:
	@bash scripts/docker-test.sh centos

docker-test-arch:
	@bash scripts/docker-test.sh arch

docker-test-oneliner:
	@bash scripts/docker-test.sh oneliner

# Complete Docker test suite
docker-test:
	@bash scripts/docker-test.sh all

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
	@bash scripts/clean.sh
