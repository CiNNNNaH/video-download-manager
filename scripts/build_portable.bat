@echo off
setlocal
cd /d %~dp0\..

python -m pip install -r requirements.txt
python -m pip install pyinstaller

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

pyinstaller VDM.spec --noconfirm

echo.
echo Build tamamlandi. Cikti klasoru: dist\VDM
pause
