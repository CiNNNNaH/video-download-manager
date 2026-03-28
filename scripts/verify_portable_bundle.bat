@echo off
setlocal
if "%~1"=="" (
  echo Usage: verify_portable_bundle.bat ^<portable_output_folder^>
  exit /b 1
)
python "%~dp0verify_portable_bundle.py" "%~1"
exit /b %errorlevel%
