# Installing Android SDK Platform Tools

## Overview
Android SDK Platform Tools contains ADB (Android Debug Bridge) which is required for iScoutTool to communicate with BlueStacks 5. This guide covers installation on Windows computers that don't have Android development tools installed.

## Method 1: Standalone Platform Tools (Recommended)

### Download Official Platform Tools
1. **Visit Google's Official Download Page**
   - URL: https://developer.android.com/studio/releases/platform-tools
   - This is the official Google source for platform tools

2. **Download Windows Version**
   - Click "Download SDK Platform-Tools for Windows"
   - File: `platform-tools_rXX.X.X-windows.zip` (~10MB)
   - No account required, direct download

3. **Extract and Install**
   ```powershell
   # Extract to a permanent location (example)
   # Extract to: C:\Android\platform-tools\
   
   # The folder should contain:
   # - adb.exe
   # - fastboot.exe
   # - Other ADB tools
   ```

4. **Add to System PATH**
   ```powershell
   # Option A: Using PowerShell (Run as Administrator)
   $oldPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
   $newPath = $oldPath + ";C:\Android\platform-tools"
   [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
   
   # Option B: Using GUI
   # 1. Windows key + R, type "sysdm.cpl"
   # 2. Advanced tab → Environment Variables
   # 3. System Variables → Path → Edit
   # 4. Add: C:\Android\platform-tools
   ```

5. **Verify Installation**
   ```cmd
   # Open new Command Prompt
   adb version
   # Should show: Android Debug Bridge version X.X.X
   
   adb devices
   # Should list connected devices (BlueStacks when running)
   ```

## Method 2: Through Android Studio (Full SDK)

### If Android Studio is Preferred
1. **Download Android Studio**
   - URL: https://developer.android.com/studio
   - Size: ~1GB download, ~3GB installed
   - Includes complete Android development environment

2. **Install with SDK**
   ```
   1. Run Android Studio installer
   2. Choose "Standard" installation
   3. Accept SDK license agreements
   4. Let installer download Android SDK
   5. SDK installs to: C:\Users\[Username]\AppData\Local\Android\Sdk
   ```

3. **Add SDK Tools to PATH**
   ```
   Add these folders to Windows PATH:
   C:\Users\[Username]\AppData\Local\Android\Sdk\platform-tools
   C:\Users\[Username]\AppData\Local\Android\Sdk\tools
   ```

## Method 3: Chocolatey Package Manager (Advanced)

### Using Chocolatey (if installed)
```powershell
# Install Chocolatey first (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install ADB via Chocolatey
choco install adb

# Verify installation
adb version
```

## Method 4: Scoop Package Manager (Alternative)

### Using Scoop (if preferred)
```powershell
# Install Scoop first (if not installed)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# Install ADB via Scoop
scoop install adb

# Verify installation
adb version
```

## BlueStacks 5 Integration

### Enable ADB in BlueStacks
```
1. Start BlueStacks 5
2. Click Settings (gear icon)
3. Go to Advanced tab
4. Enable "Android Debug Bridge (ADB)"
5. Restart BlueStacks if prompted
```

### Test Connection
```cmd
# Start BlueStacks first
# Open Command Prompt

adb devices
# Should show: 127.0.0.1:5555    device

# If not showing, try:
adb connect 127.0.0.1:5555
```

## Troubleshooting Installation

### Common Issues and Solutions

#### "adb is not recognized as a command"
```
Problem: ADB not in system PATH
Solutions:
1. Restart Command Prompt after PATH changes
2. Verify PATH includes platform-tools folder
3. Use full path: C:\Android\platform-tools\adb.exe
```

#### "ADB server didn't ACK"
```
Problem: ADB server issues
Solutions:
1. adb kill-server
2. adb start-server
3. Restart BlueStacks
4. Check Windows Firewall settings
```

#### "Device offline" or "unauthorized"
```
Problem: BlueStacks ADB not properly enabled
Solutions:
1. Re-enable ADB in BlueStacks settings
2. Restart BlueStacks completely
3. Try: adb disconnect then adb connect 127.0.0.1:5555
```

#### Antivirus blocking ADB
```
Problem: Security software interference
Solutions:
1. Add ADB folder to antivirus exceptions
2. Add BlueStacks folder to exceptions
3. Temporarily disable real-time protection for testing
```

## Verification Checklist

### Complete Installation Test
```cmd
# 1. Check ADB version
adb version

# 2. Check if BlueStacks is detected
adb devices

# 3. Test communication with BlueStacks
adb shell echo "Connection successful"

# 4. Check screen size (should work if Evony is running)
adb shell wm size
```

### Expected Results
```
> adb version
Android Debug Bridge version 1.0.41
Version 34.0.5-10900879

> adb devices
List of devices attached
127.0.0.1:5555    device

> adb shell echo "Connection successful"
Connection successful

> adb shell wm size
Physical size: 1920x1080
```

## Alternative: Portable ADB

### For Computers Without Admin Rights
```
1. Download platform-tools zip
2. Extract to user folder (e.g., Documents\Android\platform-tools)
3. Don't add to system PATH
4. Use full path in iScoutTool if needed
5. Or create batch file to run with ADB in PATH
```

### Portable Batch Script
```batch
@echo off
REM portable_adb.bat
SET PATH=%~dp0platform-tools;%PATH%
cmd /k "echo ADB is now available in this command prompt"
```

## Security Considerations

### Windows Firewall
```
ADB uses network connection to BlueStacks:
- Port: 5037 (ADB server)
- Port: 5555 (BlueStacks ADB)
- Connection: localhost only (127.0.0.1)
- No external network access required
```

### Antivirus Exceptions
```
Add these folders to antivirus exceptions:
- C:\Android\platform-tools\ (or wherever you installed)
- BlueStacks installation folder
- iScoutTool.exe location
```

## Quick Installation Summary

### Fastest Method for Most Users:
1. **Download**: https://developer.android.com/studio/releases/platform-tools
2. **Extract** to: `C:\Android\platform-tools\`
3. **Add to PATH**: Windows Settings → System → Advanced → Environment Variables
4. **Test**: Open new Command Prompt → `adb version`
5. **Enable ADB** in BlueStacks Settings → Advanced
6. **Verify**: `adb devices` shows BlueStacks connection

### Total Time: ~5-10 minutes
### Disk Space: ~15MB for platform tools only
### Internet Required: Only for initial download

---

This installation provides the ADB functionality that iScoutTool needs to communicate with BlueStacks 5 for automated Evony game interactions.