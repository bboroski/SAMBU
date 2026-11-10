#define AppName "SAMBU"
#ifndef AppVersion
  #define AppVersion "0.11.0"
#endif
#ifndef AppOutput
  #define AppOutput "SAMBU-Setup"
#endif

[Setup]
AppId={{CECCFA10-1BE4-4A08-B643-80E26A2B955E}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=SAMBU Contributors
DefaultDirName={autopf}\SAMBU
DefaultGroupName=SAMBU
OutputDir=..\\..\\dist-installer
OutputBaseFilename={#AppOutput}
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
UninstallDisplayIcon={app}\sambu.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
VersionInfoVersion={#AppVersion}
VersionInfoProductName=SAMBU
VersionInfoDescription=SAMBU language and developer toolkit

[Files]
Source: "dist\sambu.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\SAMBU CLI"; Filename: "{app}\sambu.exe"; WorkingDir: "{app}"
Name: "{group}\Uninstall SAMBU"; Filename: "{uninstallexe}"

[Registry]
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\sambu.exe"; ValueType: string; ValueName: ""; ValueData: "{app}\sambu.exe"; Flags: uninsdeletekey
