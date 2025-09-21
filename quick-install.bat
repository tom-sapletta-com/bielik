@echo off
REM Bielik CLI One-liner Installer for Windows
REM Usage: Download and run, or use PowerShell one-liner

setlocal EnableDelayedExpansion

echo.
echo ======================================
echo 🚀 Bielik CLI Quick Installer for Windows
echo ======================================

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ git not found. Please install git first.
    echo    Download from: https://git-scm.com/download/win
    echo    Or use winget: winget install Git.Git
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Python not found. Please install Python 3.8+ first.
        echo    Download from: https://www.python.org/downloads/
        echo    Or use Microsoft Store: search for "Python"
        echo    Or use winget: winget install Python.Python.3
        pause
        exit /b 1
    ) else (
        set "PYTHON_CMD=py"
    )
) else (
    set "PYTHON_CMD=python"
)

REM Set installation directory
set "INSTALL_DIR=%USERPROFILE%\bielik"

REM Clone or update repository
if exist "%INSTALL_DIR%" (
    echo 📂 Found existing installation at %INSTALL_DIR%
    cd /d "%INSTALL_DIR%"
    git pull origin main
) else (
    echo 📥 Cloning Bielik repository...
    git clone https://github.com/tom-sapletta-com/bielik.git "%INSTALL_DIR%"
    cd /d "%INSTALL_DIR%"
)

REM Run installer
echo 🔧 Running installer...
"%PYTHON_CMD%" install.py --skip-ai

REM Test installation
echo 🧪 Testing installation...
"%PYTHON_CMD%" run.py --info >nul 2>&1
if errorlevel 1 (
    echo ❌ Installation test failed
    echo 💡 Try manual installation:
    echo    cd "%INSTALL_DIR%"
    echo    %PYTHON_CMD% install.py --help
    pause
    exit /b 1
)

echo ✅ Installation successful!
echo.
echo ======================================
echo 🎉 BIELIK CLI READY TO USE!
echo ======================================
echo 📂 Installation directory: %INSTALL_DIR%
echo.
echo 🚀 Quick Start:
echo    cd "%INSTALL_DIR%"
echo    python run.py
echo    REM or
echo    run.bat
echo.
echo 📊 Try Context Provider Commands:
echo    folder: .
echo    calc: 2+3*4
echo    :help
echo.
echo 🔗 Create desktop shortcut (optional):
echo    Right-click run.bat ^> Send to ^> Desktop (create shortcut)
echo.
pause
