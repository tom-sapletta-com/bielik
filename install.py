#!/usr/bin/env python3
"""
Bielik CLI Universal Installer
Cross-platform installation script for Windows, Linux, macOS

Usage:
    python install.py [--conda] [--skip-ai] [--dev]
"""

import os
import sys
import subprocess
import platform
import shutil
import argparse
from pathlib import Path


class BielikInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.python_exe = sys.executable
        self.is_windows = self.system == 'windows'
        self.is_macos = self.system == 'darwin'
        self.is_linux = self.system == 'linux'
        self.project_dir = Path(__file__).parent
        self.venv_dir = self.project_dir / '.venv'
        
    def log(self, message, level="INFO"):
        """Cross-platform logging with colors."""
        colors = {
            'INFO': '\033[94m' if not self.is_windows else '',
            'SUCCESS': '\033[92m' if not self.is_windows else '',
            'WARNING': '\033[93m' if not self.is_windows else '',
            'ERROR': '\033[91m' if not self.is_windows else '',
            'RESET': '\033[0m' if not self.is_windows else ''
        }
        
        color = colors.get(level, colors['INFO'])
        reset = colors['RESET']
        
        print(f"{color}[{level}] {message}{reset}")
    
    def run_command(self, cmd, shell=False, check=True):
        """Run command with cross-platform compatibility."""
        try:
            if isinstance(cmd, str):
                cmd_list = cmd.split() if not shell else cmd
            else:
                cmd_list = cmd
                
            self.log(f"Running: {' '.join(cmd_list) if isinstance(cmd_list, list) else cmd_list}")
            
            result = subprocess.run(
                cmd_list,
                check=check,
                shell=shell or self.is_windows,
                capture_output=True,
                text=True,
                cwd=self.project_dir
            )
            
            if result.stdout:
                self.log(result.stdout.strip())
            
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e}", "ERROR")
            if e.stderr:
                self.log(f"Error: {e.stderr}", "ERROR")
            if not check:
                return None
            raise
    
    def detect_python_version(self):
        """Detect Python version and validate compatibility."""
        version = sys.version_info
        self.log(f"Python {version.major}.{version.minor}.{version.micro} detected")
        
        if version < (3, 8):
            self.log("Python 3.8+ required for Bielik CLI", "ERROR")
            return False
        
        if version >= (3, 12):
            self.log("Python 3.12+ detected - may need special handling for dependencies", "WARNING")
        
        return True
    
    def detect_package_managers(self):
        """Detect available package managers."""
        managers = {}
        
        # Check for conda/mamba
        for manager in ['conda', 'mamba', 'micromamba']:
            if shutil.which(manager):
                managers[manager] = shutil.which(manager)
                self.log(f"Found {manager}: {managers[manager]}", "SUCCESS")
        
        # Check for pip
        pip_cmd = 'pip3' if not self.is_windows else 'pip'
        if shutil.which(pip_cmd):
            managers['pip'] = pip_cmd
        elif shutil.which('pip'):
            managers['pip'] = 'pip'
            
        return managers
    
    def create_virtual_environment(self):
        """Create Python virtual environment."""
        if self.venv_dir.exists():
            self.log("Virtual environment already exists")
            return True
            
        try:
            self.log("Creating Python virtual environment...")
            self.run_command([self.python_exe, '-m', 'venv', str(self.venv_dir)])
            self.log("Virtual environment created successfully", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Failed to create virtual environment: {e}", "ERROR")
            return False
    
    def get_venv_python(self):
        """Get path to Python executable in virtual environment."""
        if self.is_windows:
            return str(self.venv_dir / 'Scripts' / 'python.exe')
        else:
            return str(self.venv_dir / 'bin' / 'python')
    
    def get_venv_pip(self):
        """Get path to pip in virtual environment."""
        if self.is_windows:
            return str(self.venv_dir / 'Scripts' / 'pip.exe')
        else:
            return str(self.venv_dir / 'bin' / 'pip')
    
    def install_basic_dependencies(self, use_conda=False):
        """Install basic dependencies without llama-cpp-python."""
        self.log("Installing basic dependencies...")
        
        if use_conda:
            return self.install_with_conda()
        else:
            return self.install_with_pip()
    
    def install_with_pip(self):
        """Install dependencies using pip."""
        try:
            pip_exe = self.get_venv_pip()
            
            # Upgrade pip first
            self.run_command([pip_exe, 'install', '--upgrade', 'pip'])
            
            # Install basic dependencies (without llama-cpp-python)
            basic_deps = [
                'fastapi>=0.88.0,<1.0.0',
                'uvicorn[standard]>=0.20.0,<1.0.0',
                'requests>=2.25.0,<3.0.0',
                'python-dotenv>=0.19.0,<2.0.0',
                'beautifulsoup4>=4.9.0,<5.0.0',
                'html2text>=2020.1.16,<2025.0.0',
                'python-magic>=0.4.24,<1.0.0',
                'pypdf>=3.0.0,<4.0.0',
                'python-docx>=0.8.11,<1.0.0',
                'huggingface_hub>=0.16.0,<1.0.0',
            ]
            
            for dep in basic_deps:
                self.log(f"Installing {dep}...")
                self.run_command([pip_exe, 'install', dep])
            
            self.log("Basic dependencies installed successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to install basic dependencies: {e}", "ERROR")
            return False
    
    def install_with_conda(self):
        """Install dependencies using conda."""
        try:
            managers = self.detect_package_managers()
            conda_exe = managers.get('mamba') or managers.get('conda')
            
            if not conda_exe:
                self.log("Conda/mamba not found", "ERROR")
                return False
            
            # Create conda environment
            env_name = f"bielik-{os.path.basename(self.project_dir)}"
            
            self.log(f"Creating conda environment: {env_name}")
            self.run_command([conda_exe, 'create', '-n', env_name, 'python>=3.8', '-y'])
            
            # Install dependencies
            conda_deps = [
                'fastapi', 'uvicorn', 'requests', 'beautifulsoup4', 
                'python-dotenv', 'huggingface_hub', 'pypdf2'
            ]
            
            self.run_command([conda_exe, 'install', '-n', env_name, '-c', 'conda-forge'] + conda_deps + ['-y'])
            
            self.log("Conda dependencies installed successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to install conda dependencies: {e}", "ERROR")
            return False
    
    def install_llama_cpp_python(self):
        """Try multiple strategies to install llama-cpp-python."""
        strategies = [
            self.try_prebuilt_wheels,
            self.try_conda_llama_cpp,
            self.try_older_version,
            self.try_cpu_only_build,
            self.try_alternative_compiler,
        ]
        
        for i, strategy in enumerate(strategies, 1):
            self.log(f"Strategy {i}/{len(strategies)}: {strategy.__name__}")
            try:
                if strategy():
                    self.log("llama-cpp-python installed successfully!", "SUCCESS")
                    return True
            except Exception as e:
                self.log(f"Strategy failed with exception: {e}", "WARNING")
            
            self.log(f"Strategy {strategy.__name__} failed, trying next...", "WARNING")
        
        self.log("All llama-cpp-python installation strategies failed", "WARNING")
        self.log("This is OK! Bielik Context Provider Commands will work perfectly without AI models", "INFO")
        self.log("You can still use: folder:, calc:, pdf: commands and all CLI features", "INFO")
        return False
    
    def try_prebuilt_wheels(self):
        """Try installing pre-built wheels."""
        try:
            pip_exe = self.get_venv_pip()
            
            # Try different wheel sources
            wheel_strategies = [
                ['llama-cpp-python', '--extra-index-url', 'https://abetlen.github.io/llama-cpp-python/whl/cpu'],
                ['llama-cpp-python', '--only-binary=:all:', '--no-cache-dir'],
                ['llama-cpp-python', '--prefer-binary', '--no-cache-dir'],
            ]
            
            for wheel_args in wheel_strategies:
                try:
                    self.run_command([pip_exe, 'install'] + wheel_args, check=False)
                    # Test if installation worked
                    test_result = self.run_command([self.get_venv_python(), '-c', 
                                                   'import llama_cpp; print("OK")'], check=False)
                    if test_result and test_result.returncode == 0:
                        return True
                except:
                    continue
                    
            return False
        except Exception as e:
            self.log(f"Pre-built wheels failed: {e}", "WARNING")
            return False
    
    def try_conda_llama_cpp(self):
        """Try installing llama-cpp-python via conda."""
        try:
            managers = self.detect_package_managers()
            conda_exe = managers.get('mamba') or managers.get('conda')
            
            if not conda_exe:
                return False
            
            self.run_command([conda_exe, 'install', '-c', 'conda-forge', 'llama-cpp-python', '-y'])
            return True
        except:
            return False
    
    def try_older_version(self):
        """Try installing older, more stable version."""
        try:
            pip_exe = self.get_venv_pip()
            
            old_versions = ['0.2.90', '0.2.85', '0.2.80']
            
            for version in old_versions:
                try:
                    self.run_command([pip_exe, 'install', f'llama-cpp-python=={version}', '--no-cache-dir'])
                    return True
                except:
                    continue
            
            return False
        except:
            return False
    
    def try_cpu_only_build(self):
        """Try CPU-only build with specific flags."""
        try:
            pip_exe = self.get_venv_pip()
            
            # Set CPU-only environment variables
            env = os.environ.copy()
            env['CMAKE_ARGS'] = '-DGGML_BLAS=OFF -DGGML_CUDA=OFF -DGGML_METAL=OFF'
            env['FORCE_CMAKE'] = '1'
            
            result = subprocess.run(
                [pip_exe, 'install', 'llama-cpp-python', '--no-cache-dir'],
                env=env,
                capture_output=True,
                text=True,
                cwd=self.project_dir
            )
            
            return result.returncode == 0
        except:
            return False
    
    def try_alternative_compiler(self):
        """Try with alternative compilers if available."""
        try:
            if not self.is_linux:
                return False
                
            # Check for newer GCC versions
            gcc_versions = ['gcc-12', 'gcc-13', 'clang']
            
            for compiler in gcc_versions:
                if shutil.which(compiler):
                    self.log(f"Trying with {compiler}")
                    
                    pip_exe = self.get_venv_pip()
                    env = os.environ.copy()
                    env['CC'] = compiler
                    env['CXX'] = compiler.replace('gcc', 'g++').replace('clang', 'clang++')
                    
                    try:
                        result = subprocess.run(
                            [pip_exe, 'install', 'llama-cpp-python', '--no-cache-dir'],
                            env=env,
                            capture_output=True,
                            text=True,
                            timeout=1800,  # 30 minutes max
                            cwd=self.project_dir
                        )
                        
                        if result.returncode == 0:
                            return True
                    except subprocess.TimeoutExpired:
                        self.log(f"Compilation with {compiler} timed out", "WARNING")
                    except:
                        continue
            
            return False
        except:
            return False
    
    def install_bielik_package(self):
        """Install Bielik package in development mode."""
        try:
            pip_exe = self.get_venv_pip()
            self.log("Installing Bielik CLI in development mode...")
            self.run_command([pip_exe, 'install', '-e', '.'])
            self.log("Bielik CLI installed successfully", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Failed to install Bielik CLI: {e}", "ERROR")
            return False
    
    def create_launcher_scripts(self):
        """Create platform-specific launcher scripts."""
        self.log("Creating launcher scripts...")
        
        # Universal Python launcher
        launcher_py = self.project_dir / 'run.py'
        launcher_py.write_text(self.get_python_launcher_content())
        
        if self.is_windows:
            # Windows batch file
            launcher_bat = self.project_dir / 'run.bat'
            launcher_bat.write_text(self.get_windows_launcher_content())
            self.log("Created run.bat for Windows", "SUCCESS")
        else:
            # Unix shell script
            launcher_sh = self.project_dir / 'run.sh'
            launcher_sh.write_text(self.get_unix_launcher_content())
            launcher_sh.chmod(0o755)
            self.log("Created run.sh for Unix/Linux/macOS", "SUCCESS")
        
        self.log("Created run.py universal launcher", "SUCCESS")
    
    def get_python_launcher_content(self):
        """Generate Python launcher script content."""
        return '''#!/usr/bin/env python3
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
        print("\\n👋 Bielik CLI interrupted by user")
    except Exception as e:
        print(f"❌ Error launching Bielik CLI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    def get_windows_launcher_content(self):
        """Generate Windows batch launcher."""
        return '''@echo off
REM Bielik CLI Windows Launcher

set "PROJECT_DIR=%~dp0"
set "VENV_PYTHON=%PROJECT_DIR%.venv\\Scripts\\python.exe"

if not exist "%VENV_PYTHON%" (
    echo ❌ Virtual environment not found. Please run install.py first.
    pause
    exit /b 1
)

"%VENV_PYTHON%" -m bielik.cli.main %*
'''
    
    def get_unix_launcher_content(self):
        """Generate Unix shell launcher."""
        return '''#!/bin/bash
# Bielik CLI Unix/Linux/macOS Launcher

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment not found. Please run install.py first."
    exit 1
fi

"$VENV_PYTHON" -m bielik.cli.main "$@"
'''
    
    def show_installation_summary(self, ai_installed=False):
        """Show installation summary and next steps."""
        self.log("\n" + "="*60, "SUCCESS")
        self.log("🎉 BIELIK CLI INSTALLATION COMPLETED!", "SUCCESS")
        self.log("="*60, "SUCCESS")
        
        self.log(f"✅ System: {platform.system()} {platform.release()}")
        self.log(f"✅ Python: {sys.version.split()[0]}")
        self.log(f"✅ Project directory: {self.project_dir}")
        self.log(f"✅ Virtual environment: {self.venv_dir}")
        self.log("✅ Bielik CLI with Context Provider Commands")
        
        if ai_installed:
            self.log("✅ AI models support (llama-cpp-python)", "SUCCESS")
        else:
            self.log("⚠️  AI models support disabled (llama-cpp-python not installed)", "WARNING")
            self.log("   Bielik CLI will work for Context Providers and direct commands")
        
        self.log("\n📋 NEXT STEPS:", "SUCCESS")
        
        if self.is_windows:
            self.log("   Windows users:")
            self.log("   • Double-click run.bat OR")
            self.log("   • python run.py OR")
            self.log("   • .venv\\Scripts\\python -m bielik.cli.main")
        else:
            self.log("   Unix/Linux/macOS users:")
            self.log("   • ./run.sh OR")
            self.log("   • python run.py OR")
            self.log("   • .venv/bin/python -m bielik.cli.main")
        
        self.log("\n🚀 TEST CONTEXT PROVIDER COMMANDS:")
        self.log("   • Run Bielik and try: folder: .")
        self.log("   • Check help with: :help")
        self.log("   • Calculator: :calc 2+3")
        
        if not ai_installed:
            self.log("\n💡 TO ENABLE AI MODELS:")
            self.log("   • Install manually: .venv/bin/pip install llama-cpp-python")
            self.log("   • Or try conda: conda install -c conda-forge llama-cpp-python")


def main():
    """Main installer entry point."""
    parser = argparse.ArgumentParser(description='Bielik CLI Universal Installer')
    parser.add_argument('--conda', action='store_true', 
                       help='Use conda/mamba instead of pip')
    parser.add_argument('--skip-ai', action='store_true',
                       help='Skip llama-cpp-python installation')
    parser.add_argument('--dev', action='store_true',
                       help='Development installation')
    
    args = parser.parse_args()
    
    installer = BielikInstaller()
    
    installer.log("🚀 BIELIK CLI MULTIPLATFORM INSTALLER", "SUCCESS")
    installer.log(f"Platform: {platform.system()} {platform.release()}")
    
    # Step 1: Validate Python
    if not installer.detect_python_version():
        sys.exit(1)
    
    # Step 2: Detect package managers
    managers = installer.detect_package_managers()
    installer.log(f"Available package managers: {list(managers.keys())}")
    
    # Step 3: Create virtual environment
    if not args.conda:
        if not installer.create_virtual_environment():
            sys.exit(1)
    
    # Step 4: Install basic dependencies
    if not installer.install_basic_dependencies(use_conda=args.conda):
        sys.exit(1)
    
    # Step 5: Install llama-cpp-python (optional)
    ai_installed = False
    if not args.skip_ai:
        ai_installed = installer.install_llama_cpp_python()
    else:
        installer.log("Skipping AI models installation (--skip-ai)", "WARNING")
    
    # Step 6: Install Bielik CLI
    if not args.conda:
        if not installer.install_bielik_package():
            sys.exit(1)
    
    # Step 7: Create launchers
    installer.create_launcher_scripts()
    
    # Step 8: Show summary
    installer.show_installation_summary(ai_installed)


if __name__ == '__main__':
    main()
