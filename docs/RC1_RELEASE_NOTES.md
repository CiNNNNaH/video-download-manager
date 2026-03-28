# RC1 Release Notes

## Summary
RC1 is the first package intended for controlled release-candidate testing.

## Included capabilities
- dependency detection for Python packages and external tools
- browser-cookie-aware analysis flow
- re-analysis without the prior UI hang
- download stop/cancel handling
- container/remux fixes for MP4-oriented flows
- file-open and folder-open separation
- format-table customization and persistence
- pretest, regression, and multi-site validation helper scripts

## Recommended RC1 test focus
- one public YouTube video
- one larger DASH-based YouTube video
- one audio-only download
- one stop/cancel run
- one restart-and-settings-persistence check
- one portable build packaging pass

## Ship / hold rule
Ship RC1 only after:
- `run_pretest_checks.bat` passes
- `run_regression_suite.bat` passes
- `run_multisite_validation.bat` passes
- the GUI opens and core download flows behave normally on the target Windows machine
