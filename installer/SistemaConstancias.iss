[Setup]
; Información básica
AppName=Sistema de Constancias - Escuela
AppVersion=2.0.0
AppVerName=Sistema de Constancias - Escuela v2.0.0
AppPublisher=Sistema de Constancias
AppPublisherURL=https://constancias.edu.mx
AppSupportURL=https://constancias.edu.mx/soporte
AppUpdatesURL=https://constancias.edu.mx/actualizaciones

; Directorios de instalación
DefaultDirName={autopf}\SistemaConstancias
DefaultGroupName=Sistema de Constancias
AllowNoIcons=yes

; Configuración de salida
OutputDir=output
OutputBaseFilename=SistemaConstancias_Installer_v2.0.0
; SetupIconFile=source\app\resources\images\logos\logo_educacion.png

; Compresión
Compression=lzma2
SolidCompression=yes

; Configuración de Windows
WizardStyle=modern
DisableProgramGroupPage=yes
LicenseFile=scripts\license.txt
InfoBeforeFile=scripts\readme.txt

; Privilegios
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; Aplicación principal
Source: "source\app\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Archivos de configuración
Source: "source\config\*"; DestDir: "{userappdata}\SistemaConstancias"; Flags: ignoreversion onlyifdoesntexist

; Dependencias
Source: "source\dependencies\vcredist_x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall
Source: "source\dependencies\wkhtmltopdf.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\Sistema de Constancias"; Filename: "{app}\simple_launcher.exe"
Name: "{group}\Interfaz con IA"; Filename: "{app}\simple_launcher.exe"; Parameters: "ai"
Name: "{group}\Interfaz Tradicional"; Filename: "{app}\simple_launcher.exe"; Parameters: "traditional"
Name: "{group}\{cm:UninstallProgram,Sistema de Constancias}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Sistema de Constancias"; Filename: "{app}\simple_launcher.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Sistema de Constancias"; Filename: "{app}\simple_launcher.exe"; Tasks: quicklaunchicon

[Run]
; Instalar Visual C++ Redistributables
Filename: "{tmp}\vcredist_x64.exe"; Parameters: "/quiet /norestart"; StatusMsg: "Instalando Visual C++ Redistributables..."; Flags: waituntilterminated

; Instalar wkhtmltopdf
Filename: "{tmp}\wkhtmltopdf.exe"; Parameters: "/S"; StatusMsg: "Instalando wkhtmltopdf..."; Flags: waituntilterminated

; Ejecutar aplicación al finalizar
Filename: "{app}\simple_launcher.exe"; Description: "{cm:LaunchProgram,Sistema de Constancias}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\SistemaConstancias"

[Code]
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1');
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
