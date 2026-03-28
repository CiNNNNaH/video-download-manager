@echo off
setlocal
cd /d %~dp0\..

echo Installing Python dependencies from requirements.txt ...
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Python dependency installation failed.
  pause
  exit /b 1
)

echo.
echo Python dependencies installed successfully.
pause
exit /b 0
