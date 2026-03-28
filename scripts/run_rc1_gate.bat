@echo off
setlocal

cd /d "%~dp0\.."

echo [1/4] bootstrap_python_deps.bat
call scripts\bootstrap_python_deps.bat
if errorlevel 1 goto :fail

echo [2/4] run_pretest_checks.bat
call scripts\run_pretest_checks.bat
if errorlevel 1 goto :fail

echo [3/4] run_regression_suite.bat
call scripts\run_regression_suite.bat
if errorlevel 1 goto :fail

echo [4/4] run_multisite_validation.bat
call scripts\run_multisite_validation.bat
if errorlevel 1 goto :fail

echo.
echo RC1 gate passed.
exit /b 0

:fail
echo.
echo RC1 gate failed. Inspect output above.
exit /b 1
