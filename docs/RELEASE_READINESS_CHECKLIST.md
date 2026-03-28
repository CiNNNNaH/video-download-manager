# Release Readiness Checklist

Run this checklist before calling the build stable for wider testing.

## Local validation
- bootstrap Python dependencies
- pretest checks pass
- regression suite passes
- application starts from `main.py`

## Core user flow
- analyze one public video
- clear form and analyze a second public video
- download one `video+audio` result to MP4
- download one `audio only` result
- stop one active download without UI freeze

## Persistence
- cookie source survives restart
- media mode survives restart
- container survives restart
- remux survives restart
- fallback survives restart
- format table column order survives restart
- format table column widths survive restart

## Logging / export
- `log.txt` exists in package root
- detailed log exists under `logs/app.log`
- `scripts/export_debug_info.bat` produces a zip

## Known environment-sensitive items
- Chrome cookie decrypt / DPAPI can fail depending on the Windows/browser state
- source throughput is not a pure app-level guarantee
