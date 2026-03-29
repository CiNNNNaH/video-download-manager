# Language Sweep Phase 2 Notes

This package continues the English-first normalization.

## Scope
- Remove remaining mixed Turkish/English runtime text from core GUI flows
- Normalize download stage labels to English in the source base
- Keep Turkish in the language pack only
- Fix SetupDialog startup wiring to use the i18n service correctly

## Intentional non-goals
- No layout refactor
- No EXE build changes
- No new downloader features

## Known remaining areas for later sweep
- Deeper technical diagnostics in logs can stay English-only
- Any future new UI text must be added to locale files first
