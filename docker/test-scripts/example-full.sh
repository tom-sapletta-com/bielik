#!/bin/bash

# Bielik Full Version - Usage Examples
# Demonstrates complete features including image analysis and vision capabilities

set -e

echo "🚀 Bielik Full Version - Usage Examples"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "\n${BLUE}📦 Testing Installation Size...${NC}"
echo "Full version installed size: ~2GB+"
echo "Dependencies: PyTorch, Transformers, Pillow, and more"

echo -e "\n${BLUE}🔧 All Minimal Features + Vision${NC}"
echo "-------------------------------------"

echo -e "${GREEN}✨ Includes all minimal version features:${NC}"
echo "- Polish language conversation"
echo "- HuggingFace model management"
echo "- Document processing (PDF, DOCX, TXT)"
echo "- Web content analysis"
echo "- Folder structure analysis"
echo "- Personalized CLI experience"
echo ""

echo -e "\n${BLUE}🖼️ Image Analysis Features${NC}"
echo "-----------------------------"

echo -e "${YELLOW}1. Analyze single image:${NC}"
echo "User: Przeanalizuj image.jpg"
echo "Bielik: [Generates detailed image description in Polish]"
echo ""

echo -e "${YELLOW}2. Visual Question Answering:${NC}"
echo "User: Co widać na tym zdjęciu? [uploads photo.png]"
echo "Bielik: [Analyzes image and answers in Polish]"
echo ""

echo -e "${YELLOW}3. Batch image analysis:${NC}"
echo "User: Przeanalizuj folder /images"
echo "Bielik: [Analyzes all images in folder]"
echo ""

echo -e "${YELLOW}4. Image + text analysis:${NC}"
echo "User: Opisz to zdjęcie i powiedz czy pasuje do tekstu: [image + text]"
echo "Bielik: [Analyzes both image and text, provides comparison]"
echo ""

echo -e "\n${BLUE}🤖 Vision-Language Models${NC}"
echo "----------------------------"

echo -e "${YELLOW}Available vision models:${NC}"
echo "- Salesforce/blip-image-captioning-base"
echo "- Salesforce/blip-image-captioning-large"
echo "- Microsoft/git-base-coco"
echo "- Others from HuggingFace Hub"
echo ""

echo -e "\n${BLUE}🎯 Advanced Use Cases${NC}"
echo "------------------------"

echo -e "${YELLOW}1. Document with images:${NC}"
echo "User: Przeanalizuj presentation.pptx"
echo "Bielik: [Processes text AND extracts/analyzes embedded images]"
echo ""

echo -e "${YELLOW}2. Web page with images:${NC}"
echo "User: Przeanalizuj https://news-site.com/article"
echo "Bielik: [Processes text AND analyzes article images]"
echo ""

echo -e "${YELLOW}3. Project analysis with screenshots:${NC}"
echo "User: Przeanalizuj folder /projekt (zawiera kod + screenshots)"
echo "Bielik: [Analyzes code structure AND UI screenshots]"
echo ""

echo -e "\n${BLUE}⚡ GPU Acceleration${NC}"
echo "---------------------"

echo -e "${YELLOW}With GPU support:${NC}"
echo "docker run --gpus all -it -v \$(pwd)/models:/app/models bielik:full"
echo ""

echo -e "${YELLOW}GPU features:${NC}"
echo "- Faster image analysis"
echo "- Larger vision models support"
echo "- Batch processing acceleration"
echo ""

echo -e "\n${BLUE}🛠️ Vision Model Management${NC}"
echo "------------------------------"

echo -e "${YELLOW}Download vision models:${NC}"
echo ":download-vision Salesforce/blip-image-captioning-large"
echo ""

echo -e "${YELLOW}List vision models:${NC}"
echo ":vision-models"
echo ""

echo -e "${YELLOW}Test image analysis:${NC}"
echo ":test-vision /path/to/image.jpg"
echo ""

echo -e "\n${BLUE}📊 Performance Comparison${NC}"
echo "-----------------------------"

echo -e "${YELLOW}Minimal Version:${NC}"
echo "- Install size: ~50MB"
echo "- Memory usage: ~100MB"
echo "- Features: Text only"
echo "- Startup time: <2s"
echo ""

echo -e "${YELLOW}Full Version:${NC}"
echo "- Install size: ~2GB+"
echo "- Memory usage: ~500MB-2GB"
echo "- Features: Text + Vision"
echo "- Startup time: ~5-10s"
echo ""

echo -e "\n${GREEN}🎯 When to use Full Version:${NC}"
echo "- Image analysis required"
echo "- Visual content processing"
echo "- Multimodal AI applications"
echo "- Rich media document analysis"
echo "- UI/UX analysis from screenshots"
echo ""

echo -e "\n${RED}⚠️ Full Version Requirements:${NC}"
echo "- More disk space (~2GB+)"
echo "- More RAM (min 4GB recommended)"
echo "- Optional: GPU for better performance"
echo ""

echo -e "\n${BLUE}🚀 Quick Start Commands:${NC}"
echo "# Basic full version"
echo "docker run -it -v \$(pwd)/models:/app/models -v \$(pwd)/images:/app/images bielik:full"
echo ""
echo "# With GPU acceleration"
echo "docker run --gpus all -it -v \$(pwd)/models:/app/models bielik:full"
echo ""
echo "# Docker Compose"
echo "docker-compose --profile full up bielik-full"
