; Script Inno Setup pour Pystart.
; Genere : dist\Pystart-Setup-{version}.exe
;
; Le numero de version est lu depuis app\__init__.py par le workflow de
; release (option /DMyAppVersion=...). En local, on peut le passer ainsi :
;   iscc /DMyAppVersion=0.0.1 scripts\Pystart.iss

#ifndef MyAppVersion
  #define MyAppVersion "0.0.1"
#endif

#define MyAppName "Pystart"
#define MyAppPublisher "feelsmanvt"
#define MyAppURL "https://github.com/kikilikiki/Pystart"
#define MyAppExeName "Pystart.exe"

[Setup]
AppId={{B8F2B0F1-2C3D-4E5F-9A7B-PYSTART000001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Les donnees utilisateur sont dans %APPDATA%\Pystart : jamais touchees ici.
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=..\dist
OutputBaseFilename=Pystart-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Tout le contenu du dossier PyInstaller (dist\Pystart\...).
Source: "..\dist\Pystart\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; On ne supprime QUE le dossier programme. Les cours perso et la progression
; ({userappdata}\Pystart) restent en place volontairement.
Type: filesandordirs; Name: "{app}"
