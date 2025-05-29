"""
Script para limpiar dependencias pesadas del ejecutable
"""

import os
import shutil
from pathlib import Path

def get_directory_size(path):
    """Calcula el tamaño de un directorio en MB"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except:
        pass
    return total_size / (1024 * 1024)  # Convertir a MB

def clean_heavy_dependencies():
    """Elimina dependencias pesadas innecesarias"""
    print("🧹 LIMPIANDO DEPENDENCIAS PESADAS")
    print("=" * 60)
    
    # Directorio del ejecutable
    exe_dir = Path("dist/SistemaConstancias")
    if not exe_dir.exists():
        print("❌ No se encuentra dist/SistemaConstancias/")
        return False
    
    # Dependencias pesadas a eliminar
    heavy_deps = [
        # Machine Learning (muy pesado, innecesario)
        "torch",
        "torch-2.6.0.dist-info",
        "transformers",
        "faiss",
        "faiss_cpu-1.10.0.dist-info", 
        "faiss_cpu.libs",
        "onnxruntime",
        "onnxruntime-1.21.0.dist-info",
        "sklearn",
        "scikit_learn-1.6.1.dist-info",
        "scipy",
        "scipy.libs",
        "pandas",
        "pandas.libs",
        "matplotlib",
        "accelerate-1.6.0.dist-info",
        "huggingface_hub-0.29.3.dist-info",
        "safetensors",
        "safetensors-0.5.3.dist-info",
        "tokenizers",
        "tokenizers-0.21.1.dist-info",
        
        # Gaming (completamente innecesario)
        "pygame",
        
        # Web frameworks (innecesarios)
        "fastapi-0.103.2.dist-info",
        "starlette-0.27.0.dist-info",
        "uvicorn-0.23.2.dist-info",
        
        # Testing (innecesario en producción)
        "pytest_asyncio-0.26.0.dist-info",
        
        # Otros pesados opcionales
        "regex",
        "regex-2024.11.6.dist-info",
        "contourpy",
        "kiwisolver",
        "fontTools",
    ]
    
    # DLLs de pygame a eliminar
    pygame_dlls = [
        "SDL2.dll",
        "SDL2_image.dll", 
        "SDL2_mixer.dll",
        "SDL2_ttf.dll",
        "portmidi.dll",
    ]
    
    total_saved = 0
    removed_count = 0
    
    # Eliminar directorios pesados
    for dep in heavy_deps:
        dep_path = exe_dir / dep
        if dep_path.exists():
            try:
                size_mb = get_directory_size(dep_path)
                if dep_path.is_dir():
                    shutil.rmtree(dep_path)
                    print(f"🗑️ Eliminado directorio: {dep} ({size_mb:.1f} MB)")
                else:
                    dep_path.unlink()
                    print(f"🗑️ Eliminado archivo: {dep} ({size_mb:.1f} MB)")
                total_saved += size_mb
                removed_count += 1
            except Exception as e:
                print(f"❌ Error eliminando {dep}: {e}")
        else:
            print(f"⚠️ No encontrado: {dep}")
    
    # Eliminar DLLs de pygame
    for dll in pygame_dlls:
        dll_path = exe_dir / dll
        if dll_path.exists():
            try:
                size_mb = dll_path.stat().st_size / (1024 * 1024)
                dll_path.unlink()
                print(f"🗑️ Eliminado DLL: {dll} ({size_mb:.1f} MB)")
                total_saved += size_mb
                removed_count += 1
            except Exception as e:
                print(f"❌ Error eliminando {dll}: {e}")
    
    print(f"\n✅ LIMPIEZA COMPLETADA")
    print(f"📊 Elementos eliminados: {removed_count}")
    print(f"💾 Espacio liberado: {total_saved:.1f} MB")
    
    return True

def verify_essential_dependencies():
    """Verifica que las dependencias esenciales sigan presentes"""
    print("\n🔍 VERIFICANDO DEPENDENCIAS ESENCIALES")
    print("=" * 60)
    
    exe_dir = Path("dist/SistemaConstancias")
    
    essential_deps = [
        "PyQt5",           # Interfaz gráfica
        "google",          # Google AI
        "googleapiclient", # Google APIs
        "PIL",             # Imágenes
        "app",             # Nuestra aplicación
        "resources",       # Nuestros recursos
        "pymupdf",         # PDF processing
        "jinja2",          # Plantillas (en markupsafe)
        "markupsafe",      # Jinja2 dependency
        "requests",        # HTTP
        "certifi",         # SSL certificates
        "cryptography",    # Seguridad
        "lxml",            # XML/HTML parsing
    ]
    
    missing_deps = []
    present_deps = []
    
    for dep in essential_deps:
        dep_path = exe_dir / dep
        if dep_path.exists():
            size_mb = get_directory_size(dep_path)
            present_deps.append((dep, size_mb))
            print(f"✅ {dep} ({size_mb:.1f} MB)")
        else:
            missing_deps.append(dep)
            print(f"❌ FALTA: {dep}")
    
    if missing_deps:
        print(f"\n⚠️ DEPENDENCIAS FALTANTES: {len(missing_deps)}")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("🔧 El ejecutable podría no funcionar correctamente")
    else:
        print(f"\n✅ TODAS LAS DEPENDENCIAS ESENCIALES PRESENTES")
        total_essential = sum(size for _, size in present_deps)
        print(f"📊 Tamaño de dependencias esenciales: {total_essential:.1f} MB")
    
    return len(missing_deps) == 0

def calculate_final_size():
    """Calcula el tamaño final del ejecutable"""
    print("\n📏 CALCULANDO TAMAÑO FINAL")
    print("=" * 60)
    
    exe_dir = Path("dist/SistemaConstancias")
    if not exe_dir.exists():
        print("❌ Directorio no encontrado")
        return
    
    total_size = get_directory_size(exe_dir)
    print(f"📦 Tamaño total del ejecutable: {total_size:.1f} MB")
    
    # Estimar tamaño del instalador (compresión ~50%)
    installer_size = total_size * 0.5
    print(f"📦 Tamaño estimado del instalador: {installer_size:.1f} MB")
    
    if total_size < 300:
        print("✅ Tamaño aceptable para distribución")
    elif total_size < 500:
        print("⚠️ Tamaño grande pero manejable")
    else:
        print("❌ Tamaño muy grande, considerar más limpieza")

def main():
    """Función principal"""
    print("🧹 LIMPIEZA DE DEPENDENCIAS PESADAS")
    print("=" * 70)
    
    # Confirmar antes de proceder
    response = input("⚠️ ¿Eliminar dependencias pesadas? Esto puede romper el ejecutable si hay errores (s/N): ")
    if response.lower() != 's':
        print("❌ Limpieza cancelada")
        return
    
    try:
        # Paso 1: Limpiar dependencias pesadas
        if not clean_heavy_dependencies():
            print("❌ Error en la limpieza")
            return
        
        # Paso 2: Verificar dependencias esenciales
        if not verify_essential_dependencies():
            print("⚠️ Algunas dependencias esenciales faltan")
        
        # Paso 3: Calcular tamaño final
        calculate_final_size()
        
        print("\n" + "=" * 70)
        print("🎉 LIMPIEZA COMPLETADA")
        print("=" * 70)
        print("📋 PRÓXIMOS PASOS:")
        print("1. Probar que el ejecutable siga funcionando")
        print("2. Si funciona, regenerar el instalador")
        print("3. Probar instalador en máquina limpia")
        
    except Exception as e:
        print(f"\n❌ Error durante la limpieza: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    input("\nPresiona Enter para continuar...")
