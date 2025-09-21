#!/bin/bash
# Build script for Bielik project

echo "🔨 Building package..."

# Check if we have a local venv and activate it
if [[ -d ".venv" ]]; then
    echo "📍 Activating local virtual environment..."
    source .venv/bin/activate
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "⚠️  No local .venv found, using system Python"
fi

# Install build dependencies if needed
echo "📦 Checking build dependencies..."

# Check if build dependencies are available
if python3 -c "import build, twine" > /dev/null 2>&1; then
    echo "✅ Build dependencies already available"
else
    echo "📦 Installing build dependencies..."
    if [[ -n "$VIRTUAL_ENV" ]]; then
        pip install build twine
    else
        echo "⚠️  No virtual environment active"
        echo "💡 Please activate a virtual environment or install: pip install build twine"
        exit 1
    fi
fi

# Build package
echo "🏗️ Building distributions..."
python3 -m build

if [ $? -eq 0 ]; then
    echo "✅ Package built successfully!"
else
    echo "❌ Build failed!"
    exit 1
fi
