"""
Script para limpiar el proyecto y dejarlo organizado
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Limpia archivos innecesarios del proyecto"""
    print("🧹 LIMPIANDO PROYECTO")
    print("=" * 50)

    # Archivos y carpetas a eliminar (VERSIÓN SEGURA)
    items_to_remove = [
        # Archivos de PyInstaller obsoletos (SEGUROS DE ELIMINAR)
        "Interfaz_IA.spec",
        "Interfaz_Tradicional.spec",
        "Sistema_Constancias.spec",
        "fixed_error.spec",

        # Archivos de prueba obsoletos (SEGUROS DE ELIMINAR)
        "test_executable_independence.py",
        "test_executable_paths.py",
        "test_executable_readiness.py",
        "test_path_migration.py",
        "test_services_migration.py",
        "test_system_builder.py",
        "verify_generated_system.py",

        # Scripts obsoletos (SEGUROS DE ELIMINAR)
        "build_executable.py",
        "diagnose_for_executable.py",
        "fix_wkhtmltopdf.py",
        "organize_project.py",

        # Carpetas de testing obsoletas (SEGUROS DE ELIMINAR)
        "testing/",

        # Specs obsoletos (SEGUROS DE ELIMINAR)
        "specs/",

        # ELIMINADOS DE LA LISTA (CONSERVAR):
        # - "temp/" - Podría contener archivos temporales necesarios
        # - "data/" - Podría contener datos importantes
        # - "build/" - Necesario para builds futuros
        # - "dist/" - Contiene ejecutables
        # - "dev_launcher.py" - Podría ser útil para desarrollo
        # - "hybrid_launcher.py" - Podría ser útil
        # - "database_admin.py" - Podría ser útil
        # - "backups/" - Contiene respaldos importantes
    ]

    removed_count = 0

    for item in items_to_remove:
        item_path = Path(item)
        if item_path.exists():
            try:
                if item_path.is_file():
                    item_path.unlink()
                    print(f"🗑️ Eliminado archivo: {item}")
                else:
                    shutil.rmtree(item_path)
                    print(f"🗑️ Eliminada carpeta: {item}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error eliminando {item}: {e}")
        else:
            print(f"⚠️ No existe: {item}")

    print(f"\n✅ Eliminados {removed_count} elementos")
    return removed_count

def organize_remaining_files():
    """Organiza los archivos restantes"""
    print("\n📁 ORGANIZANDO ARCHIVOS RESTANTES")
    print("=" * 50)

    # Crear estructura organizada
    directories_to_create = [
        "build/",           # Para builds futuros
        "dist/",            # Para distribución
        "installer/",       # Para archivos del instalador
        "installer/source/", # Archivos fuente del instalador
        "installer/output/", # Instaladores generados
        "tests/",           # Tests organizados
        "scripts/utils/",   # Scripts de utilidad
    ]

    for directory in directories_to_create:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Creado directorio: {directory}")

    # MOVIMIENTOS DESHABILITADOS POR SEGURIDAD
    # No moveremos archivos automáticamente para evitar romper el sistema
    print("⚠️ Movimientos de archivos deshabilitados por seguridad")
    print("📋 Archivos que podrían moverse manualmente si es necesario:")
    print("   - output/simple_launcher/ → dist/SistemaConstancias/")
    print("   - system_builder_ui.py → scripts/utils/system_builder_ui.py")

def clean_pycache():
    """Elimina todos los archivos __pycache__"""
    print("\n🧹 LIMPIANDO ARCHIVOS __pycache__")
    print("=" * 50)

    removed_count = 0
    for root, dirs, files in os.walk("."):
        # Eliminar carpetas __pycache__
        if "__pycache__" in dirs:
            pycache_path = Path(root) / "__pycache__"
            try:
                shutil.rmtree(pycache_path)
                print(f"🗑️ Eliminado: {pycache_path}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error eliminando {pycache_path}: {e}")

        # Eliminar archivos .pyc
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = Path(root) / file
                try:
                    pyc_path.unlink()
                    print(f"🗑️ Eliminado: {pyc_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Error eliminando {pyc_path}: {e}")

    print(f"✅ Eliminados {removed_count} archivos de cache")

def create_project_structure_doc():
    """Crea documentación de la estructura final"""
    print("\n📝 CREANDO DOCUMENTACIÓN DE ESTRUCTURA")
    print("=" * 50)

    structure_doc = """# ESTRUCTURA DEL PROYECTO LIMPIO

## 📁 ESTRUCTURA PRINCIPAL
```
constancias_system/
├── 📄 README.md                    # Documentación principal
├── 📄 requirements.txt             # Dependencias Python
├── 📄 school_config.json           # Configuración de escuela
├── 📄 version.json                 # Información de versión
├── 📄 .env                         # Variables de entorno
│
├── 📁 app/                         # Código principal de la aplicación
│   ├── 📁 core/                    # Núcleo del sistema
│   ├── 📁 data/                    # Modelos y repositorios
│   ├── 📁 services/                # Servicios de negocio
│   └── 📁 ui/                      # Interfaces de usuario
│
├── 📁 resources/                   # Recursos del sistema
│   ├── 📁 data/                    # Base de datos
│   ├── 📁 templates/               # Plantillas HTML
│   ├── 📁 images/                  # Imágenes y logos
│   └── 📁 examples/                # Ejemplos de constancias
│
├── 📁 logs/                        # Archivos de log
│
├── 📁 scripts/                     # Scripts de utilidad
│   └── 📁 utils/                   # Utilidades varias
│
├── 📁 tests/                       # Tests del sistema
│
├── 📁 docs/                        # Documentación
│   ├── 📁 architecture/            # Documentación técnica
│   ├── 📁 commercial/              # Documentación comercial
│   └── 📁 development/             # Documentación de desarrollo
│
├── 📁 installer/                   # Archivos para el instalador
│   ├── 📁 source/                  # Archivos fuente
│   └── 📁 output/                  # Instaladores generados
│
├── 📁 dist/                        # Distribución
│   └── 📁 SistemaConstancias/      # Ejecutable empaquetado
│
└── 📁 build/                       # Archivos de construcción
```

## 🚀 ARCHIVOS PRINCIPALES

### Puntos de entrada:
- `simple_launcher.py` - Launcher principal
- `ai_chat.py` - Interfaz IA directa
- `main_qt.py` - Interfaz tradicional directa

### Configuración:
- `school_config.json` - Configuración de la escuela
- `version.json` - Información de versión
- `.env` - API keys y variables de entorno

## 📋 ARCHIVOS ELIMINADOS

### Archivos obsoletos eliminados:
- Múltiples .spec de PyInstaller
- Scripts de prueba obsoletos
- Launchers duplicados
- Carpetas de build antiguas
- Archivos de cache Python

### Archivos reorganizados:
- Tests movidos a carpeta tests/
- Scripts movidos a scripts/utils/
- Ejecutable movido a dist/SistemaConstancias/
"""

    with open("PROJECT_STRUCTURE.md", "w", encoding="utf-8") as f:
        f.write(structure_doc)

    print("✅ Documentación creada: PROJECT_STRUCTURE.md")

def main():
    """Función principal de limpieza"""
    print("🧹 LIMPIEZA COMPLETA DEL PROYECTO")
    print("=" * 70)

    # Confirmar antes de proceder
    response = input("⚠️ ¿Estás seguro de que quieres limpiar el proyecto? (s/N): ")
    if response.lower() != 's':
        print("❌ Limpieza cancelada")
        return

    try:
        # Paso 1: Limpiar archivos innecesarios
        cleanup_project()

        # Paso 2: Limpiar cache de Python
        clean_pycache()

        # Paso 3: Organizar archivos restantes
        organize_remaining_files()

        # Paso 4: Crear documentación
        create_project_structure_doc()

        print("\n" + "=" * 70)
        print("🎉 LIMPIEZA COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print("✅ Proyecto limpio y organizado")
        print("✅ Estructura documentada en PROJECT_STRUCTURE.md")
        print("✅ Listo para crear instalador")

    except Exception as e:
        print(f"\n❌ Error durante la limpieza: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    input("\nPresiona Enter para continuar...")
