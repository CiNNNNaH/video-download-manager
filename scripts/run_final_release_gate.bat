@echo off
setlocal

echo [1/4] run_pretest_checks.bat
call "%~dp0run_pretest_checks.bat" || goto :fail

echo [2/4] run_regression_suite.bat
call "%~dp0run_regression_suite.bat" || goto :fail

echo [3/4] run_multisite_validation.bat
call "%~dp0run_multisite_validation.bat" || goto :fail

echo [4/4] final release checklist stub
python "%~dp0..\tests\final_release_stub.py" || goto :fail

echo.
echo Final release gate passed.
exit /b 0

:fail
echo.
echo Final release gate failed. Inspect output above.
exit /b 1
