@echo off
REM Bielik CLI Installation Script for Windows
REM Universal installer with automatic dependency detection

setlocal EnableDelayedExpansion

set "PROJECT_DIR=%~dp0"
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

echo.
echo ======================================================
echo 🚀 Bielik CLI Universal Installer for Windows
echo ======================================================
echo Project directory: %PROJECT_DIR%
echo.

REM Check if Python is available
call :check_python
if errorlevel 1 exit /b 1

REM Try Python installer first
if exist "%PROJECT_DIR%\install.py" (
    echo [INFO] Found Python installer, delegating to install.py...
    
    REM Parse command line arguments
    set "ARGS="
    :parse_args
    if "%~1"=="" goto end_parse
    if "%~1"=="--conda" set "ARGS=%ARGS% --conda"
    if "%~1"=="--skip-ai" set "ARGS=%ARGS% --skip-ai"
    if "%~1"=="--dev" set "ARGS=%ARGS% --dev"
    if "%~1"=="--help" goto show_help
    if "%~1"=="-h" goto show_help
    shift
    goto parse_args
    
    :end_parse
    REM Run Python installer
    "%PYTHON_CMD%" "%PROJECT_DIR%\install.py" %ARGS%
    if errorlevel 1 (
        echo [ERROR] Python installer failed, trying fallback...
        call :install_with_batch
    )
) else (
    echo [WARNING] install.py not found, using batch-based installation
    call :install_with_batch
)

call :create_launcher
call :show_summary
goto :eof

:show_help
echo Bielik CLI Installation Script for Windows
echo.
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   --conda      Use conda/mamba instead of pip
echo   --skip-ai    Skip llama-cpp-python installation
echo   --dev        Development installation
echo   --help, -h   Show this help message
exit /b 0

REM Function to check Python installation
:check_python
echo [INFO] Checking Python installation...

for %%p in (python py python3) do (
    %%p --version >nul 2>&1
    if not errorlevel 1 (
        for /f "tokens=2" %%v in ('%%p --version 2^>^&1') do (
            set "PYTHON_VERSION=%%v"
            set "PYTHON_CMD=%%p"
        )
        
        REM Check version (simple check for 3.x)
        echo !PYTHON_VERSION! | findstr /r "^3\.[89]" >nul
        if not errorlevel 1 (
            echo [SUCCESS] Found Python !PYTHON_VERSION! at %%p
            goto :eof
        )
        
        echo !PYTHON_VERSION! | findstr /r "^3\.1[0-9]" >nul
        if not errorlevel 1 (
            echo [SUCCESS] Found Python !PYTHON_VERSION! at %%p
            goto :eof
        )
        
        echo [WARNING] Python !PYTHON_VERSION! is too old (need 3.8+)
    )
)

echo [ERROR] Python 3.8+ not found. Please install Python 3.8 or newer.
echo.
echo Installation instructions:
echo • Download from: https://www.python.org/downloads/
echo • Make sure to check "Add Python to PATH" during installation
echo • Or use Microsoft Store: search for "Python"
echo • Or use Chocolatey: choco install python
exit /b 1

REM Fallback batch installation
:install_with_batch
echo [INFO] Performing batch-based installation...

set "VENV_DIR=%PROJECT_DIR%\.venv"

if exist "%VENV_DIR%" (
    echo [INFO] Virtual environment already exists
) else (
    echo [INFO] Creating virtual environment...
    "%PYTHON_CMD%" -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created
)

REM Activate virtual environment
call "%VENV_DIR%\Scripts\activate.bat"

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Install basic dependencies
echo [INFO] Installing basic dependencies...

python -m pip install "fastapi>=0.88.0,<1.0.0" ^
                      "uvicorn[standard]>=0.20.0,<1.0.0" ^
                      "requests>=2.25.0,<3.0.0" ^
                      "python-dotenv>=0.19.0,<2.0.0" ^
                      "beautifulsoup4>=4.9.0,<5.0.0" ^
                      "html2text>=2020.1.16,<2025.0.0" ^
                      "python-magic>=0.4.24,<1.0.0" ^
                      "pypdf>=3.0.0,<4.0.0" ^
                      "python-docx>=0.8.11,<1.0.0" ^
                      "huggingface_hub>=0.16.0,<1.0.0"

if errorlevel 1 (
    echo [ERROR] Failed to install basic dependencies
    exit /b 1
)

echo [SUCCESS] Basic dependencies installed

REM Try to install llama-cpp-python (optional)
echo %* | findstr /c:"--skip-ai" >nul
if errorlevel 1 (
    echo [INFO] Attempting to install llama-cpp-python...
    
    REM Try multiple strategies
    python -m pip install llama-cpp-python --no-cache-dir
    if errorlevel 1 (
        echo [INFO] Trying with pre-built wheels...
        python -m pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
        if errorlevel 1 (
            REM Check if conda is available
            conda --version >nul 2>&1
            if not errorlevel 1 (
                echo [INFO] Trying conda installation...
                conda install -c conda-forge llama-cpp-python -y
                if not errorlevel 1 (
                    echo [SUCCESS] llama-cpp-python installed via conda
                ) else (
                    echo [WARNING] Failed to install llama-cpp-python, continuing without AI support
                )
            ) else (
                echo [WARNING] Failed to install llama-cpp-python, continuing without AI support
            )
        ) else (
            echo [SUCCESS] llama-cpp-python installed via pre-built wheels
        )
    ) else (
        echo [SUCCESS] llama-cpp-python installed successfully
    )
) else (
    echo [INFO] Skipping AI model support (--skip-ai)
)

REM Install Bielik in development mode
echo [INFO] Installing Bielik CLI...
python -m pip install -e .
if errorlevel 1 (
    echo [ERROR] Failed to install Bielik CLI
    exit /b 1
)
echo [SUCCESS] Bielik CLI installed

REM Deactivate virtual environment
call deactivate
goto :eof

REM Create launcher script
:create_launcher
set "LAUNCHER=%PROJECT_DIR%\run.bat"

(
echo @echo off
echo REM Bielik CLI Launcher for Windows
echo.
echo set "PROJECT_DIR=%%~dp0"
echo set "PROJECT_DIR=%%PROJECT_DIR:~0,-1%%"
echo set "VENV_PYTHON=%%PROJECT_DIR%%\.venv\Scripts\python.exe"
echo.
echo if not exist "%%VENV_PYTHON%%" ^(
echo     echo ❌ Virtual environment not found. Please run install.bat first.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo "%%VENV_PYTHON%%" -m bielik.cli.main %%*
) > "%LAUNCHER%"

echo [SUCCESS] Created launcher script: run.bat
goto :eof

REM Show installation summary
:show_summary
echo.
echo ================================================================
echo [SUCCESS] 🎉 BIELIK CLI INSTALLATION COMPLETED!
echo ================================================================
echo.
echo [SUCCESS] ✅ System: Windows
echo [SUCCESS] ✅ Python: %PYTHON_VERSION%
echo [SUCCESS] ✅ Project: %PROJECT_DIR%
echo [SUCCESS] ✅ Virtual Environment: %PROJECT_DIR%\.venv
echo [SUCCESS] ✅ Bielik CLI with Context Provider Commands
echo.
echo [INFO] 📋 NEXT STEPS:
echo    • Launch: run.bat
echo    • Or: python run.py
echo    • Or: .venv\Scripts\python -m bielik.cli.main
echo.
echo [INFO] 🚀 TEST CONTEXT PROVIDER COMMANDS:
echo    • Try: folder: .
echo    • Help: :help
echo    • Calculator: :calc 2+3
echo.
echo 🔗 For more info: https://github.com/tom-sapletta-com/bielik
echo.
pause
goto :eof
