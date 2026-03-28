@echo off
setlocal
set TARGET=%~1
if "%TARGET%"=="" set TARGET=.
python "%~dp0collect_support_bundle.py" "%TARGET%"
endlocal
