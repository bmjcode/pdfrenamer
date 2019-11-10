; This script builds the Windows installer for PDF Renamer.
;
; Requirements:
; PyInstaller (to build PDF Renamer)
; NSIS ZipDLL plug-in (to extract GhostXPS executables)
;
; Download Ghostscript 9.27 installer files to ghostscript/
; gs927w64.exe, ghostxps-9.27-win64.zip     (for 64-bit PDF Renamer)
; gs927w32.exe, ghostxps-9.27-win32.zip     (for 32-bit PDF Renamer)
;
; I'm sticking with this older version for now because Ghostscript 9.50
; had trouble rendering some of my real-world test files.
;
; Usage:
; makensis winsetup.nsi                     (builds 64-bit PDF Renamer)
; makensis /DPLATFORM=win32 winsetup.nsi    (builds 32-bit PDF Renamer)

; Sync this with config.py
!ifndef VERSION
  !define VERSION "1.1.0"
!endif

; This can be "win32" or "win64"
!ifndef PLATFORM
  !define PLATFORM "win64"
!endif

!if ${PLATFORM} == "win64"
  !define PYTHON "py -3.6"
  !define GS_SETUP "gs927w64.exe"
  !define GXPS_DIR "ghostxps-9.27-win64"
  InstallDir "$PROGRAMFILES64\PDF Renamer"

!else if ${PLATFORM} == "win32"
  !define PYTHON "py -3.6-32"
  !define GS_SETUP "gs927w32.exe"
  !define GXPS_DIR "ghostxps-9.27-win32"
  InstallDir "$PROGRAMFILES32\PDF Renamer"

!else
  !error "Platform must be one of 'win32' or 'win64'."

!endif

; ------------------------------------------------------------------------

Name "PDF Renamer"
OutFile "pdfrenamer-${VERSION}-${PLATFORM}.exe"
InstallDirRegKey HKLM "Software\Benjamin Johnson\PDF Renamer" ""
RequestExecutionLevel admin
XPStyle on

; ------------------------------------------------------------------------

Page components
Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

; ------------------------------------------------------------------------

Section "PDF Renamer"
  SectionIn RO

  ; Build the application
  !If ! /FileExists "dist\PDF Renamer\PDF Renamer.exe"
    !Execute '${PYTHON} -m PyInstaller --clean -w -D -n "PDF Renamer" run.py'
  !EndIf

  ; Include the application files
  SetOutPath $INSTDIR
  File /r "dist\PDF Renamer\*"

  !if ${PLATFORM} == "win64"
    SetRegView 64
  !else if ${PLATFORM} == "win32"
    SetRegView 32
  !endif

  ; Write the installation path into the registry
  WriteRegStr HKLM "Software\Benjamin Johnson\PDF Renamer" "" "$INSTDIR"

  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PDF Renamer" "DisplayName" "PDF Renamer"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PDF Renamer" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PDF Renamer" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PDF Renamer" "NoRepair" 1
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

SectionGroup "File format support"
  Section "PDF/PS support via Ghostscript"
    ; Extract the Ghostscript installer to a temporary location
    File "/oname=$TEMP\${GS_SETUP}" ghostscript\${GS_SETUP}

    ;; Installing Ghostscript in the application directory is a bad idea
    ;; because it will clobber the uninstall info in the registry if this
    ;; same Ghostscript version is already installed system-wide.
    ;CreateDirectory "$INSTDIR\Ghostscript"
    ;ExecWait '"$TEMP\${GS_SETUP}" /S /D=$INSTDIR\Ghostscript'

    ; Note the Ghostscript installer is itself an NSIS executable
    ExecWait '"$TEMP\${GS_SETUP}" /S'
    Delete "$TEMP\${GS_SETUP}"
  SectionEnd

  Section "XPS support via GhostXPS"
    ; Extract the GhostXPS ZIP file to a temporary location
    File "/oname=$TEMP\${GXPS_DIR}.zip" ghostscript\${GXPS_DIR}.zip

    ; The GhostXPS ZIP file contains a nested ghostxps-* subdirectory
    ZipDLL::extractall "$TEMP\${GXPS_DIR}.zip" "$INSTDIR"
    Delete "$TEMP\${GXPS_DIR}.zip"
  SectionEnd
SectionGroupEnd

SectionGroup "Create shortcuts"
  Section "Start menu shortcut"
    CreateShortcut "$SMPROGRAMS\PDF Renamer.lnk" "$INSTDIR\PDF Renamer.exe" "" "$INSTDIR\PDF Renamer.exe" 0
  SectionEnd

  Section "Desktop shortcut"
    CreateShortcut "$DESKTOP\PDF Renamer.lnk" "$INSTDIR\PDF Renamer.exe" "" "$INSTDIR\PDF Renamer.exe" 0
  SectionEnd
SectionGroupEnd

; ------------------------------------------------------------------------

Section "Uninstall"
  !if ${PLATFORM} == "win64"
    SetRegView 64
  !else if ${PLATFORM} == "win32"
    SetRegView 32
  !endif

  ;; Uninstall our local copy of Ghostscript
  ;ExecWait '"$INSTDIR\Ghostscript\uninstgs.exe" /S _?=$INSTDIR\Ghostscript'

  ; Delete registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PDF Renamer"
  DeleteRegKey HKLM "Software\Benjamin Johnson\PDF Renamer"

  ; Delete shortcuts
  Delete "$DESKTOP\PDF Renamer.lnk"
  Delete "$SMPROGRAMS\PDF Renamer.lnk"

  ; Delete application files
  RMDir /r "$INSTDIR\Include"
  RMDir /r "$INSTDIR\PIL"
  RMDir /r "$INSTDIR\tcl"
  RMDir /r "$INSTDIR\tk"
  RMDir /r "$INSTDIR\${GXPS_DIR}"
  Delete "$INSTDIR\PDF Renamer.exe"
  Delete "$INSTDIR\PDF Renamer.exe.manifest"
  Delete "$INSTDIR\base_library.zip"
  Delete "$INSTDIR\*.dll"
  Delete "$INSTDIR\*.pyd"
  Delete "$INSTDIR\uninstall.exe"

  ; Remove the application directory if it's empty
  RMDir "$INSTDIR"
SectionEnd

; vim: set sts=2 sw=2 et nowrap :
