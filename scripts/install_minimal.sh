#!/bin/bash
# Minimal Bielik Installation Script

set -e

echo "🚀 Starting minimal Bielik installation..."

# Check if Conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed. Please install Miniconda first."
    echo "   Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Create a minimal Conda environment
echo "🔧 Creating minimal Conda environment..."
conda create -n bielik-minimal python=3.11 -y

# Activate the environment
eval "$(conda shell.bash hook)"
conda activate bielik-minimal

# Install minimal dependencies
echo "📦 Installing core dependencies..."
conda install -y -c conda-forge \
    cmake \
    make \
    gcc_linux-64 \
    gxx_linux-64 \
    python=3.11

# Install PyTorch with CPU-only support
echo "🧠 Installing PyTorch..."
conda install -y -c pytorch pytorch torchvision torchaudio cpuonly

# Install Hugging Face libraries
echo "🤗 Installing Hugging Face libraries..."
pip install --upgrade \
    transformers \
    accelerate \
    sentencepiece \
    huggingface-hub

# Install llama-cpp-python with minimal options
echo "🦙 Installing llama-cpp-python..."
CMAKE_ARGS="-DLLAMA_NO_METAL=on" FORCE_CMAKE=1 pip install llama-cpp-python --no-cache-dir

# Install Bielik in development mode
echo "⚡ Installing Bielik..."
pip install -e ".[local]"

echo -e "\n✅ Installation complete!"
echo -e "\nTo activate the environment and start Bielik, run:"
echo -e "  conda activate bielik-minimal"
echo -e "  bielik"
echo -e "\nTo verify the installation:"
echo -e "  python scripts/verify_installation.py"
