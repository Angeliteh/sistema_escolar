# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Lista de archivos y carpetas a incluir
added_files = [
    ('plantillas', 'plantillas'),
    ('logos', 'logos'),
    ('alumnos.db', '.'),  # Incluir la base de datos si existe
]

# Asegurarse de que los directorios necesarios existan
import os
os.makedirs('plantillas', exist_ok=True)
os.makedirs('logos', exist_ok=True)
os.makedirs('fotos', exist_ok=True)
os.makedirs('salidas', exist_ok=True)

a = Analysis(
    ['main_qt.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.QtPrintSupport',
        'jinja2',
        'pdfplumber',
        'PyPDF2',
        'PIL',
        'sqlite3',
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

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ConstanciasEscolares',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola (aplicación de ventana)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logos/logo_educacion.ico',  # Asegúrate de tener este archivo o cámbialo
)
