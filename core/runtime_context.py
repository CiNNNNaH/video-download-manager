from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


@dataclass(frozen=True)
class RuntimeContext:
    app_root: Path
    bundle_root: Path
    frozen: bool


def is_frozen_app() -> bool:
    return bool(getattr(sys, "frozen", False))


def get_runtime_context() -> RuntimeContext:
    if is_frozen_app():
        app_root = Path(sys.executable).resolve().parent
        bundle_root = Path(getattr(sys, "_MEIPASS", app_root / "_internal")).resolve()
        return RuntimeContext(app_root=app_root, bundle_root=bundle_root, frozen=True)
    root = Path(__file__).resolve().parents[1]
    return RuntimeContext(app_root=root, bundle_root=root, frozen=False)


def get_app_root() -> Path:
    return get_runtime_context().app_root


def get_bundle_root() -> Path:
    return get_runtime_context().bundle_root
