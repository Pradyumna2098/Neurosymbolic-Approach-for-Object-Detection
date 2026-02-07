; Inno Setup Script for Neurosymbolic Object Detection Application
; This script creates a Windows installer that packages both the Electron frontend
; and the PyInstaller-packaged backend into a single installation.

#define MyAppName "Neurosymbolic Object Detection"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Pradyumna S R"
#define MyAppURL "https://github.com/Pradyumna2098/Neurosymbolic-Approach-for-Object-Detection"
#define MyAppExeName "Neurosymbolic Object Detection.exe"
#define MyBackendExeName "neurosymbolic-backend.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{8F2D3C4A-5B6E-4F7A-8D9C-1A2B3C4D5E6F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; License file
LicenseFile=LICENSE
; Output configuration
OutputDir=installer_output
OutputBaseFilename=NeurosymbolicApp_Setup_v{#MyAppVersion}
; SetupIconFile=frontend\src\assets\icon.ico
; Uncomment the line above when icon file is created
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
; Minimum Windows version
MinVersion=10.0
; Architecture - 64-bit only
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
; Privileges
PrivilegesRequired=admin
; Wizard images (optional - comment out if images don't exist)
;WizardImageFile=installer_assets\wizard_large.bmp
;WizardSmallImageFile=installer_assets\wizard_small.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Frontend - Electron application
; Note: Update this path based on where Electron Forge outputs the built application
Source: "frontend\out\Neurosymbolic Object Detection-win32-x64\*"; DestDir: "{app}\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs
; Backend - PyInstaller executable
Source: "dist\neurosymbolic-backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs
; Configuration examples
Source: "shared\configs\*"; DestDir: "{app}\configs"; Flags: ignoreversion recursesubdirs createallsubdirs
; Documentation
Source: "README.md"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; DestName: "LICENSE.txt"; Flags: ignoreversion
Source: "EXECUTABLE_README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "docs\feature_implementation\WINDOWS_PACKAGING_GUIDE.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "docs\feature_implementation\WINDOWS_EXECUTABLE_USER_GUIDE.md"; DestDir: "{app}\docs"; Flags: ignoreversion
; Launcher scripts
Source: "start_application.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "start_backend.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcuts
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\frontend\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autoprograms}\{#MyAppName} Backend Server"; Filename: "{app}\backend\{#MyBackendExeName}"; WorkingDir: "{app}\backend"
Name: "{autoprograms}\{#MyAppName} Documentation"; Filename: "{app}\docs\WINDOWS_EXECUTABLE_USER_GUIDE.md"
Name: "{autoprograms}\{#MyAppName} Uninstall"; Filename: "{uninstallexe}"
; Desktop shortcut
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\frontend\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon
; Quick Launch shortcut
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\frontend\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: quicklaunchicon

[Dirs]
; Create directories for user data
Name: "{app}\data"; Permissions: users-full
Name: "{app}\data\uploads"; Permissions: users-full
Name: "{app}\data\results"; Permissions: users-full
Name: "{app}\data\visualizations"; Permissions: users-full
Name: "{app}\data\jobs"; Permissions: users-full
Name: "{app}\models"; Permissions: users-full
Name: "{app}\logs"; Permissions: users-full

[Run]
; Optional: Run the application after installation
Filename: "{app}\frontend\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
; Optional: Open README after installation
Filename: "{app}\EXECUTABLE_README.txt"; Description: "View README"; Flags: postinstall shellexec skipifsilent unchecked

[UninstallDelete]
; Clean up user data directories on uninstall (optional - commented out for safety)
; Users may want to keep their data even after uninstalling
; Type: filesandordirs; Name: "{app}\data"
; Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\models"

[Code]
// Custom code to check for dependencies

function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
  SwiPlPath: String;
begin
  Result := True;
  
  // Check for SWI-Prolog installation (optional but recommended)
  if RegQueryStringValue(HKLM, 'SOFTWARE\SWI\Prolog', 'home', SwiPlPath) or
     RegQueryStringValue(HKLM64, 'SOFTWARE\SWI\Prolog', 'home', SwiPlPath) or
     FileExists('C:\Program Files\swipl\bin\swipl.exe') then
  begin
    Log('SWI-Prolog detected at: ' + SwiPlPath);
  end
  else
  begin
    if MsgBox('SWI-Prolog is not detected on your system. ' +
              'The application requires SWI-Prolog for symbolic reasoning features. ' + #13#10#13#10 +
              'Do you want to continue with the installation? ' +
              'You can install SWI-Prolog later from https://www.swi-prolog.org/download/stable',
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Any post-installation tasks can be added here
    Log('Installation completed successfully');
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;
  if MsgBox('Do you want to completely remove ' + '{#MyAppName}' + ' and all of its components?',
            mbConfirmation, MB_YESNO) = IDYES then
  begin
    Result := True;
  end
  else
  begin
    Result := False;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataPath: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataPath := ExpandConstant('{app}\data');
    if DirExists(DataPath) then
    begin
      if MsgBox('Do you want to remove user data and uploaded files?' + #13#10 +
                'Location: ' + DataPath + #13#10#13#10 +
                'Select "No" to keep your data for future installations.',
                mbConfirmation, MB_YESNO) = IDYES then
      begin
        DelTree(DataPath, True, True, True);
      end;
    end;
  end;
end;
