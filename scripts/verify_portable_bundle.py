from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

REQUIRED_TOP_LEVEL = [
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "docs",
    "data",
]

FORBIDDEN_NAMES = {"__pycache__", ".pytest_cache"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}
EXCLUDE_NAMES = {"release_manifest.json"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".zip"}


def should_exclude_from_stage(path: Path) -> bool:
    if path.name in FORBIDDEN_NAMES or path.name in EXCLUDE_NAMES:
        return True
    if path.suffix.lower() in EXCLUDE_SUFFIXES:
        return True
    return False


def prepare_stage(source_root: Path) -> Path:
    stage_root = source_root.parent / f"{source_root.name}__portable_stage"
    if stage_root.exists():
        shutil.rmtree(stage_root)
    stage_root.mkdir(parents=True, exist_ok=True)

    for path in source_root.rglob("*"):
        rel = path.relative_to(source_root)
        if any(part in FORBIDDEN_NAMES for part in rel.parts):
            continue
        if path.is_file() and should_exclude_from_stage(path):
            continue
        target = stage_root / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)

    (stage_root / "log.txt").write_text("", encoding="utf-8")

    logs_dir = stage_root / "logs"
    if logs_dir.exists():
        shutil.rmtree(logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)

    history_path = stage_root / "data" / "history.json"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text("[]\n", encoding="utf-8")
    return stage_root


def collect_forbidden(root: Path) -> list[str]:
    hits: list[str] = []
    for path in root.rglob("*"):
        if path.name in FORBIDDEN_NAMES:
            hits.append(str(path.relative_to(root)))
        elif path.is_file() and path.suffix.lower() in FORBIDDEN_SUFFIXES:
            hits.append(str(path.relative_to(root)))
    return sorted(hits)


def verify_settings(root: Path) -> list[str]:
    issues: list[str] = []
    settings_path = root / "data" / "settings.json"
    if not settings_path.exists():
        return issues
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"settings.json okunamadi: {exc}"]
    if not isinstance(data, dict):
        return ["settings.json beklenen dict yapisinda degil"]
    for suspect_key in (
        "output_dir",
        "ffmpeg_path",
        "yt_dlp_path",
        "deno_path",
        "default_download_dir",
    ):
        value = data.get(suspect_key)
        if isinstance(value, str) and value.strip() and (":\\" in value or value.startswith("/")):
            issues.append(f"settings.json makineye ozel yol iceriyor: {suspect_key}={value}")
    return issues


def verify_logs(root: Path) -> list[str]:
    issues: list[str] = []
    log_root = root / "log.txt"
    if not log_root.exists():
        issues.append("root log.txt yok")
    logs_dir = root / "logs"
    if not logs_dir.exists():
        issues.append("logs klasoru yok")
    else:
        files = [p for p in logs_dir.rglob("*") if p.is_file()]
        if files:
            issues.append(
                "logs/ klasoru bos degil: "
                + ", ".join(str(p.relative_to(root)) for p in files[:10])
            )
    return issues


def verify_history(root: Path) -> list[str]:
    issues: list[str] = []
    history_path = root / "data" / "history.json"
    if history_path.exists():
        raw = history_path.read_text(encoding="utf-8", errors="ignore").strip()
        if raw not in ("", "[]", "{}"):
            issues.append("data/history.json bos degil")
    return issues


def build_manifest(root: Path, source_root: Path) -> dict[str, object]:
    files = [
        str(p.relative_to(root)).replace("\\", "/")
        for p in root.rglob("*")
        if p.is_file()
    ]
    return {
        "source_root": str(source_root),
        "bundle_root": str(root),
        "file_count": len(files),
        "files": sorted(files),
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: verify_portable_bundle.py <project_or_portable_folder>")
        return 1
    source_root = Path(sys.argv[1]).resolve()
    if not source_root.exists() or not source_root.is_dir():
        print(f"Portable folder not found: {source_root}")
        return 1

    stage_root = prepare_stage(source_root)
    issues: list[str] = []
    for item in REQUIRED_TOP_LEVEL:
        if not (stage_root / item).exists():
            issues.append(f"Eksik zorunlu oge: {item}")
    issues.extend(collect_forbidden(stage_root))
    issues.extend(verify_settings(stage_root))
    issues.extend(verify_logs(stage_root))
    issues.extend(verify_history(stage_root))

    manifest = build_manifest(stage_root, source_root)
    manifest_path = stage_root / "release_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    if issues:
        print("Portable bundle verification FAILED")
        print(f"Kaynak klasor: {source_root}")
        print(f"Stage klasoru: {stage_root}")
        for issue in issues:
            print(f" - {issue}")
        print(f"Manifest yazildi: {manifest_path}")
        return 2

    print("Portable bundle verification PASSED")
    print(f"Kaynak klasor: {source_root}")
    print(f"Stage klasoru: {stage_root}")
    print(f"Manifest yazildi: {manifest_path}")
    print(f"Toplam dosya: {manifest['file_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
