#!/bin/bash
# Install Bielik dependencies in Conda environment

set -e

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Check if Conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: Conda is not available. Please activate your Conda environment first."
    exit 1
fi

# Get the current Conda environment name
ENV_NAME=$(conda info --envs | grep '\*' | awk '{print $1}')

if [ -z "$ENV_NAME" ]; then
    echo "Error: No active Conda environment found."
    echo "Please activate your Bielik environment first:"
    echo "  conda activate bielik"
    exit 1
fi

echo -e "${GREEN}Installing dependencies in Conda environment: $ENV_NAME${NC}"

# Install dependencies using Conda and pip
echo -e "${GREEN}Installing core dependencies with Conda...${NC}"
conda install -y -c conda-forge \
    cmake \
    make \
    gcc_linux-64 \
    gxx_linux-64 \
    libgcc \
    libstdcxx-ng \
    python=3.11

echo -e "${GREEN}Installing PyTorch and dependencies...${NC}"
conda install -y -c pytorch -c nvidia \
    pytorch \
    torchvision \
    torchaudio \
    pytorch-cuda=12.1 \
    cuda-toolkit

echo -e "${GREEN}Installing Hugging Face libraries...${NC}"
pip install --upgrade \
    transformers \
    datasets \
    accelerate \
    bitsandbytes \
    sentencepiece \
    huggingface-hub

echo -e "${GREEN}Installing llama-cpp-python with CUDA support...${NC}"
CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install llama-cpp-python --no-cache-dir

echo -e "${GREEN}Installing Bielik in development mode...${NC}"
pip install -e ".[local,dev,test]"

echo -e "\n${GREEN}✅ Installation complete!${NC}"
echo "Verify the installation with:"
echo "  python scripts/verify_installation.py"
echo "\nStart Bielik with:"
echo "  bielik"
