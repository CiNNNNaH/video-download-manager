# GitHub Release Preparation

This document defines the repository-prep scope for `VDM_v1.2.0 / Package 1.0`.

## Goals
- keep the stabilized `v1.1` behavior intact while opening the `v1.2.0` line
- prepare the repository for first public upload
- avoid EXE-specific changes in this package

## Repository include list
- source code
- docs
- scripts
- tests
- README.md
- CHANGELOG.md
- PACKAGE_HISTORY.md
- CONTRIBUTING.md
- LICENSE
- SECURITY.md
- requirements.txt
- .gitignore
- .github templates

## Repository exclude list
- `__pycache__/`
- `*.pyc`, `*.pyo`
- generated release zips
- portable stage folders
- support bundle zips and stage folders
- machine-specific logs and local artifacts

## Not in scope
- portable EXE build
- major UI/layout changes
- new download-engine features
