# Portable EXE Build Foundation

## Objective
Establish a predictable portable `onedir` EXE build path for the active `VDM_v1.3.0` line without changing core product behavior.

## Decisions fixed in this package
- Build type: **PyInstaller onedir**
- Primary executable name: **VDM.exe**
- Distribution style: **portable folder zipped for delivery**
- Installer: **not included**
- Onefile build: **not used**

## Runtime contract
- Source mode root: project folder
- Frozen mode root: folder containing `VDM.exe`
- Runtime directories created on startup: `data/`, `logs/`, `tools/`
- Locales and docs are treated as build-time data assets and included in the bundle

## Portable bundle minimum contents
- `VDM.exe`
- `data/settings.json`
- `data/history.json`
- `locales/en.json`
- `locales/tr.json`
- `README.md`
- `CHANGELOG.md`
- `PACKAGE_HISTORY.md`
- `LICENSE`

## Tool resolution order
1. Portable bundled tool
2. Custom configured path
3. System PATH

Applies to `yt-dlp`, `ffmpeg`, and `deno`.

## Build workflow
1. Install PyInstaller in the active Python environment
2. Run `scripts/build_portable_exe.bat`
3. Let `scripts/verify_portable_exe_bundle.py` validate the output
4. Test the resulting `dist/VDM` folder directly before any release packaging

## Limits of this package
This package prepares the build foundation but does **not** claim a validated EXE release. That requires an actual PyInstaller build and runtime validation on Windows.
