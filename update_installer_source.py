#!/usr/bin/env python3
"""
Script para actualizar los archivos fuente del installer
Reemplaza la funcionalidad de prepare_installer.py eliminado
"""

import os
import shutil
import json
from pathlib import Path

def update_installer_source():
    """Actualiza los archivos en installer/source/ con la versión actual"""
    
    print("🔄 ACTUALIZANDO ARCHIVOS FUENTE DEL INSTALLER")
    print("=" * 50)
    
    # Rutas
    source_dir = Path("installer/source")
    app_source = source_dir / "app"
    config_source = source_dir / "config"
    
    # Crear directorios si no existen
    app_source.mkdir(parents=True, exist_ok=True)
    config_source.mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. ACTUALIZAR APLICACIÓN PRINCIPAL
        print("📁 Actualizando aplicación principal...")
        
        # Copiar archivos principales
        files_to_copy = [
            "ai_chat.py",
            "main_qt.py", 
            "simple_launcher.py",
            "requirements.txt"
        ]
        
        for file in files_to_copy:
            if Path(file).exists():
                shutil.copy2(file, app_source / file)
                print(f"  ✅ {file}")
            else:
                print(f"  ⚠️ {file} no encontrado")
        
        # Copiar directorio app/
        if Path("app").exists():
            if (app_source / "app").exists():
                shutil.rmtree(app_source / "app")
            shutil.copytree("app", app_source / "app")
            print(f"  ✅ app/ (directorio completo)")
        
        # Copiar directorio resources/
        if Path("resources").exists():
            if (app_source / "resources").exists():
                shutil.rmtree(app_source / "resources")
            shutil.copytree("resources", app_source / "resources")
            print(f"  ✅ resources/ (directorio completo)")
        
        # 2. ACTUALIZAR CONFIGURACIONES
        print("\n⚙️ Actualizando configuraciones...")
        
        # Copiar configuraciones
        config_files = [
            "school_config.json",
            "version.json"
        ]
        
        for file in config_files:
            if Path(file).exists():
                shutil.copy2(file, config_source / file)
                print(f"  ✅ {file}")
            else:
                print(f"  ⚠️ {file} no encontrado")
        
        # 3. VERIFICAR DEPENDENCIAS
        print("\n🔧 Verificando dependencias...")
        
        deps_dir = source_dir / "dependencies"
        required_deps = [
            "python-3.12.5-amd64.exe",
            "vcredist_x64.exe", 
            "wkhtmltopdf.exe"
        ]
        
        for dep in required_deps:
            dep_path = deps_dir / dep
            if dep_path.exists():
                print(f"  ✅ {dep}")
            else:
                print(f"  ❌ {dep} FALTANTE - Descargar manualmente")
        
        # 4. ACTUALIZAR VERSIÓN
        print("\n📊 Actualizando información de versión...")
        
        version_file = config_source / "version.json"
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                version_data = json.load(f)
            print(f"  📋 Versión actual: {version_data.get('version', 'N/A')}")
        
        print("\n✅ ACTUALIZACIÓN COMPLETADA")
        print("=" * 50)
        print("🎯 PRÓXIMOS PASOS:")
        print("1. Abrir installer/SistemaConstancias.iss en Inno Setup")
        print("2. Click en 'Compile'")
        print("3. El installer se generará en installer/output/")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False
    
    return True

def check_installer_ready():
    """Verifica si el installer está listo para compilar"""
    
    print("\n🔍 VERIFICANDO ESTADO DEL INSTALLER")
    print("=" * 40)
    
    source_dir = Path("installer/source")
    issues = []
    
    # Verificar archivos principales
    required_files = [
        "app/ai_chat.py",
        "app/main_qt.py",
        "app/requirements.txt",
        "app/app/__init__.py",
        "config/school_config.json"
    ]

    # Verificar scripts
    script_files = [
        "../scripts/launcher.bat",
        "../scripts/install_dependencies.bat"
    ]
    
    for file in required_files:
        file_path = source_dir / file
        if file_path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
            issues.append(file)

    # Verificar scripts
    for script in script_files:
        script_path = source_dir / script
        if script_path.exists():
            print(f"  ✅ {script}")
        else:
            print(f"  ❌ {script}")
            issues.append(script)
    
    # Verificar dependencias
    deps_dir = source_dir / "dependencies"
    required_deps = [
        "python-3.12.5-amd64.exe",
        "vcredist_x64.exe",
        "wkhtmltopdf.exe"
    ]
    
    for dep in required_deps:
        dep_path = deps_dir / dep
        if dep_path.exists():
            size_mb = dep_path.stat().st_size / (1024 * 1024)
            print(f"  ✅ {dep} ({size_mb:.1f} MB)")
        else:
            print(f"  ❌ {dep}")
            issues.append(f"dependencies/{dep}")
    
    if issues:
        print(f"\n⚠️ PROBLEMAS ENCONTRADOS: {len(issues)}")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print(f"\n✅ INSTALLER LISTO PARA COMPILAR")
        return True

if __name__ == "__main__":
    print("🚀 ACTUALIZADOR DE INSTALLER")
    print("=" * 50)
    
    # Actualizar archivos
    if update_installer_source():
        # Verificar estado
        check_installer_ready()
    
    print("\n🎯 Para compilar el installer:")
    print("1. Ejecutar este script cuando actualices código")
    print("2. Abrir installer/SistemaConstancias.iss en Inno Setup")
    print("3. Click 'Compile'")
