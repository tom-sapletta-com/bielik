#!/bin/bash
# Bielik CLI Unix/Linux/macOS Launcher

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment not found. Please run install.py first."
    exit 1
fi

"$VENV_PYTHON" -m bielik.cli.main "$@"
