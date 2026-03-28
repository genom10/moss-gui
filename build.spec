# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# Collect all app data files (only if they exist)
app_data = [('app', 'app')]

# Add optional data files if they exist
for data_file in ['moss_config.json', 'download_config.json', 'students_aliases.csv', 'requirements.txt']:
    if os.path.exists(data_file):
        app_data.append((data_file, data_file))

# Create aliases directory if it doesn't exist (it's gitignored)
if not os.path.exists('aliases'):
    os.makedirs('aliases', exist_ok=True)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=app_data,
    hiddenimports=[
        'customtkinter',
        'PIL',
        'requests',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'pages.download_page',
        'pages.aliases_page',
        'pages.grading_page',
        'pages.analysis_page',
        'components.data_table',
        'components.form_inputs',
        'utils.codeforces_api',
        'utils.csv_handler',
        'utils.moss_runner',
        'scripts.getLastSubmission',
        'scripts.pull',
        'scripts.pullSubmissions',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MOSS-Grading',
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
    icon=None,
)
