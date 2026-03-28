# Operational Hardening Guide

## Purpose
Package 18 adds low-risk operational hardening around diagnostics and package history consolidation. It does not change the validated analyze / download UI flow.

## Included
- `PACKAGE_HISTORY.md` as the single top-level package reference
- `scripts\collect_support_bundle.py`
- `scripts\collect_support_bundle.bat`
- support-bundle regression test

## Support bundle contents
The support bundle collects only troubleshooting-relevant artifacts when they exist:
- `log.txt`
- `logs\*`
- `data\settings.json`
- `data\history.json`
- `release_manifest.json`
- `PACKAGE_HISTORY.md`
- `CHANGELOG.md`
- `README.md`

## When to use it
Use the support bundle after:
- analyze / download failures that need review
- dependency update problems
- portable bundle verification or packaging problems
- multi-site failures that need a compact evidence pack

## Deliberately not changed in Package 18
- no UI/layout refactor
- no downloader logic change
- no cookie/browser fallback behavior change
- no new dependency installers
