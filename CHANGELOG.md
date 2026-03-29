# Changelog

This file tracks user-facing product changes for the active **VDM_v1.3.0** line, while preserving the older `VDM_v1.1` recovery and closure history below.

## VDM_v1.3.0 / Package 1.8 - Portable EXE Verify Timing and Strictness Fix
- updated portable bundle verification so `data/settings.json` and `data/history.json` may be validated from either app-root runtime data or bundled seed data
- removed false build failures caused by checking writable runtime data before the first EXE launch populated the app-root `data` folder
- kept package documentation synchronized with the active EXE validation line

## VDM_v1.3.0 / Package 1.7 - Portable EXE Verify Root Contract Fix and Icon Integration
- corrected the portable bundle verification contract so `data/settings.json` and `data/history.json` are validated in the writable app-root `data` folder instead of `_internal/data`
- added bundled application icon assets and wired them into the PyInstaller build and runtime window icon setup
- synchronized documentation identity for the active package after the EXE validation fixes

## VDM_v1.3.0 / Package 1.6 - Portable EXE Dependency Check and Verify Fix
- fixed EXE dependency check false errors caused by subprocess helper argument collisions
- aligned portable bundle verification with the PyInstaller `onedir` layout used by the build

## VDM_v1.3.0 / Package 1.5 - Portable EXE Resource Path and Console Suppression Fix
- separated bundled resource paths from writable app-root paths in frozen EXE runs
- fixed locale loading for the EXE build so translated UI text resolves correctly
- suppressed visible startup console flashes from hidden tool/version checks on Windows

## VDM_v1.3.0 / Package 1.4 - Portable EXE Build Foundation
- prepared the `PyInstaller onedir` build contract for the active `VDM_v1.3.0` line
- added frozen/source-aware runtime root handling for future EXE runs
- expanded build assets to include docs, data, and locale resources
- added portable build and verification scripts for the future EXE workflow

## VDM_v1.3.0 / Package 1.3 - Documentation and Version Identity Sync
- synchronized `README.md`, `CHANGELOG.md`, and `PACKAGE_HISTORY.md` with the active `VDM_v1.3.0` line
- corrected product/package identity drift left behind during rapid stabilization work
- formalized the rule that package-level runtime changes must update documentation alongside code

## VDM_v1.3.0 / Package 1.2 - Cancel and Failure Temp File Cleanup
- cleaned up partial `.part`/temporary files after cancelled or failed downloads
- kept only completed download outputs in the target folder

## VDM_v1.3.0 / Package 1.1 - Download Fallback, Stop Control, and Logging Unification
- switched the default browser path to Firefox-first for cookie-backed flows
- unified logging expectations between `app.log` and `log.txt`
- improved stop-flow honesty and fallback tracing for downloads

## VDM_v1.3.0 / Package 1.0 - Logging Hardening Foundation
- introduced hardened session logging from startup to shutdown
- added richer structured trace events for startup, analyze, and download flows
- established current-run-only session log behavior

---

The older `VDM_v1.1` history is retained below for continuity.

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
