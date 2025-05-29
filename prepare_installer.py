"""
Script para preparar archivos para el instalador
"""

import os
import shutil
import requests
from pathlib import Path

def create_installer_structure():
    """Crea la estructura de directorios para el instalador"""
    print("📁 CREANDO ESTRUCTURA DEL INSTALADOR")
    print("=" * 50)
    
    directories = [
        "installer/source",
        "installer/source/app",
        "installer/source/dependencies",
        "installer/source/config",
        "installer/source/resources",
        "installer/output",
        "installer/scripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Creado: {directory}")

def copy_application_files():
    """Copia los archivos de la aplicación al directorio del instalador"""
    print("\n📦 COPIANDO ARCHIVOS DE LA APLICACIÓN")
    print("=" * 50)
    
    # Verificar que existe el ejecutable
    source_exe = Path("dist/SistemaConstancias")
    if not source_exe.exists():
        print("❌ No se encuentra dist/SistemaConstancias/")
        print("💡 Asegúrate de que el ejecutable esté en dist/SistemaConstancias/")
        return False
    
    # Copiar ejecutable completo
    dest_app = Path("installer/source/app")
    if dest_app.exists():
        shutil.rmtree(dest_app)
    
    shutil.copytree(source_exe, dest_app)
    print(f"✅ Copiado ejecutable: {source_exe} → {dest_app}")
    
    # Copiar archivos de configuración
    config_files = [
        "school_config.json",
        "version.json"
    ]
    
    for config_file in config_files:
        if Path(config_file).exists():
            shutil.copy2(config_file, f"installer/source/config/{config_file}")
            print(f"✅ Copiado config: {config_file}")
        else:
            print(f"⚠️ No encontrado: {config_file}")
    
    return True

def download_dependencies():
    """Descarga dependencias necesarias"""
    print("\n📥 DESCARGANDO DEPENDENCIAS")
    print("=" * 50)
    
    dependencies_dir = Path("installer/source/dependencies")
    
    # URLs de dependencias
    dependencies = {
        "vcredist_x64.exe": "https://aka.ms/vs/17/release/vc_redist.x64.exe",
        "wkhtmltopdf.exe": "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.msvc2015-win64.exe"
    }
    
    for filename, url in dependencies.items():
        file_path = dependencies_dir / filename
        
        if file_path.exists():
            print(f"✅ Ya existe: {filename}")
            continue
        
        try:
            print(f"📥 Descargando {filename}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Descargado: {filename} ({file_path.stat().st_size / 1024 / 1024:.1f} MB)")
            
        except Exception as e:
            print(f"❌ Error descargando {filename}: {e}")
            print(f"💡 Descarga manualmente desde: {url}")
    
    return True

def create_installer_script():
    """Crea el script de Inno Setup"""
    print("\n📝 CREANDO SCRIPT DE INNO SETUP")
    print("=" * 50)
    
    # Leer información de versión
    version = "2.0.0"
    try:
        import json
        with open("version.json", "r") as f:
            version_data = json.load(f)
            version = version_data.get("version", "2.0.0")
    except:
        pass
    
    # Leer configuración de escuela
    school_name = "Sistema de Constancias Escolares"
    try:
        import json
        with open("school_config.json", "r", encoding="utf-8") as f:
            school_data = json.load(f)
            school_name = f"Sistema de Constancias - {school_data.get('school_name', 'Escuela')}"
    except:
        pass
    
    inno_script = f'''[Setup]
; Información básica
AppName={school_name}
AppVersion={version}
AppVerName={school_name} v{version}
AppPublisher=Sistema de Constancias
AppPublisherURL=https://constancias.edu.mx
AppSupportURL=https://constancias.edu.mx/soporte
AppUpdatesURL=https://constancias.edu.mx/actualizaciones

; Directorios de instalación
DefaultDirName={{autopf}}\\SistemaConstancias
DefaultGroupName=Sistema de Constancias
AllowNoIcons=yes

; Configuración de salida
OutputDir=installer\\output
OutputBaseFilename=SistemaConstancias_Installer_v{version}
SetupIconFile=installer\\source\\app\\resources\\images\\logos\\logo_educacion.png

; Compresión
Compression=lzma2
SolidCompression=yes

; Configuración de Windows
WizardStyle=modern
DisableProgramGroupPage=yes
LicenseFile=installer\\scripts\\license.txt
InfoBeforeFile=installer\\scripts\\readme.txt

; Privilegios
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; Aplicación principal
Source: "installer\\source\\app\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Archivos de configuración
Source: "installer\\source\\config\\*"; DestDir: "{{userappdata}}\\SistemaConstancias"; Flags: ignoreversion onlyifdoesntexist

; Dependencias
Source: "installer\\source\\dependencies\\vcredist_x64.exe"; DestDir: "{{tmp}}"; Flags: deleteafterinstall
Source: "installer\\source\\dependencies\\wkhtmltopdf.exe"; DestDir: "{{tmp}}"; Flags: deleteafterinstall

[Icons]
Name: "{{group}}\\Sistema de Constancias"; Filename: "{{app}}\\simple_launcher.exe"
Name: "{{group}}\\Interfaz con IA"; Filename: "{{app}}\\simple_launcher.exe"; Parameters: "ai"
Name: "{{group}}\\Interfaz Tradicional"; Filename: "{{app}}\\simple_launcher.exe"; Parameters: "traditional"
Name: "{{group}}\\{{cm:UninstallProgram,Sistema de Constancias}}"; Filename: "{{uninstallexe}}"
Name: "{{commondesktop}}\\Sistema de Constancias"; Filename: "{{app}}\\simple_launcher.exe"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\Sistema de Constancias"; Filename: "{{app}}\\simple_launcher.exe"; Tasks: quicklaunchicon

[Run]
; Instalar Visual C++ Redistributables
Filename: "{{tmp}}\\vcredist_x64.exe"; Parameters: "/quiet /norestart"; StatusMsg: "Instalando Visual C++ Redistributables..."; Flags: waituntilterminated

; Instalar wkhtmltopdf
Filename: "{{tmp}}\\wkhtmltopdf.exe"; Parameters: "/S"; StatusMsg: "Instalando wkhtmltopdf..."; Flags: waituntilterminated

; Ejecutar aplicación al finalizar
Filename: "{{app}}\\simple_launcher.exe"; Description: "{{cm:LaunchProgram,Sistema de Constancias}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{{userappdata}}\\SistemaConstancias"

[Code]
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{{#SetupSetting("AppId")}}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

function IsUpgrade(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;

function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  Result := 0;
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
  end else
    Result := 1;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep=ssInstall) then
  begin
    if (IsUpgrade()) then
    begin
      UnInstallOldVersion();
    end;
  end;
end;
'''
    
    script_path = Path("installer/SistemaConstancias.iss")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(inno_script)
    
    print(f"✅ Script creado: {script_path}")
    return True

def create_support_files():
    """Crea archivos de soporte para el instalador"""
    print("\n📄 CREANDO ARCHIVOS DE SOPORTE")
    print("=" * 50)
    
    # Crear directorio de scripts
    scripts_dir = Path("installer/scripts")
    scripts_dir.mkdir(exist_ok=True)
    
    # Archivo de licencia
    license_text = """LICENCIA DE USO - SISTEMA DE CONSTANCIAS ESCOLARES

Copyright (c) 2024 Sistema de Constancias

Se concede permiso para usar este software bajo los siguientes términos:

1. Este software se proporciona "tal como está", sin garantías de ningún tipo.
2. El uso de este software es bajo su propio riesgo.
3. No se permite la redistribución sin autorización expresa.
4. El soporte técnico está disponible para usuarios registrados.

Para más información, contacte: soporte@constancias.edu.mx
"""
    
    with open(scripts_dir / "license.txt", "w", encoding="utf-8") as f:
        f.write(license_text)
    
    # Archivo README
    readme_text = """SISTEMA DE CONSTANCIAS ESCOLARES
================================

¡Gracias por elegir nuestro Sistema de Constancias!

CARACTERÍSTICAS:
- Generación automática de constancias de estudios, calificaciones y traslado
- Interfaz tradicional e interfaz con Inteligencia Artificial
- Base de datos integrada para gestión de alumnos
- Plantillas personalizables
- Exportación a PDF de alta calidad

REQUISITOS DEL SISTEMA:
- Windows 10 o superior (64-bit)
- 4 GB de RAM mínimo
- 500 MB de espacio en disco
- Conexión a internet (para funciones de IA)

INSTALACIÓN:
Este instalador configurará automáticamente todas las dependencias necesarias.

SOPORTE:
- Email: soporte@constancias.edu.mx
- Documentación: https://constancias.edu.mx/docs
- Actualizaciones: https://constancias.edu.mx/updates

¡Esperamos que disfrute usando el sistema!
"""
    
    with open(scripts_dir / "readme.txt", "w", encoding="utf-8") as f:
        f.write(readme_text)
    
    print("✅ Archivos de soporte creados")
    return True

def main():
    """Función principal"""
    print("🛠️ PREPARANDO INSTALADOR PROFESIONAL")
    print("=" * 70)
    
    try:
        # Paso 1: Crear estructura
        create_installer_structure()
        
        # Paso 2: Copiar archivos de aplicación
        if not copy_application_files():
            print("❌ Error copiando archivos de aplicación")
            return False
        
        # Paso 3: Descargar dependencias
        download_dependencies()
        
        # Paso 4: Crear script de Inno Setup
        create_installer_script()
        
        # Paso 5: Crear archivos de soporte
        create_support_files()
        
        print("\n" + "=" * 70)
        print("🎉 PREPARACIÓN COMPLETADA")
        print("=" * 70)
        print("✅ Estructura del instalador creada")
        print("✅ Archivos de aplicación copiados")
        print("✅ Script de Inno Setup generado")
        print("✅ Archivos de soporte creados")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Instalar Inno Setup desde: https://jrsoftware.org/isdl.php")
        print("2. Abrir: installer/SistemaConstancias.iss")
        print("3. Compilar el instalador")
        print("4. Probar en máquina limpia")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la preparación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    input("\nPresiona Enter para continuar...")
    exit(0 if success else 1)
