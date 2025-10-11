@echo off
REM Build script for iScoutTool executable
REM This script creates a standalone executable using PyInstaller

echo ===============================================
echo Building iScoutTool Standalone Executable
echo ===============================================

REM Change to the script directory
cd /d "%~dp0"

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Error: PyInstaller is not installed!
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller!
        pause
        exit /b 1
    )
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"

REM Generate the UI file if needed
echo Generating UI files...
python -m PyQt5.uic.pyuic -x iScoutToolModern.ui -o iScoutToolModern_ui.py

REM Build the executable using the spec file
echo Building executable...
pyinstaller iScoutTool.spec --clean --noconfirm

REM Check if build was successful
if exist "dist\iScoutTool.exe" (
    echo.
    echo ===============================================
    echo BUILD SUCCESSFUL!
    echo ===============================================
    echo.
    echo Executable created: dist\iScoutTool.exe
    echo.
    echo To deploy to another computer:
    echo 1. Copy the entire 'dist' folder to the target computer
    echo 2. Install BlueStacks 5 and enable ADB debugging
    echo 3. Run iScoutTool.exe from the dist folder
    echo.
    echo Opening dist folder...
    explorer "dist"
) else (
    echo.
    echo ===============================================
    echo BUILD FAILED!
    echo ===============================================
    echo.
    echo Check the output above for error messages.
    echo Common issues:
    echo - Missing dependencies (run: pip install -r requirements.txt)
    echo - Missing UI files (ensure .ui files exist)
    echo - Antivirus interference (temporarily disable)
)

echo.
pause