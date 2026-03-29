# Localization Closure Pre-EXE Gate

## Scope
- Remove remaining mixed Turkish/English user-facing literals from the main window flow
- Normalize re-encode helper CMD strings through the locale layer
- Close known localization regressions before any EXE packaging work
- Keep layout unchanged

## Closed in Package 1.4
- Main window remaining mixed literals moved behind i18n keys
- History placeholder comparison normalized
- Re-encode button label normalized
- Container label normalized
- Thumbnail failure UI text normalized
- Output and stop-request log text normalized
- Known typo regressions fixed (`fself`, cancelled-state check)

## Pre-EXE Gate Result
Localization is now clean enough to stop mixing Turkish and English in the active main UI flow.
A final EXE phase can proceed only after runtime validation on the updated source package.
