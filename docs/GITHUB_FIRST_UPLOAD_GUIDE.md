# GitHub first upload guide

This repository package is trimmed for first upload to GitHub.

## Keep in the repo
- source code
- docs
- scripts
- tests
- README.md
- CHANGELOG.md
- PACKAGE_HISTORY.md
- CONTRIBUTING.md
- LICENSE

## Intentionally excluded from the GitHub package
- individual PACKAGE_*_NOTES.md files
- __pycache__ folders
- .pyc / .pyo files
- generated release zips
- generated portable/support stage folders

## Recommended first upload path
1. Create an empty GitHub repository.
2. Upload the contents of this package to that repository.
3. Confirm that no generated artifacts or local caches were uploaded.
4. Add future release artifacts through GitHub Releases, not as tracked source files.
