@echo off
setlocal
if "%~1"=="" goto :usage
python "%~dp0package_release_bundle.py" "%~1"
exit /b %errorlevel%

:usage
echo Usage: package_release_bundle.bat ^<project_or_portable_folder^>
exit /b 1
