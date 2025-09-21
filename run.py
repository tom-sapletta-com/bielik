#!/usr/bin/env python3
"""
Bielik CLI Universal Launcher
Cross-platform launcher script
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get project directory
    project_dir = Path(__file__).parent
    
    # Determine virtual environment path
    venv_dir = project_dir / '.venv'
    
    if os.name == 'nt':  # Windows
        python_exe = venv_dir / 'Scripts' / 'python.exe'
    else:  # Unix/Linux/macOS
        python_exe = venv_dir / 'bin' / 'python'
    
    if not python_exe.exists():
        print("❌ Virtual environment not found. Please run install.py first.")
        sys.exit(1)
    
    # Launch Bielik CLI with all arguments
    cmd = [str(python_exe), '-m', 'bielik.cli.main'] + sys.argv[1:]
    
    try:
        subprocess.run(cmd, cwd=project_dir)
    except KeyboardInterrupt:
        print("\n👋 Bielik CLI interrupted by user")
    except Exception as e:
        print(f"❌ Error launching Bielik CLI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
