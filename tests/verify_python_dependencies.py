import importlib
import sys

REQUIRED = [
    ("PySide6", "PySide6"),
    ("packaging", "packaging"),
    ("yt_dlp", "yt-dlp"),
]


def main() -> int:
    missing = []
    for module_name, package_name in REQUIRED:
        try:
            importlib.import_module(module_name)
        except Exception as exc:
            missing.append((module_name, package_name, exc))

    if missing:
        print("Missing Python dependencies detected:")
        for module_name, package_name, exc in missing:
            print(f"- import {module_name} failed ({exc}) | install package: {package_name}")
        print()
        print("Run this command before pretest:")
        print("python -m pip install -r requirements.txt")
        return 1

    print("python dependency import check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
