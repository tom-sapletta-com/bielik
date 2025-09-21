#!/bin/bash

# Bielik Minimal Version - Usage Examples
# Demonstrates text-only features and HuggingFace model management

set -e

echo "🚀 Bielik Minimal Version - Usage Examples"
echo "==========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\n${BLUE}📦 Testing Installation Size...${NC}"
echo "Minimal version installed size: ~50MB"
echo "Dependencies: essential packages only"

echo -e "\n${BLUE}🔧 Basic CLI Commands${NC}"
echo "------------------------"

echo -e "${YELLOW}1. Show available commands:${NC}"
echo "python -m bielik --help"
echo ""

echo -e "${YELLOW}2. List available HuggingFace models:${NC}"
echo ":models"
echo ""

echo -e "${YELLOW}3. Download a Polish model:${NC}"
echo ":download speakleash/bielik-4.5b-v3.0-instruct"
echo ""

echo -e "${YELLOW}4. Switch to downloaded model:${NC}"
echo ":switch speakleash/bielik-4.5b-v3.0-instruct"
echo ""

echo -e "${YELLOW}5. Check current settings:${NC}"
echo ":settings"
echo ""

echo -e "${YELLOW}6. Set your name:${NC}"
echo ":name Jan"
echo ""

echo -e "\n${BLUE}💬 Chat Examples${NC}"
echo "-------------------"

echo -e "${YELLOW}Text conversation:${NC}"
echo "User: Napisz krótki wiersz o Polsce"
echo "Bielik: [Generates Polish poem]"
echo ""

echo -e "${YELLOW}Code generation:${NC}"
echo "User: Napisz funkcję Python do sortowania listy"
echo "Bielik: [Generates Python sorting function]"
echo ""

echo -e "\n${BLUE}📁 Folder Analysis${NC}"
echo "---------------------"

echo -e "${YELLOW}Analyze project structure:${NC}"
echo "python -m bielik analyze /path/to/project"
echo ""

echo -e "${YELLOW}Interactive folder analysis:${NC}"
echo "User: Przeanalizuj folder /home/user/docs"
echo "Bielik: [Analyzes folder contents and provides summary]"
echo ""

echo -e "\n${BLUE}🌐 Web Content Processing${NC}"
echo "----------------------------"

echo -e "${YELLOW}Process web page:${NC}"
echo "User: Przeanalizuj https://example.com"
echo "Bielik: [Downloads and analyzes web content]"
echo ""

echo -e "\n${BLUE}📄 Document Processing${NC}"
echo "-------------------------"

echo -e "${YELLOW}Process PDF document:${NC}"
echo "User: Przeanalizuj document.pdf"
echo "Bielik: [Extracts and analyzes PDF content]"
echo ""

echo -e "${YELLOW}Process Word document:${NC}"
echo "User: Przeczytaj raport.docx"
echo "Bielik: [Extracts and analyzes DOCX content]"
echo ""

echo -e "\n${GREEN}✨ Key Features in Minimal Version:${NC}"
echo "- Polish language conversation"
echo "- HuggingFace model management"
echo "- Text document processing (PDF, DOCX, TXT)"
echo "- Web content analysis"
echo "- Folder structure analysis"
echo "- Personalized CLI experience"
echo "- Lightweight installation (~50MB)"
echo ""

echo -e "\n${YELLOW}📚 What's NOT included in minimal version:${NC}"
echo "- Image analysis (requires: pip install bielik[vision])"
echo "- Vision-language models"
echo "- GPU acceleration"
echo ""

echo -e "\n${BLUE}🚀 Quick Start:${NC}"
echo "docker run -it -v \$(pwd)/models:/app/models bielik:minimal"
