@echo off
echo Starting iScoutTool - Evony Automation Application
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import PyQt5, ppadb" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if UI file exists
if not exist "iScoutToolModern.ui" (
    echo ERROR: iScoutToolModern.ui file not found
    echo Please ensure all required files are in the same directory
    pause
    exit /b 1
)

REM Create Resources directory if it doesn't exist
if not exist "Resources" mkdir Resources

REM Launch the application
echo Starting iScoutTool...
python iScoutTool.py

REM Keep window open if there's an error
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error code: %errorlevel%
    pause
)