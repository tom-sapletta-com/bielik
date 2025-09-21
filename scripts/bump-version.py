#!/usr/bin/env python3
"""
Version bumping script for Bielik project
Usage: python bump-version.py [patch|minor]
"""

import re
import sys
from pathlib import Path

def bump_version(bump_type='patch'):
    """Bump version in pyproject.toml"""
    pyproject_path = Path('pyproject.toml')
    
    if not pyproject_path.exists():
        print('❌ Could not find pyproject.toml')
        return False
    
    content = pyproject_path.read_text()
    match = re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content)
    
    if not match:
        print('❌ Could not find version in pyproject.toml')
        return False
    
    major, minor, patch = map(int, match.groups())
    
    if bump_type == 'patch':
        patch += 1
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    else:
        print(f'❌ Unknown bump type: {bump_type}')
        return False
    
    new_version = f"{major}.{minor}.{patch}"
    new_content = re.sub(
        r'version = "(\d+)\.(\d+)\.(\d+)"',
        f'version = "{new_version}"',
        content
    )
    
    pyproject_path.write_text(new_content)
    print(f'✅ Version bumped to {new_version}')
    return True

if __name__ == '__main__':
    bump_type = sys.argv[1] if len(sys.argv) > 1 else 'patch'
    success = bump_version(bump_type)
    sys.exit(0 if success else 1)
