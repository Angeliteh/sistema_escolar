"""
Script completo para generar el instalador profesional
Automatiza todo el proceso desde PyInstaller hasta Inno Setup
"""

import os
import subprocess
import sys
from pathlib import Path
import shutil

def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    print(f"\n🔧 {description}")
    print("=" * 50)
    print(f"Ejecutando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Comando ejecutado exitosamente")
        if result.stdout:
            print(f"Salida: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando comando: {e}")
        if e.stdout:
            print(f"Salida: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_inno_setup():
    """Verifica si Inno Setup está instalado"""
    print("\n🔍 VERIFICANDO INNO SETUP")
    print("=" * 50)
    
    # Rutas comunes de Inno Setup
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe"
    ]
    
    for path in inno_paths:
        if Path(path).exists():
            print(f"✅ Inno Setup encontrado: {path}")
            return path
    
    print("❌ Inno Setup no encontrado")
    print("💡 Descarga e instala desde: https://jrsoftware.org/isdl.php")
    return None

def clean_previous_builds():
    """Limpia builds anteriores"""
    print("\n🧹 LIMPIANDO BUILDS ANTERIORES")
    print("=" * 50)
    
    directories_to_clean = ["dist", "build", "installer"]
    
    for directory in directories_to_clean:
        if Path(directory).exists():
            shutil.rmtree(directory)
            print(f"✅ Eliminado: {directory}")
        else:
            print(f"⚠️ No existe: {directory}")

def build_executable():
    """Construye el ejecutable con PyInstaller"""
    print("\n🏗️ CONSTRUYENDO EJECUTABLE")
    print("=" * 50)

    # Verificar que existe simple_launcher.py
    if not Path("simple_launcher.py").exists():
        print("❌ No se encuentra simple_launcher.py")
        return False

    # Verificar que existe el archivo .spec
    spec_file = Path("SistemaConstancias.spec")
    if spec_file.exists():
        print("✅ Usando archivo .spec personalizado")
        command = f"pyinstaller {spec_file}"
    else:
        print("⚠️ Archivo .spec no encontrado, usando comando básico")
        # Comando PyInstaller básico
        pyinstaller_cmd = [
            "pyinstaller",
            "--onedir",
            "--windowed",
            "--name=SistemaConstancias",
            "--icon=app/ui/resources/images/logos/logo_educacion.ico",
            "simple_launcher.py"
        ]
        command = " ".join(pyinstaller_cmd)

    return run_command(command, "Generando ejecutable con PyInstaller")

def prepare_installer():
    """Ejecuta el script de preparación del instalador"""
    print("\n📦 PREPARANDO INSTALADOR")
    print("=" * 50)
    
    return run_command("python prepare_installer.py", "Preparando archivos del instalador")

def compile_installer(inno_path):
    """Compila el instalador con Inno Setup"""
    print("\n🔨 COMPILANDO INSTALADOR")
    print("=" * 50)
    
    iss_file = Path("installer/SistemaConstancias.iss")
    if not iss_file.exists():
        print(f"❌ No se encuentra {iss_file}")
        return False
    
    command = f'"{inno_path}" "{iss_file.absolute()}"'
    return run_command(command, "Compilando instalador con Inno Setup")

def verify_output():
    """Verifica que el instalador se generó correctamente"""
    print("\n✅ VERIFICANDO RESULTADO")
    print("=" * 50)
    
    output_dir = Path("installer/output")
    if not output_dir.exists():
        print("❌ Directorio de salida no existe")
        return False
    
    installer_files = list(output_dir.glob("*.exe"))
    if not installer_files:
        print("❌ No se encontró archivo instalador")
        return False
    
    installer_file = installer_files[0]
    size_mb = installer_file.stat().st_size / 1024 / 1024
    
    print(f"✅ Instalador generado: {installer_file.name}")
    print(f"✅ Tamaño: {size_mb:.1f} MB")
    print(f"✅ Ubicación: {installer_file.absolute()}")
    
    return True

def main():
    """Función principal - proceso completo"""
    print("🚀 GENERADOR COMPLETO DE INSTALADOR PROFESIONAL")
    print("=" * 70)
    print("Este script automatiza todo el proceso:")
    print("1. Limpia builds anteriores")
    print("2. Genera ejecutable con PyInstaller") 
    print("3. Prepara archivos del instalador")
    print("4. Compila instalador con Inno Setup")
    print("5. Verifica resultado final")
    print("=" * 70)
    
    try:
        # Paso 1: Verificar Inno Setup
        inno_path = check_inno_setup()
        if not inno_path:
            return False
        
        # Paso 2: Limpiar builds anteriores
        clean_previous_builds()
        
        # Paso 3: Construir ejecutable
        if not build_executable():
            print("❌ Error construyendo ejecutable")
            return False
        
        # Paso 4: Preparar instalador
        if not prepare_installer():
            print("❌ Error preparando instalador")
            return False
        
        # Paso 5: Compilar instalador
        if not compile_installer(inno_path):
            print("❌ Error compilando instalador")
            return False
        
        # Paso 6: Verificar resultado
        if not verify_output():
            print("❌ Error verificando resultado")
            return False
        
        print("\n" + "=" * 70)
        print("🎉 ¡INSTALADOR GENERADO EXITOSAMENTE!")
        print("=" * 70)
        print("✅ Proceso completado sin errores")
        print("✅ Instalador listo para distribución")
        print("✅ Probado en máquina de desarrollo")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Probar instalador en máquina limpia")
        print("2. Verificar que todas las dependencias se instalan")
        print("3. Confirmar que la aplicación funciona correctamente")
        print("4. Distribuir a usuarios finales")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante el proceso: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    input("\nPresiona Enter para continuar...")
    exit(0 if success else 1)
