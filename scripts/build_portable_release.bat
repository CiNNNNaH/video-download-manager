@echo off
setlocal

echo [1/4] Running pretest checks...
call "%~dp0run_pretest_checks.bat" || exit /b 1

echo [2/4] Running regression suite...
call "%~dp0run_regression_suite.bat" || exit /b 1

echo [3/4] Running multi-site validation helper...
call "%~dp0run_multisite_validation.bat" || exit /b 1

echo [4/4] Ready for portable build.
echo Build your portable folder with your normal PyInstaller flow or VDM.spec.
echo Then run:
echo   scripts\clean_runtime_artifacts.bat
echo   scripts\verify_portable_bundle.bat ^<portable_folder^>
echo   scripts\package_release_bundle.bat ^<portable_folder^>
exit /b 0
