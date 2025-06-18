@echo off
title RPG Maker MV NW.js Automator
color 0A

echo.
echo ==========================================
echo   RPG Maker MV NW.js Automation Tool
echo ==========================================
echo.
echo This tool will help you optimize your RPG Maker games
echo by replacing the built-in runtime with NW.js
echo.
echo Benefits:
echo  * Save 120MB+ per game
echo  * Enable Developer Tools (F12)
echo  * Better performance and compatibility
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    echo After installing Python, restart this script.
    echo.
    pause
    exit /b 1
)

echo Python found and ready!

REM Check if requests module is installed
echo Checking dependencies...
python -c "import requests" 2>nul
if errorlevel 1 (
    echo Installing required dependencies...
    python -m pip install requests
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        echo This might be due to:
        echo  - No internet connection
        echo  - Insufficient permissions
        echo  - Python/pip not properly installed
        echo.
        echo Please try running as administrator or install manually:
        echo pip install requests
        echo.
        pause
        exit /b 1
    )
    echo Dependencies installed successfully!
) else (
    echo All dependencies are already installed!
)

REM Change to script directory
cd /d "%~dp0"

REM Check if nwjs_automator.py exists
if not exist "nwjs_automator.py" (
    echo.
    echo ERROR: nwjs_automator.py not found in current directory
    echo Please ensure all script files are in the same folder
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo.
echo Starting NW.js Automator...
echo.

REM Run the Python script
python "nwjs_automator.py"
set PYTHON_EXIT_CODE=%errorlevel%

echo.
if %PYTHON_EXIT_CODE% equ 0 (
    echo Script completed successfully!
) else (
    echo Script encountered an error ^(exit code: %PYTHON_EXIT_CODE%^)
    echo Check the output above for details.
)

echo.
echo Press any key to exit...
pause >nul