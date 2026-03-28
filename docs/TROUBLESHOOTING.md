# Troubleshooting

## PySide6 not found
Run:

```bat
scriptsootstrap_python_deps.bat
```

## ffmpeg appears missing but is installed
Use the app's dependency check again. If the system copy is still not detected, place a portable binary under `toolsfmpeg` or make sure `ffmpeg.exe` is on `PATH`.

## Analysis fails with browser-cookie issues
- try Firefox if Chrome DPAPI decryption fails on the machine
- validate that the target browser profile is unlocked and currently usable
- update `yt-dlp` if site behavior changed

## Download stops or behaves unexpectedly
- rerun the same format once
- switch browser cookie source
- export a debug bundle with `scripts\export_debug_info.bat`

## Portable build issues
See `docs\PORTABLE_RELEASE_GUIDE.md` and `docs\BUILD.md`.
