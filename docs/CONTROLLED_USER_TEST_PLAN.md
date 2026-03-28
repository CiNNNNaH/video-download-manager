# Controlled User Test Plan

Run these steps on Windows from the current package folder.

## Phase 1 - Baseline sanity
1. Launch the app.
2. Verify dependency summary renders without false warnings.
3. Verify fallback default state is what the package notes expect.
4. Verify the selected media summary row stays single-line and does not overlap the table.

## Phase 2 - YouTube baseline
1. Test one public YouTube URL with cookies off.
2. Test one browser-cookie path with fallback off.
3. Repeat with fallback on and record the used browser.
4. Download one video+audio DASH case and one audio-only case.

## Phase 3 - Multi-site sweep
Use docs/MULTI_SITE_VALIDATION_MATRIX.md and test at least one representative URL from each relevant family available to you. Prioritize real URLs over synthetic samples.

## Phase 4 - Release closure evidence
Record:
- package name
- date and Windows version
- browser mode used
- whether fallback was used
- final output extension
- log lines proving analyze start/finish and download start/finish

## Stop conditions
Stop and report immediately if any of the following happen:
- table corruption or overlap returns
- browser fallback becomes invisible
- remux output extension mismatches the selected rule
- UI hang or forced close
