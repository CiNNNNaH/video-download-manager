from __future__ import annotations

import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from verify_portable_bundle import prepare_stage  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: package_release_bundle.py <project_or_portable_folder>")
        return 1

    source_root = Path(sys.argv[1]).resolve()
    if not source_root.exists() or not source_root.is_dir():
        print(f"Portable folder not found: {source_root}")
        return 1

    stage_root = prepare_stage(source_root)
    if not stage_root.exists() or not stage_root.is_dir():
        print(f"Stage folder not found after verification: {stage_root}")
        return 2

    zip_path = source_root.parent / f"{source_root.name}_release.zip"
    if zip_path.exists():
        zip_path.unlink()

    archive_base = zip_path.with_suffix("")
    shutil.make_archive(str(archive_base), "zip", root_dir=stage_root)

    print(f"Release zip created: {zip_path}")
    print(f"Stage folder used: {stage_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
