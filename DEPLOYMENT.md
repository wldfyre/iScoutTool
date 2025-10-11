# iScoutTool Deployment Guide

## Building the Executable

### Prerequisites
1. Python 3.8+ installed on build machine
2. All dependencies installed: `pip install -r requirements.txt`
3. PyInstaller installed: `pip install pyinstaller`

### Build Steps

#### Option 1: Use the Build Script (Recommended)
```bash
# Run the automated build script
build_executable.bat
```

#### Option 2: Manual Build
```bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Generate UI files
python -m PyQt5.uic.pyuic -x iScoutToolModern.ui -o iScoutToolModern_ui.py

# Clean previous builds
rmdir /s /q build dist __pycache__

# Build using spec file
pyinstaller iScoutTool.spec --clean --noconfirm
```

### Build Output
- **Executable**: `dist/iScoutTool.exe`
- **Supporting Files**: All included in `dist/` folder
- **Size**: Approximately 40-60 MB (includes Python runtime and PyQt5)

## Deployment to Target Computer

### Target Computer Requirements
- **Operating System**: Windows 10/11 (64-bit recommended)
- **BlueStacks 5**: Must be installed and configured
- **ADB Debugging**: Must be enabled in BlueStacks settings
- **No Python Required**: Executable is completely standalone

### Deployment Steps

1. **Copy Files**
   ```
   Copy the entire 'dist' folder to the target computer
   Rename to 'iScoutTool' for cleaner appearance
   ```

2. **Install Android SDK Platform Tools**
   - **Required for ADB communication with BlueStacks**
   - See detailed guide: `ANDROID_SDK_INSTALLATION.md`
   - Quick method: Download from https://developer.android.com/studio/releases/platform-tools
   - Extract and add to Windows PATH

3. **BlueStacks Setup**
   - Install BlueStacks 5 from bluestacks.com
   - Install Evony game in BlueStacks
   - Enable Advanced Settings > Android Debug Bridge (ADB)
   - Start BlueStacks and verify ADB connection

4. **Verify Installation**
   ```
   Run: adb devices
   Should show: 127.0.0.1:5555 device
   ```

5. **Launch Application**
   - Double-click `iScoutTool.exe`
   - Application should start with modern dark theme UI
   - Test ADB connection using "Test Connection" menu option

### Troubleshooting Deployment

#### Common Issues

**1. "Missing DLL" errors**
- Ensure Microsoft Visual C++ Redistributables are installed
- Download from Microsoft website if needed

**2. "ADB Connection Failed"**
- Verify BlueStacks 5 is running
- Check ADB debugging is enabled
- Restart BlueStacks if needed
- Run `adb devices` in command prompt to verify

**3. "Application won't start"**
- Check antivirus hasn't quarantined the executable
- Run as Administrator if needed
- Check Windows Event Viewer for detailed errors

**4. UI elements missing/broken**
- Ensure all files in dist folder are copied together
- Don't separate the executable from supporting files
- Verify Resources/locations.xml exists

#### Configuration Files
- **locations.xml**: Must be in Resources/ subfolder
- **iScoutTool.cfg**: Created automatically on first run
- **UI files**: Embedded in executable, no external files needed

### File Structure on Target Computer
```
iScoutTool/
├── iScoutTool.exe              # Main executable
├── Resources/
│   └── locations.xml           # Screen coordinate presets
├── iScoutTool.cfg             # User configuration (auto-created)
└── [Various PyQt5/Python DLLs and supporting files]
```

### Performance Notes
- **Startup Time**: 3-5 seconds (first launch may be slower)
- **Memory Usage**: ~50-80 MB RAM
- **Disk Space**: ~60-80 MB total
- **CPU Usage**: Minimal during operation, spikes during ADB commands

### Security Considerations
- Executable may trigger antivirus warnings (false positive)
- Add exception for iScoutTool.exe if needed
- Application only connects to localhost (BlueStacks ADB)
- No network communication outside of ADB

### Updates and Maintenance
- Rebuild executable for code updates
- Replace entire dist folder for updates
- User settings in iScoutTool.cfg are preserved
- locations.xml updates require new Resources folder

### Testing Checklist
Before deploying, verify:
- [ ] Executable starts without errors
- [ ] BlueStacks connection works
- [ ] Timer functionality operates correctly
- [ ] Navigation buttons function properly
- [ ] Target loading and processing works
- [ ] Configuration saves and loads correctly
- [ ] All UI elements display properly

### Support Information
- **Build Date**: Generated automatically during build
- **Python Version**: Embedded runtime version
- **Dependencies**: PyQt5, ppadb (embedded)
- **Target Platform**: Windows x64