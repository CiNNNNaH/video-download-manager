@echo off
setlocal
cd /d "%~dp0.."

echo [1/4] run_pretest_checks.bat
call "%~dp0run_pretest_checks.bat"
if errorlevel 1 goto :fail

echo [2/4] run_regression_suite.bat
call "%~dp0run_regression_suite.bat"
if errorlevel 1 goto :fail

echo [3/4] multisite_validation_stub.py
python tests\multisite_validation_stub.py
if errorlevel 1 goto :fail

echo [4/4] Manual multi-site checklist
echo Open docs\MULTI_SITE_VALIDATION_MATRIX.md and complete one real URL per relevant family.

echo.
echo Multi-site validation preparation completed.
exit /b 0
:fail
echo.
echo Multi-site validation preparation failed. Inspect output above.
exit /b 1
