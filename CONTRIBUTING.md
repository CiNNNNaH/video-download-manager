# Contributing

This repository is still in an early structured build-out phase.

## Ground rules
- Keep the project portable-first.
- Keep Windows as the primary target unless a change is explicitly cross-platform safe.
- Prefer practical fixes over speculative abstractions.
- Do not weaken dependency freshness checks.
- In `VDM_v1.1`, do **not** turn encode/transcode into the core download pipeline.
- Remux may remain part of the normal flow when needed.
- Optional FFmpeg re-encode actions may exist, but they must stay **separate, explicitly triggered, non-blocking helper actions** rather than becoming the default processing path.
- Document browser-cookie reality honestly. In current tested environments, Firefox is the most reliable cookie-backed path; Edge may work; Chrome and Brave may fail because of cookie database or DPAPI issues.

## Development flow
1. Create a focused branch.
2. Make a small, testable change.
3. Run a local syntax check.
4. Update `CHANGELOG.md` when the change is meaningful.
5. Include logs or reproduction notes for bug fixes.

## Recommended local check
```bash
python -m compileall .
```

## Bug reports
Use the issue templates. Include:
- VDM product version
- delivery package number
- Python version
- `yt-dlp` version
- `ffmpeg` presence/version
- `deno` presence/version
- target site
- minimal reproduction steps
- relevant log excerpt

## Package versioning
- Keep the product version and package version separate in docs and notes.
- Use `.0` for integer package numbers in documentation (`16.0`, `17.0`, `18.0`, `19.0`).
