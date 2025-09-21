.PHONY: install dev lint test build publish clean setup-dev

install:
	python3 -m pip install --upgrade pip
	python3 -m pip install .

setup-dev:
	python3 -m pip install --upgrade pip
	python3 -m pip install -e .[ollama] pytest flake8 build twine httpx

dev: setup-dev
	@echo "✅ Development environment ready!"
	@echo "📋 Available commands:"
	@echo "  make test    - Run tests"
	@echo "  make lint    - Run linting"
	@echo "  make build   - Build package"
	@echo "  make publish - Publish to PyPI"

lint:
	@echo "🔍 Running flake8..."
	flake8 bielik
	@echo "✅ Linting passed!"

test:
	@echo "🧪 Running tests..."
	pytest
	@echo "✅ All tests passed!"

build:
	@echo "🔨 Building package..."
	python3 -m build
	@echo "✅ Package built successfully!"

publish: clean build
	@echo "🚀 Publishing to PyPI..."
	twine upload dist/*
	@echo "✅ Package published successfully!"
	@echo ""
	@echo "🎉 Congratulations! Your package is now available on PyPI!"
	@echo "📦 Install with: pip install bielik"
	@echo "🔗 Package URL: https://pypi.org/project/bielik/"
	@echo ""
	@echo "Next steps:"
	@echo "1. Tag this release: git tag v0.1.0 && git push origin v0.1.0"
	@echo "2. Create GitHub release with changelog"
	@echo "3. Update documentation if needed"

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build dist *.egg-info .pytest_cache __pycache__ */__pycache__
	@echo "✅ Clean completed!"
