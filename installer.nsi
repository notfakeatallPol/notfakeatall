; Installer script for Secure Submission System
; Created with NSIS (Nullsoft Scriptable Install System)

; Define the application name and version
!define APPNAME "Secure Submission System"
!define APPVERSION "1.0.0"
!define COMPANYNAME "Your Company"

; Include modern UI
!include "MUI2.nsh"

; General
Name "${APPNAME} ${APPVERSION}"
OutFile "SecureSubmissionSystem-Setup.exe"
InstallDir "$PROGRAMFILES\${APPNAME}"
InstallDirRegKey HKLM "Software\${APPNAME}" "Install_Dir"
RequestExecutionLevel admin

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "static\favicon.ico"
!define MUI_UNICON "static\favicon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "static\installer-welcome.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "static\installer-welcome.bmp"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; The installation section
Section "Install"
  SetOutPath $INSTDIR
  
  ; Write the installation files
  File "distribution\SecureSubmissionSystem.exe"
  File "distribution\run_secure_submission_system.bat"
  File "distribution\README.txt"
  
  ; Create application shortcut
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\run_secure_submission_system.bat" "" "$INSTDIR\SecureSubmissionSystem.exe" 0
  CreateShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\run_secure_submission_system.bat" "" "$INSTDIR\SecureSubmissionSystem.exe" 0
  
  ; Write the uninstall keys
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\SecureSubmissionSystem.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${APPVERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
  
  ; Write the uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

; The uninstallation section
Section "Uninstall"
  ; Remove application files
  Delete "$INSTDIR\SecureSubmissionSystem.exe"
  Delete "$INSTDIR\run_secure_submission_system.bat"
  Delete "$INSTDIR\README.txt"
  Delete "$INSTDIR\uninstall.exe"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\Uninstall.lnk"
  Delete "$DESKTOP\${APPNAME}.lnk"
  RMDir "$SMPROGRAMS\${APPNAME}"
  
  ; Remove uninstall information
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
  DeleteRegKey HKLM "Software\${APPNAME}"
  
  ; Remove installation directory (if empty)
  RMDir "$INSTDIR"
SectionEnd