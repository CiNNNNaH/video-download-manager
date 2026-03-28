# Portable Bundle Structure

Expected top-level structure for a portable candidate:

- `README.md`
- `CHANGELOG.md`
- `LICENSE`
- `log.txt`
- `release_manifest.json` _(generated during verification)_
- `docs/`
- `data/`
- `logs/`
- application binaries / onedir output

## Rules
- `logs/` should exist but be empty in the release candidate
- `log.txt` should exist in the root and be reset before packaging
- `data/history.json` should be empty or absent
- `data/settings.json` may exist with defaults, but it should not contain stale personal paths
- no `__pycache__`, `.pyc`, `.pyo`, or temporary build leftovers should ship

## Practical note
The exact binary layout depends on your PyInstaller/onedir output. Package 17 does not force one binary layout; it forces a clean handoff layout.
