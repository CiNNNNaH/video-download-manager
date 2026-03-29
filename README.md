# Video Download Manager (VDM)

Video Download Manager (VDM) is a portable-first Windows desktop downloader built around `yt-dlp` with a PySide6 GUI.

- **Product Version:** `VDM_v1.1`
- **Current Delivery Package:** `19.0`

## Versioning model
VDM uses two parallel identifiers:
- **Product version**: the main product line, currently `VDM_v1.1`
- **Package version**: delivery iterations inside the same product line, for example `15R.2`, `16.0`, `17.2`, `19.0`

Integer package numbers are normalized in documentation as `.0` for readability and sorting.

## What this build is expected to do
- detect Python and external-tool readiness
- analyze supported URLs through `yt-dlp`
- list formats in a user-friendly table
- download video+audio, video-only, and audio-only targets
- stop an in-progress download without freezing the UI
- remember the user's key GUI selections across restarts
- export debug information for troubleshooting

## Known limits
- site behavior can still change without notice
- some sites require a fresh `yt-dlp` build or browser-session validation
- protected or age-gated content may still fail depending on browser/session state
- Instagram and similar sites may fail because of account/session/content restrictions even when the app itself is behaving correctly
- cookie-backed flows are environment-sensitive on Windows because browser database access and DPAPI behavior are not equally reliable across browsers

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
- **Node.js** only if a specific helper or local environment script still depends on it
- local `tools/` copies of external binaries if you prefer portable bundling over system PATH

### Browser integration
Supported browser-cookie integrations:
- Chrome
- Brave
- Firefox
- Edge

These are not all hard dependencies for every scenario, but they matter for cookie-backed or protected content.

### Browser cookie reliability note
Current tested behavior in this project line:
- **Firefox** is the most reliable cookie-backed path in tested environments.
- **Edge** may work depending on local profile and DPAPI state.
- **Chrome** and **Brave** may fail in some Windows environments because of cookie-database access or DPAPI decryption issues.
- For cookie-backed flows, keep browser fallback enabled and treat **Firefox** as the preferred recovery path.

## Media processing scope
- normal downloads may use remux when required
- optional FFmpeg re-encode actions are allowed in `VDM_v1.1`
- re-encode must remain a separate, explicitly triggered helper action rather than becoming the core default pipeline

## Quick start
Install Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Run validation helpers:

```bat
scriptsun_pretest_checks.bat
scriptsun_regression_suite.bat
scriptsun_multisite_validation.bat
```

Start the application:

```bash
python main.py
```

Do not launch the app with `app.py`.

## Recommended release order
1. `scriptsootstrap_python_deps.bat`
2. `scriptsun_pretest_checks.bat`
3. `scriptsun_regression_suite.bat`
4. `scriptsun_multisite_validation.bat`
5. `python .\main.py`
6. Build your portable folder with your normal PyInstaller flow / `VDM.spec`
7. `scripts\clean_runtime_artifacts.bat`
8. `scriptserify_portable_bundle.bat <portable_folder>`
9. `scripts\package_release_bundle.bat <portable_folder>`
10. `scripts\collect_support_bundle.bat <portable_folder>` when you need a support handoff archive

## Release-candidate closure focus
This package does not add new product scope. It closes the `VDM_v1.1` line with:
- docs consistency pass
- known limitations documented honestly
- release checklist consolidation
- packaging and support-bundle workflows already validated in previous packages

## Support bundle
Use this when you need to send a compact troubleshooting package:

```bat
scripts\collect_support_bundle.bat "."
```

## Important docs
- `docs\FINAL_RELEASE_CHECKLIST.md`
- `docs\RELEASE_CANDIDATE_CLOSURE.md`
- `docs\MULTI_SITE_VALIDATION_MATRIX.md`
- `docs\OPERATIONAL_HARDENING.md`
- `docs\TROUBLESHOOTING.md`
- `PACKAGE_HISTORY.md`
- `CHANGELOG.md`

## Project layout
- `core/` business logic
- `gui/` desktop interface
- `services/` settings, logging, theme
- `models/` typed data models
- `data/` settings and history
- `logs/` detailed logs
- `tests/` sanity and regression checks
- `scripts/` helper, build, packaging, and support-bundle scripts
- `docs/` validation, release, and usage notes

## Warning
This project depends on third-party tools and extractor behavior that can change without notice. Keep `yt-dlp` current and validate protected or cookie-backed sites on the target machine.
