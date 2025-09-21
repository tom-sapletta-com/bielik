#!/usr/bin/env python3
"""
Bielik CLI Universal Launcher
Cross-platform launcher script for Windows, Linux, macOS

This script automatically detects the platform and launches Bielik CLI
from the appropriate virtual environment.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


class BielikLauncher:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.system = platform.system().lower()
        self.is_windows = self.system == 'windows'
        
    def find_python_executable(self):
        """Find Python executable in virtual environment."""
        venv_dir = self.project_dir / '.venv'
        
        if self.is_windows:
            python_exe = venv_dir / 'Scripts' / 'python.exe'
        else:
            python_exe = venv_dir / 'bin' / 'python'
        
        return python_exe
    
    def check_installation(self):
        """Check if Bielik CLI is properly installed."""
        python_exe = self.find_python_executable()
        
        if not python_exe.exists():
            self.show_installation_help()
            return False
        
        # Test if bielik module is available
        try:
            result = subprocess.run(
                [str(python_exe), '-c', 'import bielik.cli.main'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print("❌ Bielik CLI not found in virtual environment")
                print("Please run the installer first:")
                self.show_installation_help()
                return False
            
            return True
            
        except subprocess.TimeoutExpired:
            print("⚠️ Timeout checking Bielik installation")
            return False
        except Exception as e:
            print(f"❌ Error checking installation: {e}")
            return False
    
    def show_installation_help(self):
        """Show platform-specific installation instructions."""
        print("\n🔧 INSTALLATION REQUIRED")
        print("=" * 50)
        
        if self.is_windows:
            print("Windows users:")
            print("  • Double-click install.bat")
            print("  • Or run: python install.py")
        else:
            print("Unix/Linux/macOS users:")
            print("  • Run: ./install.sh")
            print("  • Or: bash install.sh")
            print("  • Or: python install.py")
        
        print("\nFor more options:")
        print("  python install.py --help")
        print("\n💡 If you encounter issues:")
        print("  • Check Python 3.8+ is installed")
        print("  • Try: python install.py --skip-ai")
        print("  • See README.md for troubleshooting")
    
    def launch_bielik(self, args):
        """Launch Bielik CLI with provided arguments."""
        python_exe = self.find_python_executable()
        
        # Prepare command
        cmd = [str(python_exe), '-m', 'bielik.cli.main'] + args
        
        try:
            # Launch Bielik CLI
            subprocess.run(cmd, cwd=self.project_dir)
            
        except KeyboardInterrupt:
            print("\n👋 Bielik CLI interrupted by user")
            
        except FileNotFoundError:
            print("❌ Python executable not found")
            self.show_installation_help()
            sys.exit(1)
            
        except Exception as e:
            print(f"❌ Error launching Bielik CLI: {e}")
            sys.exit(1)
    
    def show_info(self):
        """Show system and installation info."""
        print(f"🖥️ System: {platform.system()} {platform.release()}")
        print(f"🐍 Python: {sys.version.split()[0]}")
        print(f"📂 Project: {self.project_dir}")
        
        python_exe = self.find_python_executable()
        if python_exe.exists():
            print(f"✅ Virtual environment: {python_exe.parent.parent}")
        else:
            print("❌ Virtual environment: Not found")


def main():
    """Main launcher entry point."""
    launcher = BielikLauncher()
    
    # Handle special arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--info', '--version', '-v']:
            launcher.show_info()
            return
        elif sys.argv[1] in ['--install-help', '-i']:
            launcher.show_installation_help()
            return
        elif sys.argv[1] in ['--help', '-h'] and len(sys.argv) == 2:
            print("Bielik CLI Universal Launcher")
            print("")
            print("Usage: python run.py [BIELIK_ARGS...]")
            print("")
            print("Launcher options:")
            print("  --info, -v          Show system information")
            print("  --install-help, -i  Show installation help")
            print("  --help, -h          Show this help (without args)")
            print("")
            print("All other arguments are passed to Bielik CLI.")
            print("Run 'python run.py :help' for Bielik CLI help.")
            return
    
    # Check if properly installed
    if not launcher.check_installation():
        sys.exit(1)
    
    # Launch Bielik with all arguments
    launcher.launch_bielik(sys.argv[1:])


if __name__ == "__main__":
    main()
