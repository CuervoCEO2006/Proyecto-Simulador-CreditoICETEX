# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_dynamic_libs

datas = []
binaries = []
datas += collect_data_files('kivy')
binaries += collect_dynamic_libs('kivy')


a = Analysis(
    ['../main_gui.py'],
    pathex=['src'],
    binaries=binaries,
    datas=datas,
    hiddenimports=['kivy', 'kivy.app', 'kivy.clock', 'kivy.core.window', 'kivy.core.window.window_sdl2', 'kivy.uix.boxlayout', 'kivy.uix.button', 'kivy.uix.label', 'kivy.uix.textinput'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CreditoICETEXNuevo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
