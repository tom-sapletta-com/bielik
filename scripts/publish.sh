#!/bin/bash

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Usage function
usage() {
    echo "Usage: $0 [patch|minor|major]"
    echo "  patch - increment patch version (default)"
    echo "  minor - increment minor version"  
    echo "  major - increment major version"
    exit 1
}

# Get bump type from argument or default to patch
BUMP_TYPE=${1:-patch}

if [[ ! "$BUMP_TYPE" =~ ^(patch|minor|major)$ ]]; then
    echo "${RED}❌ Invalid bump type: $BUMP_TYPE${NC}"
    usage
fi

echo "${YELLOW}📦 Publishing Bielik to PyPI with $BUMP_TYPE version increment...${NC}"

# Check if we have a local venv and activate it
if [[ -d ".venv" ]]; then
    echo "${YELLOW}📍 Activating local virtual environment...${NC}"
    source .venv/bin/activate
    echo "${GREEN}✅ Virtual environment activated: $VIRTUAL_ENV${NC}"
else
    echo "${YELLOW}⚠️  No local .venv found, using system Python${NC}"
fi

# Ensure build dependencies are installed
echo "${YELLOW}📦 Checking dependencies...${NC}"

# Check if build dependencies are available
if python3 -c "import build, twine" > /dev/null 2>&1; then
    echo "${GREEN}✅ Build dependencies already available${NC}"
else
    echo "${YELLOW}📦 Installing build dependencies...${NC}"
    if [[ -n "$VIRTUAL_ENV" ]]; then
        pip install build twine
    else
        echo "${RED}❌ No virtual environment active${NC}"
        echo "${YELLOW}💡 Please activate a virtual environment or install: pip install build twine${NC}"
        exit 1
    fi
fi

# Auto-increment version
echo "${YELLOW}🔢 Auto-incrementing $BUMP_TYPE version...${NC}"
if python3 scripts/bump-version.py $BUMP_TYPE; then
    echo "${GREEN}✅ Version incremented successfully${NC}"
else
    echo "${RED}❌ Failed to increment version${NC}"
    exit 1
fi

# Clean previous builds
echo "${YELLOW}🧹 Cleaning previous builds...${NC}"
rm -rf build/ dist/ *.egg-info/

# Build the package
echo "${YELLOW}🏗️ Building package...${NC}"
if python3 -m build; then
    echo "${GREEN}✅ Package built successfully${NC}"
else
    echo "${RED}❌ Package build failed${NC}"
    exit 1
fi

# Upload to PyPI (dry-run for testing)
echo "${YELLOW}🚀 Ready to upload to PyPI...${NC}"
echo "${YELLOW}💡 This is a test - skipping actual upload${NC}"
echo "${YELLOW}📦 To actually publish, run: twine upload dist/*${NC}"

# Get the new version for confirmation
NEW_VERSION=$(grep -o 'version = "[^"]*"' pyproject.toml | cut -d'"' -f2)
echo "${GREEN}✅ Build complete for Bielik version ${NEW_VERSION}${NC}"
echo "${GREEN}📦 Ready to install with: pip install bielik${NC}"
echo "${GREEN}🔗 Package URL: https://pypi.org/project/bielik/${NC}"

# Show what would be uploaded
echo "${YELLOW}📋 Files ready for upload:${NC}"
ls -la dist/
twine upload dist/*