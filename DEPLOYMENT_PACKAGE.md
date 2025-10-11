# iScoutTool Standalone Executable - Deployment Package

## 📦 What's Included

- **iScoutTool.exe** (38MB) - Complete standalone application
- **All resources embedded** - No external files needed
- **Python runtime included** - Target computer needs NO Python installation
- **PyQt5 GUI framework included** - All UI components embedded

## 🎯 Target Computer Requirements

### Minimum System Requirements
- **Operating System**: Windows 10 (64-bit) or Windows 11
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 100MB free space
- **Dependencies**: None (all included in executable)

### Required Software
1. **Android SDK Platform Tools** - For ADB communication
   - Download: https://developer.android.com/studio/releases/platform-tools
   - See: `ANDROID_SDK_INSTALLATION.md` for detailed instructions
   - Must be installed and in system PATH
2. **BlueStacks 5** - Android emulator
   - Download: https://www.bluestacks.com/
   - Must enable ADB debugging in settings
3. **Evony Game** - Installed in BlueStacks
4. **Microsoft Visual C++ Redistributables** (usually already installed)

## 🚀 Quick Deployment Steps

### 1. Copy to Target Computer
```
1. Copy iScoutTool.exe to target computer
2. Place in any folder (e.g., C:\iScoutTool\)
3. No installation required - just copy and run!
```

### 2. Install Android SDK Platform Tools
```
1. Download from: https://developer.android.com/studio/releases/platform-tools  
2. Extract to folder (e.g., C:\Android\platform-tools\)
3. Add folder to Windows PATH environment variable
4. Test: Open new Command Prompt, type "adb version"
```

### 3. BlueStacks Setup
```
1. Install BlueStacks 5
2. Install Evony game in BlueStacks
3. Enable Settings > Advanced > Android Debug Bridge (ADB)
4. Start BlueStacks and verify it's running
```

### 4. Verify ADB Connection
```
1. Open Command Prompt (Windows key + R, type "cmd")
2. Type: adb devices
3. Should show: 127.0.0.1:5555    device
4. If not working, restart BlueStacks
```

### 5. Launch iScoutTool
```
1. Double-click iScoutTool.exe
2. Application should start with dark theme interface
3. Green indicator should show "🟢 Emulator Connected"
4. If red, check BlueStacks is running and ADB is enabled
```

## 🔧 Troubleshooting

### Application Won't Start
- **Antivirus blocking**: Add iScoutTool.exe to antivirus exceptions
- **Missing VC++ redistributables**: Download from Microsoft
- **Run as Administrator**: Right-click → "Run as administrator"

### ADB Connection Issues  
- **BlueStacks not running**: Start BlueStacks 5
- **ADB not enabled**: BlueStacks Settings > Advanced > Enable ADB
- **Port conflict**: Restart BlueStacks
- **Firewall blocking**: Allow BlueStacks and iScoutTool through Windows Firewall

### UI/Display Problems
- **Dark theme issues**: Update graphics drivers
- **Text not visible**: Windows display scaling set too high
- **Buttons not working**: Ensure mouse/touchpad drivers are current

## 📋 Feature Verification Checklist

After deployment, test these features:
- [ ] Application starts without errors
- [ ] Connection indicator shows green "Emulator Connected"
- [ ] Can paste scout data into text area
- [ ] "Load Targets" button populates the table
- [ ] Timer shows "05:00" in cyan color
- [ ] "Reset Timer" button works (resets to 05:00)
- [ ] Navigation buttons ("Go to Enemy", "Go Home") function
- [ ] Configuration settings can be entered and saved

## 💾 User Data and Settings

### Configuration Storage
- **Settings file**: `iScoutTool.cfg` (auto-created in same folder as .exe)
- **Preset locations**: Embedded in executable (Resources/locations.xml)
- **User data**: No persistent storage (session-based only)

### Backup/Migration
- **Settings backup**: Copy `iScoutTool.cfg` file
- **No other files needed**: All resources embedded in executable

## 🔄 Updates and Maintenance

### Updating the Application
1. **Replace executable**: Simply copy new iScoutTool.exe over old one
2. **Preserve settings**: Keep existing iScoutTool.cfg file
3. **No uninstall needed**: Delete old executable to remove

### Version Information
- **Build Date**: October 10, 2025
- **Python Version**: 3.13.3 (embedded)
- **PyQt5 Version**: Latest (embedded)
- **Executable Size**: ~38MB
- **Architecture**: Windows x64

## 📞 Support Information

### Log Files
- **Application logs**: Check console output if run from command prompt
- **ADB logs**: Use `adb logcat` for Android-side debugging
- **Windows logs**: Event Viewer > Windows Logs > Application

### Common File Locations
```
Application: C:\[YourFolder]\iScoutTool.exe
Settings: C:\[YourFolder]\iScoutTool.cfg
BlueStacks: C:\Program Files\BlueStacks_nxt\
ADB: Usually in BlueStacks installation folder
```

### Performance Expectations
- **Startup time**: 3-5 seconds
- **Memory usage**: 50-80MB RAM
- **Navigation speed**: ~0.5 seconds per coordinate
- **CPU usage**: Low (spikes during ADB commands)

---

## ✅ Deployment Success!

Your iScoutTool is now ready for standalone deployment. The single executable file contains everything needed to run the application on any compatible Windows computer with BlueStacks 5 installed.

**No Python, PyQt5, or additional dependencies required on target computer!**