# Current Behavior Contract

This document defines the intended behavior for the active VDM_v1.1 stabilization line.

## 1. Scope
- VDM is a `yt-dlp` GUI wrapper for supported sites.
- It is not guaranteed to work equally well on every supported site.
- The minimum product promise is controlled behavior, useful logs, and honest error reporting.

## 2. Dependency contract
- Startup checks must classify each managed dependency as `ready`, `outdated`, `critical_outdated`, `missing`, or `error`.
- `yt-dlp` is the most critical dependency. Missing or stale `yt-dlp` must be highlighted clearly.
- Dependency resolution order is: portable tool -> custom path -> system PATH.
- After install/update actions, VDM must run verification again.

## 3. Browser / cookie contract
- Browser choices are `chrome`, `brave`, `firefox`, `edge`, `cookies kapali`.
- `cookies kapali` means VDM will not request browser cookies.
- If fallback is enabled, VDM may try additional browsers after the selected browser fails.
- Browser fallback is an analysis/download recovery mechanism, not a promise that protected content will work.

## 4. Download pipeline contract
- Main pipeline does not perform full re-encode.
- Remux is allowed only when needed and enabled.
- External FFmpeg re-encode remains a separate helper action launched outside the main pipeline.
- A failed optional re-encode must not block normal VDM usage.

## 5. Filename contract
- New analysis resets the filename controls to the default preset.
- Manual filename mode is local to the current selection state and must not leak unexpectedly into later analyses.
- Preview text must reflect the active template, selected format, and selected target container as closely as possible.

## 6. Format table contract
- The first valid result row should be selected automatically after a successful analysis.
- The summary panel must describe the selected row without forcing advanced-only knowledge on the user.
- Simple vs advanced view changes must not silently corrupt the selected download meaning.

## 7. Logging / errors contract
- Errors shown to the user must map to a real classification, not a fake generic label unless no better mapping exists.
- Logs must capture dependency source, browser mode, fallback mode, selected format, output container, and final result state.
- Troubleshooting should be possible from exported logs without forcing the user into manual guesswork first.


## 15R.2 Validation Notes
- Dependency update akisi saha testinde dogrulandi: `yt-dlp` ve `deno` downgrade sonrasi uygulama ici guncelleme ile tekrar `ready` durumuna donebildi.
- Runtime loglari update/verify sonucunda kullanilan binary yolunu `resolved_path=` alaniyla gostermelidir.
- Secili format ozeti tek satir yuksekliginde kalmali; tam metin tooltip icinde korunur.
