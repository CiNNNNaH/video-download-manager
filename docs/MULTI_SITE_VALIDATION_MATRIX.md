# Multi-Site Validation Matrix

Use this matrix for real Windows validation before any new release candidate. The goal is not to prove that every yt-dlp site behaves perfectly. The goal is to prove that VDM behaves predictably across the main site families it claims to support.

## Validation rules
- Record the exact URL tested.
- Record selected browser mode and whether fallback was enabled.
- Record whether analysis succeeded, whether the table stayed readable, and whether download finished without UI hang.
- Record the final extension and whether remux changed the container.
- Record the browser actually used when fallback succeeds.
- Record the most useful log lines around analyze start, analyze finish, download start, download finish, and fallback.

## Site-family matrix
| Family | Example target | Analyze | Download | Cookies expectation | Remux expectation | Minimum pass condition | Status |
|---|---|---|---|---|---|---|---|
| youtube | public single video | Required | Required | Works with cookies off for public URLs; browser mode must still behave predictably | mp4 remux path must remain valid for DASH video+audio | analyze success, readable formats, final file playable | Pending |
| youtube | cookie-sensitive / age-gated / login-sensitive | Required | Required when access is allowed | browser mode and fallback chain must be visible in logs | no false container claim | correct error or successful fallback | Pending |
| youtube | long video / post-live / large DASH | Required | Required | same as above | verify merge/remux and no UI hang | download completes and output extension matches rule | Pending |
| soundcloud or audio-first | audio-oriented page | Required | Required | cookies usually not required | keep-original and audio-only behavior must stay correct | audio-only result is correct and opens cleanly | Pending |
| vimeo | public hosted video | Required | Required | cookies optional depending on page | remux only when user requested | analyze + download without table corruption | Pending |
| x / twitter | direct media tweet/post | Required | Required if media is available | browser mode may matter; fallback must be visible | keep-original unless explicit remux | analysis should not hang on embed/post pages | Pending |
| instagram | public reel/post | Required | Required if accessible | browser mode likely matters; fallback must be visible | keep-original unless explicit remux | clear success or clear cookie/access error | Pending |
| tiktok | public video | Required | Required | cookies optional on many public posts but browser path must stay stable | keep-original unless explicit remux | stable analyze and final file written | Pending |
| facebook | public watch/post | Required | Required if accessible | browser mode often matters | keep-original unless explicit remux | clear success or clear access error | Pending |
| generic extractor-supported site | one representative URL | Required | Optional if analysis succeeds | depends on site | depends on source/container | no UI hang and usable logs | Pending |

## What to record for each test
- URL
- Site family
- Selected browser mode
- Fallback on/off
- Used browser after fallback
- Selected format id
- Media mode
- Target container
- Remux enabled true/false
- Final output path
- Final output extension
- Whether Open File opened the file itself
- Whether Stop stayed silent / non-modal
- Any key log lines

## Pass gate
A test is pass only when all of the following are true:
1. analysis succeeds or fails with a correct, useful classified error
2. the format table remains readable and selectable
3. download result matches the selected container / remux rule
4. fallback behavior is visible when enabled
5. no UI hang occurs
6. logs are usable for debugging
