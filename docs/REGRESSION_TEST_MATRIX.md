# Regression Test Matrix

Use this matrix when re-running the package on another Windows machine.

| Area | Case | Expected |
|---|---|---|
| Startup | main.py launch | main window opens |
| Dependencies | startup check | yt-dlp / ffmpeg visible |
| Analyze | public video | content + thumbnail + formats load |
| Re-analyze | clear then analyze second URL | no UI hang |
| Download | video+audio MP4 path | file downloads and opens |
| Download | audio only | audio file downloads |
| Stop | interrupt active download | no modal error, controlled stop |
| Persistence | restart app | selections remain |
| Table UX | move/resize columns | layout persists |
| Export | debug export script | zip created |
