@echo off
setlocal
cd /d %~dp0\..

if exist debug_export rd /s /q debug_export
if exist debug_export.zip del /f /q debug_export.zip
mkdir debug_export
mkdir debug_export\diagnostics

if exist log.txt copy /y log.txt debug_export\log.txt >nul
if exist logs\app.log copy /y logs\app.log debug_export\app.log >nul
if exist data\settings.json copy /y data\settings.json debug_export\settings.json >nul
if exist data\history.json copy /y data\history.json debug_export\history.json >nul
if exist docs\CONTROLLED_USER_TEST_PLAN.md copy /y docs\CONTROLLED_USER_TEST_PLAN.md debug_export\CONTROLLED_USER_TEST_PLAN.md >nul
if exist PACKAGE_9_NOTES.md copy /y PACKAGE_9_NOTES.md debug_export\PACKAGE_9_NOTES.md >nul

echo VDM debug export > debug_export\diagnostics\summary.txt
echo Timestamp: %date% %time%>> debug_export\diagnostics\summary.txt
echo Root: %cd%>> debug_export\diagnostics\summary.txt
echo.>> debug_export\diagnostics\summary.txt

echo ==== python ==== > debug_export\diagnostics\python_version.txt
python --version >> debug_export\diagnostics\python_version.txt 2>&1
where python >> debug_export\diagnostics\python_version.txt 2>&1

echo ==== yt-dlp ==== > debug_export\diagnostics\yt_dlp_version.txt
yt-dlp --version >> debug_export\diagnostics\yt_dlp_version.txt 2>&1
where yt-dlp >> debug_export\diagnostics\yt_dlp_version.txt 2>&1

echo ==== ffmpeg ==== > debug_export\diagnostics\ffmpeg_version.txt
ffmpeg -version >> debug_export\diagnostics\ffmpeg_version.txt 2>&1
where ffmpeg >> debug_export\diagnostics\ffmpeg_version.txt 2>&1

echo ==== deno ==== > debug_export\diagnostics\deno_version.txt
deno --version >> debug_export\diagnostics\deno_version.txt 2>&1
where deno >> debug_export\diagnostics\deno_version.txt 2>&1

echo ==== systeminfo ==== > debug_export\diagnostics\systeminfo.txt
systeminfo >> debug_export\diagnostics\systeminfo.txt 2>&1

echo ==== PATH ==== > debug_export\diagnostics\path.txt
echo %PATH%>> debug_export\diagnostics\path.txt

dir /s /b tools > debug_export\diagnostics\tools_tree.txt 2>&1
dir /s /b scripts > debug_export\diagnostics\scripts_tree.txt 2>&1

powershell -NoProfile -Command "Compress-Archive -Force -Path 'debug_export\*' -DestinationPath 'debug_export.zip'"

echo debug_export.zip hazirlandi.
echo Kullanici test raporuna eklemeden once settings.json ve loglari gozden gecir.
pause
