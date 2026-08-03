; installer.iss — Script de instalação do Finance Manager

[Setup]
AppName=Finance Manager
AppVersion=1.0
AppPublisher=Daniel Carvanny
DefaultDirName={autopf}\FinanceManager
DefaultGroupName=Finance Manager
OutputDir=installer_output
OutputBaseFilename=FinanceManager_Setup_v1.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar ícone na Área de Trabalho"; GroupDescription: "Ícones adicionais:"; Flags: unchecked

[Files]
; Copia toda a pasta do PyInstaller
Source: "dist\FinanceManager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Atalho no Menu Iniciar
Name: "{group}\Finance Manager"; Filename: "{app}\FinanceManager.exe"
; Atalho na Área de Trabalho (opcional)
Name: "{autodesktop}\Finance Manager"; Filename: "{app}\FinanceManager.exe"; Tasks: desktopicon

[Run]
; Abre o app ao finalizar a instalação
Filename: "{app}\FinanceManager.exe"; Description: "Iniciar Finance Manager"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Remove a pasta de dados ao desinstalar (opcional — remova se quiser preservar os dados)
; Type: filesandordirs; Name: "{userappdata}\FinanceManager"