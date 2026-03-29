import json
import logging
import platform
import sys
import traceback
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


class LogService:
    def __init__(self, root_log_path: Path, detailed_log_path: Path):
        self.root_log_path = root_log_path
        self.detailed_log_path = detailed_log_path
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logger = logging.getLogger("VDM")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        self.logger.propagate = False
        self._configure_handlers()

    def _configure_handlers(self) -> None:
        self.root_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.detailed_log_path.parent.mkdir(parents=True, exist_ok=True)

        root_handler = logging.FileHandler(self.root_log_path, mode="w", encoding="utf-8")
        root_handler.setLevel(logging.DEBUG)

        detailed_handler = logging.FileHandler(self.detailed_log_path, mode="w", encoding="utf-8")
        detailed_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        root_handler.setFormatter(formatter)
        detailed_handler.setFormatter(formatter)

        self.logger.addHandler(root_handler)
        self.logger.addHandler(detailed_handler)

    def _flush_handlers(self) -> None:
        for handler in list(self.logger.handlers):
            try:
                handler.flush()
            except Exception:
                pass

    def _normalize_settings(self, settings) -> dict[str, Any]:
        if settings is None:
            return {}
        if is_dataclass(settings):
            return asdict(settings)
        if hasattr(settings, "__dict__"):
            return dict(settings.__dict__)
        return {"value": str(settings)}

    @staticmethod
    def _sanitize_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
        redacted_keys = {
            "password",
            "token",
            "authorization",
            "cookie",
            "cookies",
            "cookiefile",
            "cookie_file",
            "headers",
        }
        out: dict[str, Any] = {}
        for key, value in mapping.items():
            lowered = str(key).lower()
            if lowered in redacted_keys:
                out[key] = "<redacted>"
                continue
            out[key] = value
        return out

    def start_session(self, settings=None, root_path: Path | None = None, env_paths=None, bundle_root: Path | None = None) -> None:
        settings_map = self._normalize_settings(settings)
        summary = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "executable": sys.executable,
            "frozen": bool(getattr(sys, "frozen", False)),
            "root": str(root_path) if root_path else "",
            "bundle_root": str(bundle_root) if bundle_root else "",
            "tools_dir": str(getattr(env_paths, "tools_dir", "")) if env_paths else "",
            "logs_dir": str(getattr(env_paths, "logs_dir", "")) if env_paths else "",
            "settings": {
                "version": settings_map.get("version", ""),
                "theme": settings_map.get("theme", ""),
                "language": settings_map.get("language", ""),
                "default_browser": settings_map.get("default_browser", ""),
                "fallback_browsers": settings_map.get("fallback_browsers", ""),
                "prefer_portable_tools": settings_map.get("prefer_portable_tools", ""),
                "startup_dependency_check": settings_map.get("startup_dependency_check", ""),
                "check_online_updates_on_startup": settings_map.get("check_online_updates_on_startup", ""),
                "detailed_logging": settings_map.get("detailed_logging", ""),
                "default_view_mode": settings_map.get("default_view_mode", ""),
                "default_media_mode": settings_map.get("default_media_mode", ""),
            },
        }
        self.info("VDM session started")
        self.trace("session.bootstrap", **summary)

    def trace(self, event: str, **fields) -> None:
        payload = {"event": event, **fields}
        self.debug(f"TRACE {json.dumps(payload, ensure_ascii=False, default=str)}")

    def trace_step(self, component: str, step: str, **fields) -> None:
        self.trace(f"{component}.{step}", **fields)

    def trace_command(self, component: str, command: list[str] | tuple[str, ...] | str, **fields) -> None:
        normalized = command if isinstance(command, str) else " ".join(str(part) for part in command)
        self.trace(f"{component}.command", command=normalized, **fields)

    def trace_response(self, component: str, response: Any = None, **fields) -> None:
        payload = dict(fields)
        if response is not None:
            payload["response"] = response
        self.trace(f"{component}.response", **payload)

    def trace_exception(self, component: str, exc: Exception, **fields) -> None:
        payload = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            **fields,
        }
        self.trace(f"{component}.exception", **payload)
        self.debug(traceback.format_exc())

    def trace_paths(self, component: str, **paths) -> None:
        self.trace(f"{component}.paths", **paths)

    def trace_settings_snapshot(self, settings) -> None:
        snapshot = self._sanitize_mapping(self._normalize_settings(settings))
        self.trace("settings.snapshot", **snapshot)

    def info(self, message: str) -> None:
        self.logger.info(message)
        self._flush_handlers()

    def warning(self, message: str) -> None:
        self.logger.warning(message)
        self._flush_handlers()

    def error(self, message: str) -> None:
        self.logger.error(message)
        self._flush_handlers()

    def debug(self, message: str) -> None:
        self.logger.debug(message)
        self._flush_handlers()

    def close(self) -> None:
        self.trace("session.shutdown", timestamp=datetime.now().isoformat(timespec="seconds"))
        handlers = list(self.logger.handlers)
        for handler in handlers:
            try:
                handler.flush()
            except Exception:
                pass
            try:
                handler.close()
            except Exception:
                pass
            try:
                self.logger.removeHandler(handler)
            except Exception:
                pass
        logging.shutdown()
