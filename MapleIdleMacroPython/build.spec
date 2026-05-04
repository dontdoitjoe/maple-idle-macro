# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Maple Idle Macro.
Build with: pyinstaller build.spec
"""

import os

block_cipher = None

hiddenimports = [
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.sip',
    'numpy',
    'numpy.core',
    'numpy.core.multiarray',
    'PIL',
    'PIL.Image',
    'pyautogui',
    'Quartz',
    'Quartz.CoreGraphics',
    'AppKit',
    'objc',
    'Foundation',
    'src.services.adb_service',
    'src.services.input_backend',
]

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[
        ('resources', 'resources'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # pyautogui -> pyscreeze optionally imports cv2; we do not use image matching — exclude to keep the .app small.
    excludes=['cv2'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MapleIdleMacro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MapleIdleMacro',
)

app = BUNDLE(
    coll,
    name='MapleIdleMacro.app',
    icon=None,
    bundle_identifier='com.mapleidlemacro.app',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDocumentTypes': [],
        'LSMinimumSystemVersion': '13.0',
        'CFBundleDisplayName': 'Maple Idle Macro',
        'CFBundleName': 'Maple Idle Macro',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'LSApplicationCategoryType': 'public.app-category.utilities',
        'NSHumanReadableCopyright': 'For personal use only.',
        'NSAccessibilityUsageDescription': (
            'Maple Idle Macro needs Accessibility permission to automate mouse clicks '
            'and keyboard keys for Maple Idle in BlueStacks.'
        ),
        'NSAppleEventsUsageDescription': (
            'Maple Idle Macro may use AppleScript to bring BlueStacks to the front '
            'before sending input.'
        ),
    },
)
