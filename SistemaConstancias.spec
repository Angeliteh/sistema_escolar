# -*- mode: python ; coding: utf-8 -*-

"""
Archivo de configuración PyInstaller para Sistema de Constancias
Incluye todas las dependencias y recursos necesarios
"""

import os
from pathlib import Path

# Configuración de rutas
project_root = Path.cwd()
resources_path = project_root / "resources"

# Verificar que existen los recursos
print(f"🔍 Verificando recursos en: {resources_path}")
if resources_path.exists():
    print(f"✅ Recursos encontrados: {list(resources_path.iterdir())}")
else:
    print(f"❌ No se encontraron recursos en: {resources_path}")

# Datos adicionales (archivos que no son código Python)
datas = []

# Solo agregar recursos si existen
if resources_path.exists():
    datas.append((str(resources_path), "resources"))
    print(f"✅ Agregando recursos: {resources_path} → resources")

# Archivos de configuración
config_files = [
    ("school_config.json", "."),
    ("version.json", "."),
]

for src, dst in config_files:
    if Path(src).exists():
        datas.append((src, dst))
        print(f"✅ Agregando config: {src}")
    else:
        print(f"⚠️ Config no encontrado: {src}")

# Base de datos (si existe)
if Path("constancias.db").exists():
    datas.append(("constancias.db", "."))
    print("✅ Agregando base de datos")

print(f"📦 Total de archivos de datos: {len(datas)}")

# Filtrar elementos None
datas = [item for item in datas if item is not None]

# Módulos ocultos (que PyInstaller no detecta automáticamente)
hiddenimports = [
    # PyQt5 módulos
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'PyQt5.QtPrintSupport',
    
    # Gemini AI
    'google.generativeai',
    'google.ai.generativelanguage',
    
    # Otros módulos críticos
    'sqlite3',
    'json',
    'pathlib',
    'subprocess',
    'threading',
    'queue',
    'logging',
    'datetime',
    'uuid',
    'base64',
    'hashlib',
    'urllib.parse',
    'urllib.request',
    'requests',
    'fitz',  # PyMuPDF
    'pdfplumber',
    'PyPDF2',
    'PIL',  # Pillow
    'dotenv',
    
    # Módulos de la aplicación (CORREGIDOS)
    'app.core.ai.gemini_client',
    'app.core.ai.interpretation.master_interpreter',
    'app.core.ai.interpretation.student_interpreter',
    'app.core.ai.interpretation.help_interpreter',
    'app.core.database_manager',
    'app.core.pdf_generator',
    'app.ui.ai_chat.chat_window',
    'app.ui.menu_principal',
    'app.ui.buscar_ui',
    'app.ui.transformar_ui',
]

# Archivos binarios adicionales
binaries = []

# Análisis principal
a = Analysis(
    ['simple_launcher.py'],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Excluir módulos innecesarios para reducir tamaño
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
        'tensorflow',
        'torch',
        'pygame',  # Excluir pygame que aparece en los logs
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Recopilar archivos Python
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Crear ejecutable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='simple_launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(resources_path / "images" / "logos" / "logo_educacion.png") if (resources_path / "images" / "logos" / "logo_educacion.png").exists() else None,
)

# Crear directorio de distribución
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SistemaConstancias'
)
