@echo off
setlocal
cd /d "%~dp0.."

echo [1/9] pretest_core_checks.py
python tests\pretest_core_checks.py || goto :fail

echo [2/9] settings_persistence_regression.py
python tests\settings_persistence_regression.py || goto :fail

echo [3/9] package10_flow_regression.py
python tests\package10_flow_regression.py || goto :fail

echo [4/9] dependency_contract_regression.py
python tests\dependency_contract_regression.py || goto :fail

echo [5/9] browser_cookie_contract_regression.py
python tests\browser_cookie_contract_regression.py || goto :fail

echo [6/9] error_taxonomy_regression.py
python tests\error_taxonomy_regression.py || goto :fail

echo [7/9] bootstrap_action_contract_regression.py
python tests\bootstrap_action_contract_regression.py || goto :fail

echo.
echo [8/9] dependency_path_logging_regression.py
python tests\dependency_path_logging_regression.py || goto :fail

echo [9/9] multisite_site_family_regression.py
python tests\multisite_site_family_regression.py || goto :fail

echo.
echo Regression suite passed.
goto :end

:fail
echo.
echo Regression suite failed. Inspect output above.
exit /b 1

:end
endlocal

python tests\support_bundle_regression.py
if errorlevel 1 goto :fail
