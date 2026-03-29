from __future__ import annotations

import sys
from pathlib import Path

ROOT_REQUIRED_FILES = [
    "VDM.exe",
]

APP_DATA_FILES = [
    "data/settings.json",
    "data/history.json",
]

BUNDLE_REQUIRED_FILES = [
    "README.md",
    "CHANGELOG.md",
    "PACKAGE_HISTORY.md",
    "LICENSE",
    "locales/en.json",
    "locales/tr.json",
    "assets/app_icon.png",
    "assets/app_icon.ico",
]

BUNDLED_SEED_DATA_FILES = [
    "data/settings.json",
    "data/history.json",
]


def _missing_from(base: Path, rel_paths: list[str]) -> list[str]:
    missing: list[str] = []
    for rel in rel_paths:
        if not (base / rel).exists():
            missing.append(rel)
    return missing


def _exists_in_any(base_paths: list[Path], rel_path: str) -> bool:
    return any((base / rel_path).exists() for base in base_paths)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: verify_portable_exe_bundle.py <dist/VDM path>")
        return 2

    root = Path(sys.argv[1]).resolve()
    bundle_root = root / "_internal"

    missing_root = _missing_from(root, ROOT_REQUIRED_FILES)
    missing_bundle = _missing_from(bundle_root, BUNDLE_REQUIRED_FILES)

    data_failures: list[str] = []
    for rel in APP_DATA_FILES:
        if not _exists_in_any([root, bundle_root], rel):
            data_failures.append(rel)

    warnings: list[str] = []
    for rel in APP_DATA_FILES:
        if not (root / rel).exists() and (bundle_root / rel).exists():
            warnings.append(
                f"runtime data file not present in app root yet (acceptable before first launch): {rel}"
            )

    if missing_root or missing_bundle or data_failures:
        print("Missing required portable bundle items:")
        for item in missing_root:
            print(f" - {item}")
        for item in missing_bundle:
            print(f" - _internal/{item}")
        for item in data_failures:
            print(f" - {item} (missing from both app root and _internal seed data)")
        return 1

    for warning in warnings:
        print(f"Warning: {warning}")

    print("Portable bundle verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
