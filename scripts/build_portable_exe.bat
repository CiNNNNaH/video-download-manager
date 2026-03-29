@echo off
setlocal
cd /d "%~dp0\.."

echo [VDM] Portable EXE build foundation
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
  echo PyInstaller is not installed in the active Python environment.
  echo Install it first, then rerun this script.
  exit /b 1
)

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

python -m PyInstaller --noconfirm VDM.spec
if errorlevel 1 (
  echo PyInstaller build failed.
  exit /b 1
)

python scripts\verify_portable_exe_bundle.py dist\VDM
if errorlevel 1 (
  echo Portable bundle verification failed.
  exit /b 1
)

echo Portable EXE build foundation completed.
exit /b 0
