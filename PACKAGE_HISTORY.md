# Package History

This file is the consolidated package index for the active `VDM_v1.3.0` line and retains the older `VDM_v1.1` history for reference.

## Current product line rules
- `VDM_v1.3.0` is the active product version.
- Package numbers in the active line are tracked as `1.0`, `1.1`, `1.2`, `1.3`, and so on.
- Every package that changes runtime behavior must also update the main documentation identity (`README.md`, `CHANGELOG.md`, `PACKAGE_HISTORY.md`, relevant package notes, and version-facing docs/settings where applicable).

## Active line: VDM_v1.3.0

### Package 1.3
- documentation and version identity sync
- repo/package identity corrected to reflect the active `VDM_v1.3.0` line
- documentation-update rule formalized for future packages

### Package 1.2
- temp-file cleanup after cancelled or failed downloads
- target folders now keep completed outputs only

### Package 1.1
- Firefox-first browser-cookie handling for download fallback
- logging unification and stop-control improvements

### Package 1.0
- session logging hardening foundation
- startup-to-shutdown structured trace coverage

---

The older `VDM_v1.1` package history is retained below.

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
