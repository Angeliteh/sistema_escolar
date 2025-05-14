#!/usr/bin/env python3
"""
Script para crear un ejecutable del Sistema de Constancias Escolares.
Este script automatiza el proceso de creación de un ejecutable usando PyInstaller.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """Verifica que todos los requisitos estén instalados"""
    print("Verificando requisitos...")
    
    # Verificar PyInstaller
    try:
        import PyInstaller
        print("✓ PyInstaller está instalado")
    except ImportError:
        print("✗ PyInstaller no está instalado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Verificar otras dependencias
    dependencies = [
        "PyQt5", "jinja2", "pdfplumber", "PyPDF2", "Pillow", "sqlite3"
    ]
    
    for dep in dependencies:
        try:
            if dep == "sqlite3":  # sqlite3 es parte de la biblioteca estándar
                import sqlite3
            elif dep == "Pillow":
                import PIL
            else:
                __import__(dep)
            print(f"✓ {dep} está instalado")
        except ImportError:
            print(f"✗ {dep} no está instalado. Instalando...")
            package_name = "pillow" if dep == "Pillow" else dep.lower()
            subprocess.run([sys.executable, "-m", "pip", "install", package_name])

def create_icon():
    """Crea un archivo de icono si no existe"""
    icon_path = Path("logos/logo_educacion.ico")
    
    if icon_path.exists():
        print(f"✓ Icono encontrado en {icon_path}")
        return str(icon_path)
    
    # Buscar alguna imagen en la carpeta logos
    logos_dir = Path("logos")
    if not logos_dir.exists():
        os.makedirs("logos", exist_ok=True)
        print("✗ No se encontró la carpeta de logos. Se ha creado.")
    
    # Buscar imágenes que podrían servir como icono
    image_files = list(logos_dir.glob("*.png")) + list(logos_dir.glob("*.jpg"))
    
    if image_files:
        # Usar la primera imagen encontrada
        source_image = image_files[0]
        print(f"✓ Usando {source_image} como base para el icono")
        
        try:
            from PIL import Image
            img = Image.open(source_image)
            # Redimensionar a tamaños de icono estándar
            img.save(icon_path, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128)])
            print(f"✓ Icono creado en {icon_path}")
            return str(icon_path)
        except Exception as e:
            print(f"✗ Error al crear el icono: {e}")
    
    print("✗ No se encontraron imágenes para usar como icono")
    return None

def ensure_directories():
    """Asegura que existan los directorios necesarios"""
    print("Verificando directorios necesarios...")
    
    directories = ["plantillas", "logos", "fotos", "salidas", "temp_images"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Directorio {directory} verificado")

def build_executable():
    """Construye el ejecutable usando PyInstaller"""
    print("\nConstruyendo ejecutable...")
    
    # Verificar si existe el archivo spec
    spec_path = Path("ConstanciasEscolares.spec")
    
    if spec_path.exists():
        print(f"✓ Usando archivo de especificación existente: {spec_path}")
        subprocess.run(["pyinstaller", str(spec_path)])
    else:
        print("✗ No se encontró archivo de especificación. Creando uno nuevo...")
        
        # Crear comando de PyInstaller
        icon_path = create_icon()
        cmd = [
            "pyinstaller",
            "--name", "ConstanciasEscolares",
            "--onefile",
            "--windowed",
        ]
        
        if icon_path:
            cmd.extend(["--icon", icon_path])
        
        # Agregar datos adicionales
        cmd.extend(["--add-data", f"plantillas{os.pathsep}plantillas"])
        cmd.extend(["--add-data", f"logos{os.pathsep}logos"])
        
        # Agregar el script principal
        cmd.append("main_qt.py")
        
        # Ejecutar PyInstaller
        subprocess.run(cmd)
    
    # Verificar si se creó el ejecutable
    if sys.platform == "win32":
        exe_path = Path("dist/ConstanciasEscolares.exe")
    else:
        exe_path = Path("dist/ConstanciasEscolares")
    
    if exe_path.exists():
        print(f"\n✅ Ejecutable creado exitosamente: {exe_path}")
        print("\nPuedes distribuir el archivo ejecutable junto con las carpetas:")
        print("- plantillas/")
        print("- logos/")
        print("- fotos/ (si es necesario)")
        print("\nO puedes crear un instalador para una distribución más sencilla.")
    else:
        print("\n❌ Error al crear el ejecutable. Revisa los mensajes anteriores.")

def main():
    """Función principal"""
    print("=== CREACIÓN DE EJECUTABLE DEL SISTEMA DE CONSTANCIAS ESCOLARES ===\n")
    
    check_requirements()
    ensure_directories()
    build_executable()

if __name__ == "__main__":
    main()
