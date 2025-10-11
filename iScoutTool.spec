# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the directory containing this spec file
spec_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['iScoutTool.py'],
    pathex=[spec_dir],
    binaries=[],
    datas=[
        # Include UI files
        ('iScoutToolModern.ui', '.'),
        ('iScoutTool.ui', '.'),
        
        # Include Resources directory and contents
        ('Resources', 'Resources'),
        
        # Include config file if it exists
        ('iScoutTool.cfg', '.') if os.path.exists(os.path.join(spec_dir, 'iScoutTool.cfg')) else None,
        
        # Include generated UI Python files for backup
        ('iScoutToolModern_ui.py', '.'),
        ('iScoutTool_ui.py', '.'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtWidgets', 
        'PyQt5.QtGui',
        'PyQt5.uic',
        'ppadb.client',
        'ppadb.device',
        'xml.etree.ElementTree',
        'winsound',
        'configparser',
        'dataclasses',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'cv2',
    ],
    noarchive=False,
)

# Filter out None entries from datas
a.datas = [item for item in a.datas if item is not None]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='iScoutTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed app, True for console debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon='icon.ico' if you have an icon file
    version_info=None,  # Add version info if desired
)