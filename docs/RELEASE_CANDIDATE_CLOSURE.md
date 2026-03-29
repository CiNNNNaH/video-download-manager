# Release Candidate Closure

This document closes the `VDM_v1.1` line at the package level.

## Scope of Package 19.0
- no new product features
- no UI or layout rework
- no download-pipeline changes
- no new encode/transcode scope
- documentation, release order, and operational closure only

## Closure checklist
1. Dependency detection works and reports `yt-dlp`, `ffmpeg`, and `deno` honestly.
2. Analyze flow works on the current baseline sites.
3. Download flow works on the validated baseline sites.
4. Browser fallback stays enabled by default.
5. `verify_portable_bundle.bat` passes.
6. `package_release_bundle.bat` produces the release zip.
7. `collect_support_bundle.bat` produces the support zip.
8. `README.md`, `CHANGELOG.md`, `PACKAGE_HISTORY.md`, and `CONTRIBUTING.md` agree on scope and versioning.

## Known realities carried forward
- Firefox is the preferred cookie-backed recovery path.
- Edge may work but is less predictable than Firefox.
- Chrome and Brave can fail because of cookie-database access or DPAPI issues.
- Protected or restricted content can still fail even when the app is behaving correctly.
- Re-encode remains optional and explicitly triggered; it is not part of the default pipeline.

## Exit condition
When a future package introduces a true product-level milestone rather than more `v1.1` hardening, open a new product version such as `VDM_v1.2`.
