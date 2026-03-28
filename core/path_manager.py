import os
import shutil
import sys
from pathlib import Path
from typing import Optional

from models.app_settings import AppSettings
from core.environment import EnvironmentPaths


class PathManager:
    BROWSER_ALIASES = {
        "chrome": "chrome",
        "brave": "brave",
        "firefox": "firefox",
        "edge": "msedge",
    }

    def __init__(self, env_paths: EnvironmentPaths, settings: AppSettings):
        self.env_paths = env_paths
        self.settings = settings

    def _resolve_existing_file(self, value: str) -> Optional[str]:
        if not value:
            return None
        candidate = Path(value)
        if candidate.exists() and candidate.is_file():
            return str(candidate.resolve())
        return None

    def resolve_binary(self, name: str, custom_path: str = "") -> tuple[Optional[str], str]:
        custom_resolved = self._resolve_existing_file(custom_path)
        if custom_resolved:
            return custom_resolved, "custom"

        if self.settings.prefer_portable_tools:
            for candidate in self.env_paths.portable_binary_candidates(name):
                if candidate.exists() and candidate.is_file():
                    return str(candidate.resolve()), "portable"

        system_path = shutil.which(name)
        if system_path:
            return system_path, "system"

        return None, "unknown"

    def resolve_browser_binary(self, browser_name: str) -> tuple[Optional[str], str]:
        normalized = (browser_name or "").strip().lower()
        alias = self.BROWSER_ALIASES.get(normalized, normalized)

        system_path = shutil.which(alias)
        if system_path:
            return system_path, "system"

        if sys.platform != "win32":
            return None, "unknown"

        env = os.environ
        program_files = [
            env.get("PROGRAMFILES", ""),
            env.get("PROGRAMFILES(X86)", ""),
            env.get("LOCALAPPDATA", ""),
        ]

        candidates = {
            "chrome": [
                Path(env.get("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe",
                Path(env.get("PROGRAMFILES(X86)", "")) / "Google/Chrome/Application/chrome.exe",
                Path(env.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe",
            ],
            "brave": [
                Path(env.get("PROGRAMFILES", "")) / "BraveSoftware/Brave-Browser/Application/brave.exe",
                Path(env.get("PROGRAMFILES(X86)", "")) / "BraveSoftware/Brave-Browser/Application/brave.exe",
                Path(env.get("LOCALAPPDATA", "")) / "BraveSoftware/Brave-Browser/Application/brave.exe",
            ],
            "firefox": [
                Path(env.get("PROGRAMFILES", "")) / "Mozilla Firefox/firefox.exe",
                Path(env.get("PROGRAMFILES(X86)", "")) / "Mozilla Firefox/firefox.exe",
            ],
            "edge": [
                Path(env.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
                Path(env.get("PROGRAMFILES", "")) / "Microsoft/Edge/Application/msedge.exe",
                Path(env.get("LOCALAPPDATA", "")) / "Microsoft/Edge/Application/msedge.exe",
            ],
        }.get(normalized, [])

        for candidate in candidates:
            if str(candidate) and candidate.exists() and candidate.is_file():
                return str(candidate.resolve()), "system"

        return None, "unknown"

    def build_runtime_env(self) -> dict:
        env = os.environ.copy()
        extra_paths = []
        for folder in [self.env_paths.ffmpeg_dir, self.env_paths.deno_dir, self.env_paths.tools_dir]:
            if folder.exists():
                extra_paths.append(str(folder))

        if extra_paths:
            env["PATH"] = os.pathsep.join(extra_paths + [env.get("PATH", "")])
        return env

    def _read_user_path_windows(self) -> str:
        if sys.platform != "win32":
            return os.environ.get("PATH", "")
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "Path")
                return value
        except FileNotFoundError:
            return ""
        except Exception:
            return os.environ.get("PATH", "")

    def _write_user_path_windows(self, value: str) -> tuple[bool, str]:
        if sys.platform != "win32":
            return False, "User PATH update is only supported on Windows."
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, value)
            return True, "User PATH updated."
        except Exception as exc:
            return False, str(exc)

    def append_to_user_path(self, folder: Path) -> tuple[bool, str]:
        folder = folder.resolve()
        current = self._read_user_path_windows()
        parts = [p for p in current.split(os.pathsep) if p]
        normalized = {str(Path(p).resolve()) if Path(p).exists() else p for p in parts}

        if str(folder) in normalized:
            return True, "Path already exists in user PATH."

        new_value = os.pathsep.join(parts + [str(folder)]) if current else str(folder)
        return self._write_user_path_windows(new_value)

    def ensure_dependency_paths(self, dependency_name: str) -> tuple[bool, str]:
        if not self.settings.allow_system_path_updates:
            return False, "System PATH updates are disabled in settings."

        name = dependency_name.lower()
        if name == "ffmpeg":
            return self.append_to_user_path(self.env_paths.ffmpeg_dir)
        if name == "deno":
            return self.append_to_user_path(self.env_paths.deno_dir)
        if name == "yt-dlp":
            return self.append_to_user_path(self.env_paths.tools_dir)
        return False, f"No PATH rule defined for {dependency_name}."
