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

# Ensure build dependencies are installed
echo "${YELLOW}📦 Checking dependencies...${NC}"

# Check if we're in a virtual environment or can install packages
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "${YELLOW}📍 Using virtual environment: $VIRTUAL_ENV${NC}"
    pip install --quiet build twine > /dev/null 2>&1 || {
        echo "${YELLOW}Installing build dependencies in venv...${NC}"
        pip install build twine
    }
elif python3 -c "import build, twine" > /dev/null 2>&1; then
    echo "${GREEN}✅ Build dependencies already available${NC}"
else
    echo "${YELLOW}⚠️  Build dependencies not found. Trying to install...${NC}"
    python3 -m pip install --quiet --user build twine > /dev/null 2>&1 || {
        echo "${RED}❌ Failed to install build dependencies${NC}"
        echo "${YELLOW}💡 Please run: pip install build twine${NC}"
        echo "${YELLOW}💡 Or activate a virtual environment first${NC}"
        exit 1
    }
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

# Upload to PyPI
echo "${YELLOW}🚀 Uploading to PyPI...${NC}"
if twine upload dist/*; then
    echo "${GREEN}✅ Published to PyPI successfully${NC}"
    
    # Get the new version for confirmation
    NEW_VERSION=$(grep -o 'version = "[^"]*"' pyproject.toml | cut -d'"' -f2)
    echo "${GREEN}🎉 Bielik version ${NEW_VERSION} is now live on PyPI!${NC}"
    echo "${GREEN}📦 Install with: pip install bielik${NC}"
    echo "${GREEN}🔗 Package URL: https://pypi.org/project/bielik/${NC}"
else
    echo "${RED}❌ Upload to PyPI failed${NC}"
    exit 1
fi
