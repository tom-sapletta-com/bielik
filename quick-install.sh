#!/bin/bash
# Bielik CLI One-liner Installer for Unix/Linux/macOS
# Usage: curl -sSL https://raw.githubusercontent.com/tom-sapletta-com/bielik/main/quick-install.sh | bash

set -e

echo "🚀 Bielik CLI Quick Installer"
echo "=============================="

# Check if git is available
if ! command -v git >/dev/null 2>&1; then
    echo "❌ git not found. Please install git first."
    echo "   Ubuntu/Debian: sudo apt install git"
    echo "   CentOS/RHEL: sudo yum install git"
    echo "   macOS: xcode-select --install"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
    echo "❌ Python 3 not found. Please install Python 3.8+ first."
    echo "   Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "   CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "   macOS: brew install python3"
    exit 1
fi

# Clone repository
INSTALL_DIR="$HOME/bielik"
if [ -d "$INSTALL_DIR" ]; then
    echo "📂 Found existing installation at $INSTALL_DIR"
    cd "$INSTALL_DIR"
    git pull origin main
else
    echo "📥 Cloning Bielik repository..."
    git clone https://github.com/tom-sapletta-com/bielik.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Make scripts executable
chmod +x install.sh run.py

# Run installer
echo "🔧 Running installer..."
python3 install.py --skip-ai

# Test installation
echo "🧪 Testing installation..."
if ./run.py --info >/dev/null 2>&1; then
    echo "✅ Installation successful!"
    echo ""
    echo "🎉 BIELIK CLI READY TO USE!"
    echo "=========================="
    echo "📂 Installation directory: $INSTALL_DIR"
    echo ""
    echo "🚀 Quick Start:"
    echo "   cd $INSTALL_DIR"
    echo "   ./run.py"
    echo ""
    echo "🔗 Or add to PATH:"
    echo "   echo 'export PATH=\"$INSTALL_DIR:\$PATH\"' >> ~/.bashrc"
    echo "   source ~/.bashrc"
    echo "   bielik  # (after adding run.py as 'bielik' symlink)"
    echo ""
    echo "📊 Try Context Provider Commands:"
    echo "   folder: ."
    echo "   calc: 2+3*4"
    echo "   :help"
else
    echo "❌ Installation test failed"
    echo "💡 Try manual installation:"
    echo "   cd $INSTALL_DIR"
    echo "   python3 install.py --help"
    exit 1
fi
