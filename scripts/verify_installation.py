#!/usr/bin/env python3
"""
Bielik Installation Verifier

This script verifies that Bielik and its dependencies are properly installed
using Conda and provides guidance for troubleshooting any issues.
"""

import sys
import subprocess
import json
import platform
from pathlib import Path

def run_command(cmd, capture_output=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=False,
            capture_output=capture_output,
            text=True
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout.strip() if result.stdout else '',
            'stderr': result.stderr.strip() if result.stderr else ''
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def check_conda():
    """Check if Conda is installed and accessible."""
    print("🔍 Checking Conda installation...")
    result = run_command("conda --version")
    
    if not result['success']:
        print("❌ Conda is not installed or not in PATH")
        print("   Please install Miniconda from: https://docs.conda.io/en/latest/miniconda.html")
        return False
    
    print(f"✅ Conda version: {result['stdout']}")
    return True

def check_environment():
    """Check if Bielik Conda environment exists."""
    print("\n🔍 Checking Conda environment...")
    result = run_command("conda env list --json")
    
    if not result['success']:
        print("❌ Failed to list Conda environments")
        return False
    
    try:
        envs = json.loads(result['stdout'])
        bielik_env = next((e for e in envs['envs'] if 'bielik' in str(e).lower()), None)
        
        if not bielik_env:
            print("❌ 'bielik' environment not found")
            print("   Create it with: conda env create -f environment.yml")
            return False
            
        print(f"✅ Found Bielik environment at: {bielik_env}")
        return True
        
    except Exception as e:
        print(f"❌ Error checking environments: {e}")
        return False

def check_python():
    """Check Python version and installation."""
    print("\n🔍 Checking Python installation...")
    
    # Check Python version in the environment
    result = run_command("python --version")
    if not result['success']:
        print("❌ Python is not accessible in the current environment")
        return False
    
    py_version = result['stdout']
    print(f"✅ {py_version}")
    
    # Check Python path
    result = run_command("which python" if platform.system() != "Windows" else "where python")
    if result['success']:
        print(f"   Python path: {result['stdout']}")
    
    return True

def check_dependencies():
    """Check if required dependencies are installed in conda bielik environment."""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        'llama-cpp-python',
        'transformers',
        'torch',
        'sentencepiece',
        'accelerate',
        'bitsandbytes',
        'huggingface-hub'
    ]
    
    # CPU optimization packages (optional but recommended for performance)
    cpu_optimization_packages = [
        'onnxruntime',
        'optimum', 
        'numpy',
        'numba',
        'numexpr'
    ]
    
    # Check if we're in conda bielik environment
    conda_env = run_command("conda info --envs | grep '*'")
    if conda_env['success'] and 'bielik' not in conda_env['stdout']:
        print("⚠️  Not running in conda 'bielik' environment!")
        print("   Checking dependencies using conda run...")
        
        # Use conda run to check dependencies in bielik environment
        all_ok = True
        for pkg in required_packages:
            result = run_command(f"conda run -n bielik python -c \"import {pkg}; print('OK')\"")
            if result['success'] and 'OK' in result['stdout']:
                print(f"✅ {pkg}: Installed in bielik environment")
            else:
                print(f"❌ {pkg}: Not found in bielik environment")
                all_ok = False
        
        # Check CPU optimization packages 
        print("\n🚀 Checking CPU optimization packages...")
        cpu_ok = 0
        for pkg in cpu_optimization_packages:
            result = run_command(f"conda run -n bielik python -c \"import {pkg}; print('OK')\"")
            if result['success'] and 'OK' in result['stdout']:
                print(f"✅ {pkg}: Installed (performance optimized)")
                cpu_ok += 1
            else:
                print(f"⚠️  {pkg}: Not found (performance may be slower)")
        
        print(f"\n🎯 CPU Optimization Status: {cpu_ok}/{len(cpu_optimization_packages)} packages installed")
        if cpu_ok < len(cpu_optimization_packages):
            print("💡 For better performance, run 'make install' to install all optimization packages")
        
        if not all_ok:
            print("\n🔧 Run these commands to fix dependencies:")
            print("   conda activate bielik")
            print("   conda env update -f environment.yml")
            print("   # or run: make install")
        
        return all_ok
    else:
        # Already in bielik environment, check normally
        all_ok = True
        for pkg in required_packages:
            result = run_command(f"python -c \"import {pkg}; print('OK')\"")
            if result['success'] and 'OK' in result['stdout']:
                print(f"✅ {pkg}: Installed")
            else:
                print(f"❌ {pkg}: Not found")
                all_ok = False
        
        return all_ok

def check_bielik():
    """Check if Bielik package is installed and importable."""
    print("\n🔍 Checking Bielik installation...")
    
    result = run_command("python -c \"import bielik; print('OK')\"")
    if result['success'] and 'OK' in result['stdout']:
        print("✅ Bielik package is properly installed")
        return True
    else:
        print("❌ Bielik package is not installed or not in PYTHONPATH")
        print("   Install with: pip install -e .")
        return False

def main():
    """Main verification function."""
    print("\n🦅 Bielik Installation Verifier")
    print("=" * 40)
    
    # Run all checks
    checks = [
        ("Conda", check_conda()),
        ("Environment", check_environment()),
        ("Python", check_python()),
        ("Dependencies", check_dependencies()),
        ("Bielik Package", check_bielik())
    ]
    
    # Print summary
    print("\n" + "=" * 40)
    print("📋 Verification Summary:")
    
    all_passed = True
    for name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✨ All checks passed! You're ready to use Bielik! 🚀")
        print("   Start with: bielik")
    else:
        print("\n⚠️  Some checks failed. Please review the messages above.")
        print("   Refer to the documentation for troubleshooting help.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
