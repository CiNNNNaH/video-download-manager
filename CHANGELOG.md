## VDM_v1.2.0 / Package 1.0 - GitHub Release Prep
- opened the `VDM_v1.2.0` product line from the stabilized `VDM_v1.1 / Package 19.0` baseline
- aligned in-app version metadata and default settings to `VDM_v1.2.0`
- added GitHub issue templates, pull-request template, and repository support files
- kept UI, analyze/download behavior, packaging, and support-bundle flow unchanged

# Changelog

This file tracks user-facing product changes across VDM product lines. Historical v1.1 entries are preserved below the v1.2.0 baseline reset.

- `VDM_v1.2.0` starts from the stabilized `VDM_v1.1 / Package 19.0` baseline.
- Package numbering restarts inside the new product line.
- **Package numbers** are delivery iterations inside the same product line.
- Integer package numbers are normalized in documentation as `.0` for readability and sorting.

## VDM_v1.1 / Package 19.0 - Release Candidate Closure Pack
- consolidated release-candidate guidance and final release closure notes
- clarified known limits, cookie-browser reality, and support-bundle usage in the main README
- normalized `requirements.txt` comments so Python-package scope and external-tool scope are separated cleanly
- kept product scope fixed: no new UI/layout/download features, only release closure and documentation hardening

## VDM_v1.1 / Package 18.3 - Docs, Requirements, and Cookie Reality Fix
- aligned `.0` normalization across `CHANGELOG.md` and `PACKAGE_HISTORY.md`
- clarified that Python is a required runtime for this distribution model
- restored `ffmpeg` and `deno` to the documented tool requirements
- kept Node.js out of the core requirement list and marked it optional/environment-dependent
- documented current browser-cookie reliability reality: Firefox strongest, Edge conditional, Chrome and Brave unreliable on some Windows setups

## VDM_v1.1 / Package 18.2 - Docs Consistency Fix
- aligned `CHANGELOG.md`, `PACKAGE_HISTORY.md`, `README.md`, and `CONTRIBUTING.md`
- clarified product-version vs package-version rules
- normalized integer package references in docs as `.0`
- clarified dependency categories and encode/remux/re-encode scope language

## VDM_v1.1 / Package 18.1 - Package History Order Fix
- corrected `PACKAGE_HISTORY.md` ordering and status labels

## VDM_v1.1 / Package 18.0 - Operational Hardening Pack
- added support-bundle collection scripts for troubleshooting handoff
- consolidated package-note tracking into `PACKAGE_HISTORY.md`
- added operational hardening documentation

## VDM_v1.1 / Package 17.2 - Batch Wrapper Fix
- fixed portable release packaging batch wrapper for quoted paths with spaces and parentheses

## VDM_v1.1 / Package 17.1 - Portable Release Packaging Fix
- moved release zip creation into Python for more reliable packaging behavior

## VDM_v1.1 / Package 17.0 - Portable Release Discipline Pack
- added portable bundle verification and release staging workflow
- tightened runtime artifact cleanup and release-manifest generation

## VDM_v1.1 / Package 16.0 - Multi-Site Regression Pack
- added site-family classification and logging for analyze/download flows
- expanded multi-site validation guidance and regression coverage
- validated YouTube, Vimeo, SoundCloud, X, TikTok; documented Instagram restricted-content behavior

## VDM_v1.1 / Recovery Line (15R.x)
### Package 15R.2 - Dependency Closure + Row Polish
- fixed selected-media summary row overflow
- added dependency resolved-path logging

### Package 15R.1 - UI Polish + Defaults
- made browser fallback default to enabled
- reduced selected-media summary to a single-line presentation

### Package 15R.0 - Safe Recovery
- rolled back to the validated final-release base after failed Package 15 layout attempts
- reintroduced safe dependency/fallback/error-taxonomy improvements without layout regressions

## VDM_v1.1 / Failed and superseded Package 15 line
### Package 15.4 - Adaptive Layout Refactor
- attempted tabbed/adaptive layout approach
- rejected because critical format/download UI sections disappeared

### Package 15.3 - Snap Responsive
- attempted snap-aware responsive layout
- superseded during rollback/recovery

### Package 15.2 - Responsive Layout
- attempted layout compression for fullscreen and half-screen use
- superseded during rollback/recovery

### Package 15.1 - Layout + Dependency Hotfix
- improved dependency update handling and basic scroll access
- superseded during rollback/recovery

### Package 15.0 - Stability Contract Pack
- introduced behavior-contract, dependency UX, browser/cookie contract, and error-taxonomy hardening
- later found to introduce layout regressions and was superseded by 15R recovery packages

## Earlier VDM_v1.1 build-up
### Package 14.3
- finalized filename reset/persistence behavior after additional UI fixes

### Package 14.2
- corrected filename preview/output synchronization edge cases

### Package 14.1
- polished filename preset/manual interactions and fallback state behavior

### Package 14.0
- added final release gate, cleanup, and portable bundle structure docs

### Package 13.2
- stabilized filename behavior across analyze cycles and preset/manual transitions

### Package 13.1
- added optional external FFmpeg re-encode launcher as a separate helper action

### Package 13.0
- added RC-style release notes, quick-start, troubleshooting, and gate script

### Package 12.0
- added multi-site validation guidance and release-readiness helper scripts

### Package 11.2
- fixed filename/manual-mode reset and preview issues

### Package 11.1
- fixed regression suite compatibility with current settings fields

### Package 11.0
- added regression suite runner, persistence regression test, and release-readiness checklist

### Package 10.0
- added persisted format-table column order/widths and runtime selection persistence

### Package 9.5
- refined settings persistence and related UI synchronization

### Package 9.4
- added browser/history usability refinements

### Package 9.0
- stabilized analyze/download UI integration and settings behavior

### Package 8.0
- strengthened downloader workflow and result handling

### Package 7.0
- hardened dependency startup checks, browser detection, and download/fallback behavior

### Package 6.0
- repository cleanup and open-source/release-prep groundwork

### Package 5.0
- hardening, error-classification, and build/export preparation

### Package 4.0
- real download engine integration

### Package 3.0
- real URL analysis and format listing integration

### Package 2.0
- dependency freshness checks and install/update groundwork

### Package 1.0
- foundation bootstrap, GUI skeleton, settings, and logging


## VDM_v1.2.0 / Package 1.1 - GitHub Repo Cleanup
- Removed individual package note files from the GitHub-facing repo.
- Kept PACKAGE_HISTORY.md as the single package timeline reference.
- Removed __pycache__ and compiled Python artifacts from the repository package.
- Kept source, docs, scripts, tests, and GitHub templates only.
