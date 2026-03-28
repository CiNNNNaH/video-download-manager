## VDM_v1.2.0 line

### Package 1.0
**Status:** validated

- Opened the `VDM_v1.2.0` line from the stabilized `VDM_v1.1 / Package 19.0` baseline.
- Aligned repository metadata, docs, and in-app version strings for GitHub publishing.
- Added `.github` issue templates and pull-request template.
- No UI/layout or download-engine behavior changes were introduced.

## Archived VDM_v1.1 line

# PACKAGE HISTORY

This file is the consolidated package index across VDM product lines. The active line now starts at `VDM_v1.2.0 / Package 1.0`, while the full `VDM_v1.1` history remains below.

Status markers:
- validated: passed the user-facing test gate in this conversation
- repacked: same package line was rebuilt to fix packaging or integration problems
- rejected: package line was tested and not accepted as a working base
- superseded: kept for traceability but replaced by a later corrected package
- recovery: rollback-based rebuild after the failed Package 15 layout branch

Versioning note:
- `VDM_v1.2.0` is the active product version.
- `VDM_v1.1` remains the archived stabilization line.
- `Package x.y` is the delivery iteration inside that product line.
- Integer package numbers are normalized here as `.0` for readability and sorting.

## Package 7.0
Source: `PACKAGE_7_NOTES.md`
Status: superseded

- Launch-time dependency scan now respects `startup_dependency_check`.
- Manual dependency refresh still works regardless of that setting.
- Dependency reporting was tightened so `ffmpeg` no longer looks outdated just because no online latest-version comparison is available.

## Package 8.0
Source: `PACKAGE_8_NOTES.md`
Status: superseded

- Test-readiness and local execution hardening pass.
- `tests/internal_smoke_test.py` adds the project root into `sys.path`.
- Direct local test execution no longer breaks imports.

## Package 9.0
Source: `PACKAGE_9_NOTES.md`
Status: superseded

- Reanalysis hang fix and deeper trace logging.
- Layout pass on the early working UI.

## Package 9.4
Source: `PACKAGE_9_4_NOTES.md`
Status: superseded

- Container logic refinement.
- Better open-file behavior.
- Format list expansion.

## Package 9.5
Source: `PACKAGE_9_5_NOTES.md`
Status: superseded

- Format table brought closer to yt-dlp style.
- File size surfaced more clearly.
- Stop UX improved.

## Package 10.0
Source: `PACKAGE_10_NOTES.md`
Status: superseded

- Format table columns became draggable.
- Column widths became persistent across restarts.

## Package 11.0
Source: `PACKAGE_11_NOTES.md`
Status: superseded

- Stabilization, regression lock, and release-readiness pass.
- Working Package 10 flow frozen behind lightweight regression checks.

## Package 11.1
Source: `PACKAGE_11_1_NOTES.md`
Status: superseded

- `tests/settings_persistence_regression.py` aligned with current `AppSettings` field names.
- `default_browser` and `default_media_mode` coverage updated.

## Package 11.2
Source: `PACKAGE_11_2_NOTES.md`
Status: superseded

- `package10_flow_regression.py` aligned with current settings model names.
- Regression suite brought back into sync.

## Package 12.0
Source: `PACKAGE_12_NOTES.md`
Status: superseded

- Multi-site validation readiness.
- Final UI polish checklist handoff.

## Package 13.0
Source: `PACKAGE_13_NOTES.md`
Status: superseded

- RC1 build and final docs preparation.
- Portable bundle finalization groundwork.

## Package 13.1
Source: `PACKAGE_13_1_NOTES.md`
Status: superseded

- Optional external FFmpeg re-encode launcher added.
- Re-encode remained outside the main download pipeline.

## Package 13.2
Source: `PACKAGE_13_2_NOTES.md`
Status: superseded

- YouTube watch URL normalization.
- Enter-to-analyze workflow.
- Queued re-analyze behavior.

## Package 14.0
Source: `PACKAGE_14_NOTES.md`
Status: superseded

- Final release candidate lock and cleanup pass.
- Final gate and runtime artifact cleanup scripts added.

## Package 14.1
Source: `PACKAGE_14_1_NOTES.md`
Status: superseded

- `ffmpeg` local version normalization fixed.
- Regression added for normalized `ffmpeg` version parsing.

## Package 14.2
Source: `PACKAGE_14_2_NOTES.md`
Status: superseded

- Filename template UX rewritten.
- Default naming preset set to original title only.

## Package 14.3
Source: `PACKAGE_14_3_NOTES.md`
Status: superseded

- Filename preset mapping fixed for resolution and upload date preview.
- New analysis resets filename UI state to default.
- Manual filename input clears when leaving manual mode and on new analysis.

## Package 15.0
Status: rejected

- Stability Contract Pack line started here.
- This branch introduced the later layout regression chain and was not kept as the base.

## Package 15.1
Status: rejected

- Layout and dependency hotfix attempt.
- Improved some areas but did not close the layout regression.

## Package 15.2
Status: rejected

- Responsive layout compression attempt.
- Did not fully solve fullscreen and snap behavior.

## Package 15.3
Status: rejected

- Snap-responsive layout attempt.
- Reduced some overflow but introduced new responsive issues.

## Package 15.4
Status: rejected

- Adaptive layout refactor attempt.
- Scroll pressure improved, but core format/download areas broke.
- Triggered the rollback decision back to Final Release.

## Package 15R.0
Source: `PACKAGE_15R_0_NOTES.md`
Status: recovery, superseded

- Recovery line based on `VDM_v1.1_Final_Release`.
- Only low-risk, non-layout improvements were brought back.

## Package 15R.1
Source: `PACKAGE_15R_1_NOTES.md`
Status: recovery, superseded

- Selected format summary made single-line.
- Fallback default switched on by default.

## Package 15R.2
Source: `PACKAGE_15R_2_NOTES.md`
Status: recovery, validated

- Selected format summary row polish completed.
- Dependency update logging clarified with used binary path details.
- Served as the validated recovery baseline.

## Package 16.0
Source: `PACKAGE_16_NOTES.md`
Status: superseded

- Multi-site regression pack line introduced.
- Original build had a `UrlUtils` integration/import break and was not kept.

## Package 16.0 (repacked build)
Source: `PACKAGE_16_NOTES.md`
Status: validated, repacked

- `UrlUtils` integration fixed.
- `site_family` logging validated across YouTube, Vimeo, SoundCloud, X, TikTok, and an access-restricted Instagram case.

## Package 17.0
Source: `PACKAGE_17_NOTES.md`
Status: superseded

- Portable release discipline line introduced.
- Verification idea was correct, but packaging scripts were not yet reliable.

## Package 17.1
Source: `PACKAGE_17_1_NOTES.md`
Status: superseded

- Python-based release zip creation added.
- Core packaging logic worked, but batch wrapper remained broken.

## Package 17.2
Source: `PACKAGE_17_2_NOTES.md`
Status: validated

- Batch wrapper fixed.
- `verify_portable_bundle.bat` and `package_release_bundle.bat` both validated.
- This closed the Package 17 line.

## Package 18.0
Source: `PACKAGE_18_NOTES.md`
Status: superseded

- Operational hardening line introduced.
- Support bundle worked, but `PACKAGE_HISTORY.md` ordering remained messy.

## Package 18.1
Source: `PACKAGE_18_1_NOTES.md`
Status: validated

- `PACKAGE_HISTORY.md` order corrected.
- Recovery, repacked, rejected, and validated states clarified.
- No application logic, layout, or packaging behavior changed.

## Package 18.2
Source: `PACKAGE_18_2_NOTES.md`
Status: superseded

- Docs consistency work started.
- `.0` normalization, dependency categories, and encode-scope wording were improved, but package history normalization and requirement coverage were still incomplete.

## Package 19.0
Status: validated

- Release-candidate closure pass for the `VDM_v1.1` product line.
- No new feature scope added; this package consolidates docs, release order, requirements wording, and known limitations.
- Serves as the current closure baseline before any future `VDM_v1.2` planning.

## Package 18.3
Status: validated

- `.0` normalization applied consistently across `CHANGELOG.md` and `PACKAGE_HISTORY.md`.
- Requirements and supported tools clarified: Python runtime, Python packages, `ffmpeg`, `deno`, and optional Node.js note.
- Browser cookie reliability documented with Firefox as the preferred recovery path in current tested environments.


## VDM_v1.2.0 / Package 1.1 - GitHub Repo Cleanup
- Status: validated
- Purpose: minimize the GitHub-facing repository package before first upload.
- Changes: removed individual PACKAGE_*_NOTES.md files, removed __pycache__ and compiled artifacts, retained PACKAGE_HISTORY.md as the single package history reference.
