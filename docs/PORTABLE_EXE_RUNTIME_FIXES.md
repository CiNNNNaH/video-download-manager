# Portable EXE Runtime Fixes

Package 1.5 fixes the first EXE runtime blockers:

- packaged resources are now loaded from the frozen bundle root
- writable runtime data stays under the EXE app root
- Windows subprocess checks use hidden console flags
- the build script now invokes PyInstaller via `python -m PyInstaller`


## Package 1.7 follow-up
- verify script now treats `data/settings.json` and `data/history.json` as writable app-root files instead of bundled `_internal/data` resources
- app icon assets are bundled and applied both at build time and at runtime
