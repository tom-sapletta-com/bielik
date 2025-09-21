.PHONY: install dev lint test build publish clean setup-dev bump-patch bump-minor bump-major publish-patch publish-minor publish-major

install:
	python -m venv .venv
	source .venv/bin/activate
	python3 -m pip install --upgrade pip
	python3 -m pip install .

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
