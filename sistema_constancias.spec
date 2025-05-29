# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Configuración del ejecutable
block_cipher = None

# Datos adicionales a incluir
added_files = [
    # Archivos de configuración CRÍTICOS
    ('school_config.json', '.'),
    ('version.json', '.'),
    ('.env', '.'),

    # Base de datos
    ('resources/data/alumnos.db', 'resources/data'),

    # Plantillas HTML
    ('resources/templates', 'resources/templates'),

    # Imágenes y logos
    ('resources/images', 'resources/images'),

    # Todo el directorio de recursos
    ('resources', 'resources'),

    # Directorio completo de la aplicación
    ('app', 'app'),
]

# Módulos ocultos que PyInstaller no detecta automáticamente
hidden_imports = [
    # PyQt5 módulos
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt5.QtPrintSupport',
    'PyQt5.QtWebEngineWidgets',

    # Módulos del sistema (MIGRADOS)
    'app.core.system_detector',
    'app.core.environment_detector',
    'app.core.executable_paths',  # NUEVO: gestor de rutas dinámicas
    'app.core.logging.logger_manager',
    'app.core.school_config',
    'app.core.database_manager',
    'app.core.chat_engine',
    'app.core.setup_wizard',
    'app.core.pdf_generator',
    'app.core.pdf_extractor',
    'app.core.config',
    'app.core.utils',

    # Servicios (MIGRADOS)
    'app.services.alumno_service',
    'app.services.constancia_service',
    'app.services.pdf_service',

    # Repositorios
    'app.data.repositories.alumno_repository',
    'app.data.repositories.constancia_repository',
    'app.data.repositories.datos_escolares_repository',

    # Modelos
    'app.data.models.alumno',
    'app.data.models.constancia',
    'app.data.models.datos_escolares',

    # UI módulos
    'app.ui.menu_principal',
    'app.ui.ai_chat.chat_window',
    'app.ui.ai_chat.chat_interface',
    'app.ui.ai_chat.message_widget',
    'app.ui.database_admin_ui',

    # Otros módulos críticos
    'sqlite3',
    'json',
    'datetime',
    'pathlib',
    'tempfile',
    'zipfile',
    'hashlib',
    'base64',
    'urllib.parse',
    'urllib.request',
    'logging',
    'threading',
    'queue',

    # Gemini AI
    'google.generativeai',
    'google.ai.generativelanguage',

    # PDF y procesamiento
    'jinja2',
    'fitz',  # PyMuPDF
    'subprocess',

    # PIL/Pillow (CRÍTICO)
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'PIL.ImageOps',
    'Pillow',

    # OpenCV (si se usa)
    'cv2',

    # Otros módulos que pueden faltar
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
]

# Análisis del script principal
a = Analysis(
    ['ai_chat.py'],
    pathex=[
        '.',  # Directorio actual
        'app',  # Directorio de la aplicación
    ],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
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
        # NO excluir PIL ni cv2 porque los necesitamos
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filtrar archivos duplicados
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Crear ejecutable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Sistema_Constancias',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin ventana de consola
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/images/icon.ico' if Path('resources/images/icon.ico').exists() else None,
)
