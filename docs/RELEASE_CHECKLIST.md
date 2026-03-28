# Release Checklist

## Before tagging
- [ ] App launches on a clean Windows machine
- [ ] Dependency scan behaves correctly
- [ ] Outdated `yt-dlp` warning is visible
- [ ] Analyze flow works on at least multiple supported sites
- [ ] Download flow works for video and audio-only cases
- [ ] Stop flow works without leaving broken UI state
- [ ] Remux flow is validated on at least one case
- [ ] `log.txt` and `logs/app.log` are created correctly
- [ ] No `__pycache__`, temp build leftovers, or personal paths remain
- [ ] README is current
- [ ] CHANGELOG is current
- [ ] LICENSE is included

## Packaging
- [ ] Portable `onedir` build created
- [ ] `tools/` binaries resolved correctly or documented clearly
- [ ] Zip package tested after extraction
- [ ] Release notes drafted
