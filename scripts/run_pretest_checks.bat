@echo off
setlocal
cd /d %~dp0\..

echo [0/4] Python dependency import check
python tests\verify_python_dependencies.py
if errorlevel 1 goto :fail

echo [1/4] internal_smoke_test.py
python tests\internal_smoke_test.py
if errorlevel 1 goto :fail

echo [2/4] pretest_core_checks.py
python tests\pretest_core_checks.py
if errorlevel 1 goto :fail

echo [3/4] local_runtime_sanity.py
python tests\local_runtime_sanity.py
if errorlevel 1 goto :fail

echo.
echo Tum pretest kontrolleri gecti.
pause
exit /b 0

:fail
echo.
echo Pretest kontrolu basarisiz. Yukaridaki ciktiyi incele.
echo Gerekirse once scripts\bootstrap_python_deps.bat calistir.
pause
exit /b 1
