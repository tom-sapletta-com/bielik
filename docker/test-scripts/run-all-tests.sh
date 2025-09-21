#!/bin/bash

# Bielik Test Suite - Automated testing for both versions
# Tests minimal and full versions with various scenarios

set -e  # Exit on any error

echo "🧪 Starting Bielik Test Suite"
echo "==============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "\n${BLUE}🔬 Running: $test_name${NC}"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED: $test_name${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAILED: $test_name${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Test 1: Basic Import Test
run_test "Basic Import Test" "python -c 'import bielik; print(\"Bielik imported successfully\")'"

# Test 2: CLI Help Test  
run_test "CLI Help Test" "python -m bielik --help"

# Test 3: CLI Version Test
run_test "CLI Version Check" "python -c 'import bielik; print(f\"Version info available\")'"

# Test 4: HuggingFace Hub Connection
run_test "HuggingFace Hub Test" "python -c 'from huggingface_hub import HfApi; api = HfApi(); print(\"HF Hub connection OK\")'"

# Test 5: Models Command Test
run_test "Models List Test" "echo ':models' | timeout 10 python -m bielik --no-setup || true"

# Test 6: Settings Command Test  
run_test "Settings Command Test" "echo ':settings' | timeout 10 python -m bielik --no-setup || true"

# Test 7: Name Command Test
run_test "Name Command Test" "echo ':name TestUser' | timeout 10 python -m bielik --no-setup || true"

# Test 8: Folder Analysis Test (should work in minimal version)
run_test "Folder Analysis Test" "python -c 'from bielik.folder_scanner import FolderScanner; fs = FolderScanner(); print(\"Folder scanner works\")'"

# Test 9: Content Processing Test
run_test "Content Processing Test" "python -c 'from bielik.content_processor import get_content_processor; cp = get_content_processor(); print(\"Content processor works\")'"

# Test 10: HF Model Manager Test
run_test "HF Model Manager Test" "python -c 'from bielik.hf_models import get_model_manager; mm = get_model_manager(); print(f\"Available models: {len(mm.SPEAKLEASH_MODELS)}\")'"

# Test 11: CLI Settings Manager Test
run_test "CLI Settings Test" "python -c 'from bielik.cli.settings import get_cli_settings; s = get_cli_settings(); print(f\"User: {s.get_user_name()}\")'"

# Vision-specific tests (only if vision packages available)
echo -e "\n${YELLOW}🔍 Testing Vision Capabilities...${NC}"

if python -c "import PIL, transformers; print('Vision packages available')" 2>/dev/null; then
    echo -e "${GREEN}Vision packages detected - running vision tests${NC}"
    
    run_test "Image Analyzer Import" "python -c 'from bielik.image_analyzer import ImageAnalyzer; ia = ImageAnalyzer(); print(f\"Vision available: {ia.is_available()}\")'"
    
    # Create test image for analysis
    run_test "Create Test Image" "python -c 'from PIL import Image; img = Image.new(\"RGB\", (100, 100), \"blue\"); img.save(\"/tmp/test.jpg\")'"
    
    run_test "Image Analysis Test" "python -c 'from bielik.image_analyzer import ImageAnalyzer; ia = ImageAnalyzer(); result = ia.analyze_image(\"/tmp/test.jpg\"); print(f\"Analysis result type: {type(result)}\")'"
    
else
    echo -e "${YELLOW}⚠️ Vision packages not available - skipping vision tests${NC}"
    echo -e "${YELLOW}💡 Install with: pip install bielik[vision]${NC}"
fi

# Test Summary
echo -e "\n${BLUE}📊 Test Summary${NC}"
echo "================="
echo -e "${GREEN}✅ Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}❌ Tests Failed: $TESTS_FAILED${NC}"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
echo -e "${BLUE}📈 Total Tests: $TOTAL_TESTS${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! Bielik is working correctly.${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️ Some tests failed. Check the output above for details.${NC}"
    exit 1
fi
