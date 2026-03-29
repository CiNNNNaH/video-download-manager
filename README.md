# Video Download Manager (VDM)

Video Download Manager (VDM) is a portable-first Windows desktop downloader built around `yt-dlp` with a PySide6 GUI.

- **Product Version:** `VDM_v1.3.0`
- **Current Delivery Package:** `1.8`

## Versioning model
VDM uses two parallel identifiers:
- **Product version**: the active product line, currently `VDM_v1.3.0`
- **Package version**: delivery iterations inside the same product line, for example `1.0`, `1.1`, `1.2`, `1.3`, `1.4`, `1.5`, `1.6`, `1.7`, `1.8`

Integer package numbers are normalized in documentation as `.0` only when required by older history entries. The active `VDM_v1.3.0` line uses the simple `1.x` package sequence.

## What this build is expected to do
- detect Python and external-tool readiness
- analyze supported URLs through `yt-dlp`
- list formats in Simple and Advanced views
- download video+audio, video-only, and audio-only targets
- stop an in-progress download without freezing the UI
- remove temporary partial files after user-cancelled or failed downloads
- remember key GUI selections across restarts
- export session logging from startup to shutdown for troubleshooting

## Current line highlights
- English-first UI with Turkish language pack support
- Firefox-first browser-cookie handling with fallback enabled
- corrected Selected Format panel layout
- Advanced view enabled by default
- session log hardened from startup to shutdown
- cancelled/failed download temp-file cleanup enabled
- portable EXE `onedir` build foundation prepared
- portable EXE app icon integrated for window and executable branding
- portable EXE resource/verify contract aligned for app-root data and bundled resources
- portable EXE resource path, console suppression, dependency check, and verify fixes validated
- portable EXE verify timing/strictness aligned so first-build checks do not fail before app-root runtime data is created

## Known limits
- site behavior can still change without notice
- some sites require a fresh `yt-dlp` build or browser-session validation
- protected or age-gated content may still fail depending on browser/session state
- Instagram and similar sites may fail because of account/session/content restrictions even when the app itself is behaving correctly
- cookie-backed flows are environment-sensitive on Windows because browser database access and DPAPI behavior are not equally reliable across browsers
- some downloads may still depend on site-specific behavior even when analyze succeeds

## Requirements and supported tools

### Required runtime
- **Python 3.13+** (or the project-supported Python version in your environment)
- **Python packages from `requirements.txt`**

### Core external tools
- **yt-dlp**
- **ffmpeg**
- **deno**

### Optional or environment-dependent tools
- **winget** for some install/update flows on Windows
- local `tools/` copies of external binaries if you prefer portable bundling over system PATH

### Browser integration
Supported browser-cookie integrations:
- Firefox
- Chrome
- Brave
- Edge
- cookies disabled

These are not all hard dependencies for every scenario, but they matter for cookie-backed or protected content.

### Browser cookie reliability note
Current tested behavior in this project line:
- **Firefox** is the most reliable cookie-backed path in tested environments.
- **Edge** may work depending on local profile and DPAPI state.
- **Chrome** and **Brave** may fail in some Windows environments because of cookie-database access or DPAPI decryption issues.
- Keep browser fallback enabled and treat **Firefox** as the preferred recovery path.

## Media processing scope
- normal downloads may use remux when required
- optional FFmpeg re-encode actions are allowed in `VDM_v1.3.0`
- re-encode remains a separate, explicitly triggered helper action rather than the core default pipeline

## Quick start
Install Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Run validation helpers:

```bat
scripts
un_pretest_checks.bat
scripts
un_regression_suite.bat
scripts
un_multisite_validation.bat
```

Start the application:

```bash
python main.py
```

Do not launch the app with `app.py`.

## Recommended release order
1. `scripts\bootstrap_python_deps.bat`
2. `scripts\run_pretest_checks.bat`
3. `scripts\run_regression_suite.bat`
4. `scripts\run_multisite_validation.bat`
5. `python .\main.py`
6. Build the portable folder with the normal PyInstaller flow / `VDM.spec`
7. `scripts\clean_runtime_artifacts.bat`
8. `scripts\verify_portable_bundle.bat <portable_folder>`
9. `scripts\package_release_bundle.bat <portable_folder>`
10. `scripts\collect_support_bundle.bat <portable_folder>` when a support handoff archive is needed

## Documentation update rule
Every package that changes runtime behavior must also update:
- `README.md`
- `CHANGELOG.md`
- `PACKAGE_HISTORY.md`
- package note file(s)
- any version identifiers in settings or runtime-facing docs that changed with the package

## Important docs
- `docs\SESSION_LOGGING_CONTRACT.md`
- `docs\CURRENT_BEHAVIOR_CONTRACT.md`
- `docs\LOCALIZATION_CLOSURE_PRE_EXE_GATE.md`
- `docs\PACKAGE_1_5_RUNTIME_GATE.md`
- `docs\RELEASE_CANDIDATE_CLOSURE.md`
