# Final Release Checklist

## Gate checks
- Run `scripts\bootstrap_python_deps.bat`
- Run `scripts\run_pretest_checks.bat`
- Run `scripts\run_regression_suite.bat`
- Run `scripts\run_multisite_validation.bat`
- Run `scripts\run_final_release_gate.bat`

## Manual validation
- Launch `python .\main.py`
- Analyze one public YouTube URL
- Download one MP4-compatible `video+audio` selection
- Download one `audio-only` selection
- Confirm browser fallback still works on at least one cookie-sensitive case
- Confirm `Dosyayi Ac` and `Klasoru Ac` both work

## Portable bundle discipline
- Build the portable folder
- Run `scripts\clean_runtime_artifacts.bat`
- Run `scripts\verify_portable_bundle.bat <portable_folder>`
- Confirm `release_manifest.json` was generated
- Run `scripts\package_release_bundle.bat <portable_folder>`
- Extract the resulting zip into a clean folder and smoke test launch

## Release review
- Confirm README is current
- Confirm CHANGELOG is current
- Confirm latest package notes are included
- Confirm zip package name is ASCII-only
