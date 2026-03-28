from __future__ import annotations

import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

INCLUDE_FILES = [
    'log.txt',
    'release_manifest.json',
    'PACKAGE_HISTORY.md',
    'CHANGELOG.md',
    'README.md',
]
INCLUDE_DIRS = [
    'logs',
]
INCLUDE_DATA = [
    'data/settings.json',
    'data/history.json',
]
EXCLUDE_SUFFIXES = {'.pyc', '.pyo'}
EXCLUDE_NAMES = {'__pycache__'}


def safe_copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree(src: Path, dst: Path) -> None:
    for path in src.rglob('*'):
        rel = path.relative_to(src)
        if any(part in EXCLUDE_NAMES for part in rel.parts):
            continue
        if path.is_file() and path.suffix.lower() in EXCLUDE_SUFFIXES:
            continue
        target = dst / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def collect_bundle(root: Path) -> Path:
    root = root.resolve()
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    stage = root.parent / f'{root.name}__support_bundle_stage'
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True, exist_ok=True)

    for name in INCLUDE_FILES:
        src = root / name
        if src.exists() and src.is_file():
            safe_copy_file(src, stage / name)

    for rel in INCLUDE_DATA:
        src = root / rel
        if src.exists() and src.is_file():
            safe_copy_file(src, stage / rel)

    for name in INCLUDE_DIRS:
        src = root / name
        if src.exists() and src.is_dir():
            copy_tree(src, stage / name)

    zip_path = root.parent / f'{root.name}_support_bundle_{stamp}.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(stage.rglob('*')):
            if path.is_file():
                zf.write(path, path.relative_to(stage))

    print(f'Support bundle created: {zip_path}')
    print(f'Stage folder used: {stage}')
    return zip_path


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path('.')
    collect_bundle(root)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
