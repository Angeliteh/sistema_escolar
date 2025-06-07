#!/usr/bin/env python3
"""
🔧 GENERADOR AUTOMÁTICO DE REQUIREMENTS.TXT
Analiza todo el código Python y genera requirements.txt completo
"""

import os
import ast
import sys
from pathlib import Path
from collections import defaultdict

def extract_imports_from_file(file_path):
    """Extrae todos los imports de un archivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
        
        return imports
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return set()

def scan_project_imports():
    """Escanea todo el proyecto buscando imports"""
    project_root = Path('.')
    all_imports = set()
    
    # Buscar archivos Python
    python_files = []
    for pattern in ['*.py', 'app/**/*.py']:
        python_files.extend(project_root.glob(pattern))
    
    print(f"🔍 Analizando {len(python_files)} archivos Python...")
    
    for py_file in python_files:
        if py_file.name.startswith('.'):
            continue
            
        imports = extract_imports_from_file(py_file)
        all_imports.update(imports)
        
        if imports:
            print(f"  📄 {py_file}: {len(imports)} imports")
    
    return all_imports

def categorize_imports(imports):
    """Categoriza imports en estándar, terceros y locales"""
    
    # Módulos estándar de Python (no necesitan instalación)
    standard_modules = {
        'os', 'sys', 'json', 'sqlite3', 'pathlib', 'datetime', 'uuid',
        'base64', 'hashlib', 'urllib', 'subprocess', 'threading', 'queue',
        'logging', 'argparse', 'tempfile', 'shutil', 'glob', 'time',
        'collections', 'itertools', 'functools', 'typing', 'dataclasses',
        'enum', 'abc', 'copy', 'pickle', 'csv', 'configparser', 'io',
        'math', 'random', 'string', 'textwrap', 'traceback', 'warnings',
        'weakref', 'gc', 'inspect', 'ast', 'dis', 'code', 'codeop',
        'keyword', 'token', 'tokenize', 'symbol', 'parser', 'platform',
        'ctypes', 'struct', 'array', 'bisect', 'heapq', 'operator',
        'reprlib', 'pprint', 'locale', 'gettext', 'calendar', 'mailbox',
        'mimetypes', 'base64', 'binascii', 'quopri', 'uu', 'html',
        'xml', 'email', 'mailcap', 'mimetypes', 'encodings', 'codecs',
        'unicodedata', 'stringprep', 'readline', 'rlcompleter'
    }
    
    # Mapeo de imports a paquetes PyPI
    pypi_mapping = {
        'PyQt5': 'PyQt5==5.15.10',
        'google': 'google-generativeai>=0.3.2',
        'dotenv': 'python-dotenv>=1.0.0',
        'pdfplumber': 'pdfplumber==0.10.2',
        'PyPDF2': 'PyPDF2==3.0.1',
        'reportlab': 'reportlab>=4.0.0',
        'PIL': 'Pillow==10.0.0',
        'jinja2': 'Jinja2==3.1.2',
        'requests': 'requests>=2.31.0',
        'fitz': 'PyMuPDF>=1.23.0',
        'urllib3': 'urllib3>=2.0.0'
    }
    
    standard = set()
    third_party = set()
    local = set()
    
    for imp in imports:
        if imp.startswith('app.'):
            local.add(imp)
        elif imp in standard_modules or imp.startswith('_'):
            standard.add(imp)
        else:
            third_party.add(imp)
    
    return standard, third_party, local, pypi_mapping

def generate_requirements_txt():
    """Genera requirements.txt completo"""
    
    print("🚀 GENERADOR AUTOMÁTICO DE REQUIREMENTS.TXT")
    print("=" * 50)
    
    # Escanear imports
    all_imports = scan_project_imports()
    
    # Categorizar
    standard, third_party, local, pypi_mapping = categorize_imports(all_imports)
    
    print(f"\n📊 ANÁLISIS COMPLETADO:")
    print(f"  📦 Módulos estándar: {len(standard)}")
    print(f"  🌐 Terceros: {len(third_party)}")
    print(f"  🏠 Locales: {len(local)}")
    
    # Generar requirements.txt
    requirements_content = """# ========================================
# SISTEMA DE CONSTANCIAS - DEPENDENCIAS COMPLETAS
# Generado automáticamente por generate_requirements.py
# ========================================

"""
    
    # Dependencias críticas
    critical_deps = []
    optional_deps = []
    
    for imp in sorted(third_party):
        if imp in pypi_mapping:
            critical_deps.append(pypi_mapping[imp])
        else:
            # Dependencia no mapeada - agregar como básica
            optional_deps.append(f"{imp}  # Verificar versión manualmente")
    
    if critical_deps:
        requirements_content += "# 🎯 DEPENDENCIAS CRÍTICAS\n"
        for dep in sorted(critical_deps):
            requirements_content += f"{dep}\n"
        requirements_content += "\n"
    
    if optional_deps:
        requirements_content += "# ⚠️ DEPENDENCIAS NO MAPEADAS (VERIFICAR)\n"
        for dep in sorted(optional_deps):
            requirements_content += f"# {dep}\n"
        requirements_content += "\n"
    
    requirements_content += """# ========================================
# NOTAS IMPORTANTES:
# ========================================
# - wkhtmltopdf se instala por separado (incluido en installer)
# - sqlite3 viene incluido con Python
# - tkinter viene incluido con Python
# - Módulos estándar no requieren instalación
# ========================================

# 📋 MÓDULOS ESTÁNDAR DETECTADOS (NO REQUIEREN INSTALACIÓN):
"""
    
    for mod in sorted(standard):
        requirements_content += f"# {mod}\n"
    
    requirements_content += "\n# 🏠 MÓDULOS LOCALES DETECTADOS:\n"
    for mod in sorted(local):
        requirements_content += f"# {mod}\n"
    
    # Escribir archivo
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    print(f"\n✅ requirements.txt generado exitosamente!")
    print(f"📄 Dependencias críticas: {len(critical_deps)}")
    print(f"⚠️ Dependencias no mapeadas: {len(optional_deps)}")
    
    return critical_deps, optional_deps

if __name__ == "__main__":
    critical, optional = generate_requirements_txt()
    
    if optional:
        print(f"\n⚠️ ATENCIÓN: {len(optional)} dependencias no mapeadas:")
        for dep in optional:
            print(f"  - {dep}")
        print("\nVerifica manualmente estas dependencias.")
