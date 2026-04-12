# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for NW.js Automator GUI."""

import sys

block_cipher = None

a = Analysis(
    ['gui_interface.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('translations/*.json', 'translations'),
        ('translations/i18n.py', 'translations'),
        ('plugins/sample_plugin.py', 'plugins'),
        ('sample_batch.txt', '.'),
    ],
    hiddenimports=[
        'nwjs_automator',
        'batch_processor',
        'plugin_system',
        'translations.i18n',
        'requests',
        'psutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt6', 'tkinter', 'matplotlib', 'numpy'],
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
    name='NWjsAutomator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False if sys.platform in ('win32', 'darwin') else True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NWjsAutomator',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='NWjsAutomator.app',
        icon=None,
        bundle_identifier='dev.aeagis.nwjsautomator',
        info_plist={
            'CFBundleName': 'NW.js Automator',
            'CFBundleDisplayName': 'RPG Maker NW.js Automator',
            'CFBundleVersion': '2.2.0',
            'NSHighResolutionCapable': True,
        },
    )
