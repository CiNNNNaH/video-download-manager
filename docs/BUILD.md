# Build Notes

## Target
First official target: **Windows portable onedir build**.

## Recommended flow
1. Create a clean virtual environment
2. Install Python dependencies
3. Install PyInstaller
4. Run the build script
5. Validate the output from a fresh extracted folder

## Commands
```bash
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

```bat
scripts\build_portable.bat
```

## External tools
For portable use, place binaries in:
- `tools\ffmpeg\ffmpeg.exe`
- `tools\ffmpeg\ffprobe.exe`
- `tools\deno\deno.exe`

VDM should prefer local portable binaries before falling back to system `PATH`.

## Important
The build script is not proof of release quality. A clean-machine validation pass is mandatory.
