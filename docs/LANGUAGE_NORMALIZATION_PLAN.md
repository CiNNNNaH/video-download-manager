# Language Normalization and i18n Foundation

## Phase objective
Normalize the application to an English-first UI baseline, then add Turkish as a language pack without changing the core workflow.

## Immediate scope
- add persistent `language` setting
- add locale dictionaries (`locales/en.json`, `locales/tr.json`)
- add centralized `I18nService`
- convert the settings dialog and dependency setup dialog to translation-based text
- switch the main UI baseline to English-first labels and status text
- keep layout and download logic intact

## Risk control
- no aggressive UI refactor
- no EXE build work in this package
- no feature expansion
- keep rollback easy by isolating language work

## Next pass after this package
- sweep remaining hardcoded strings in downloader/analyzer/status logs
- expand translation coverage for deeper runtime messages
- add regression checks for language persistence and mixed-text detection
