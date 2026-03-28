import json
import logging
import platform
import sys
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path


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
        root_handler.setLevel(logging.INFO)

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

    def _normalize_settings(self, settings) -> dict:
        if settings is None:
            return {}
        if is_dataclass(settings):
            return asdict(settings)
        if hasattr(settings, "__dict__"):
            return dict(settings.__dict__)
        return {"value": str(settings)}

    def start_session(self, settings=None, root_path: Path | None = None, env_paths=None) -> None:
        settings_map = self._normalize_settings(settings)
        summary = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "root": str(root_path) if root_path else "",
            "tools_dir": str(getattr(env_paths, "tools_dir", "")) if env_paths else "",
            "logs_dir": str(getattr(env_paths, "logs_dir", "")) if env_paths else "",
            "settings": {
                "version": settings_map.get("version", ""),
                "theme": settings_map.get("theme", ""),
                "default_browser": settings_map.get("default_browser", ""),
                "fallback_browsers": settings_map.get("fallback_browsers", ""),
                "prefer_portable_tools": settings_map.get("prefer_portable_tools", ""),
                "startup_dependency_check": settings_map.get("startup_dependency_check", ""),
                "check_online_updates_on_startup": settings_map.get("check_online_updates_on_startup", ""),
                "detailed_logging": settings_map.get("detailed_logging", ""),
            },
        }
        self.info("VDM session started")
        self.debug(f"Session bootstrap: {json.dumps(summary, ensure_ascii=False)}")

    def trace(self, event: str, **fields) -> None:
        payload = {"event": event, **fields}
        self.debug(f"TRACE {json.dumps(payload, ensure_ascii=False, default=str)}")

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
