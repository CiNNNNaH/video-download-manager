@echo off
setlocal

set "ROOT=%~dp0.."
echo Cleaning runtime artifacts under %ROOT% ...

if exist "%ROOT%\logs" (
  del /q "%ROOT%\logs\*" >nul 2>&1
) else (
  mkdir "%ROOT%\logs"
)

echo.> "%ROOT%\log.txt"
if exist "%ROOT%\data\history.json" (
  echo []> "%ROOT%\data\history.json"
)

echo Runtime artifacts cleaned.
echo - logs/ emptied
if exist "%ROOT%\data\history.json" echo - data/history.json reset to []
echo - root log.txt reset
exit /b 0
