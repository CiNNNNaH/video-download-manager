import json
import re
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.request import Request, urlopen

from packaging.version import InvalidVersion, Version


class VersionCheck:
    USER_AGENT = "VDM/1.1"

    @staticmethod
    def normalize(version_text: str) -> str:
        if not version_text:
            return ""

        cleaned = version_text.strip()
        cleaned = cleaned.replace("yt-dlp", "").replace("ffmpeg version", "").strip()
        cleaned = cleaned.replace("deno", "").strip()
        cleaned = cleaned.lstrip("vV").strip()

        ffmpeg_git_match = re.search(r"git-(\d{4})-(\d{2})-(\d{2})", cleaned, re.IGNORECASE)
        if ffmpeg_git_match:
            year, month, day = ffmpeg_git_match.groups()
            return f"{year}.{month}.{day}"

        date_match = re.search(r"(\d{4})[-.](\d{1,2})[-.](\d{1,2})", cleaned)
        if date_match:
            year, month, day = date_match.groups()
            return f"{year}.{int(month)}.{int(day)}"

        match = re.search(r"(\d{4}\.\d{1,2}\.\d{1,2}|\d+\.\d+\.\d+)", cleaned)
        return match.group(1) if match else cleaned

    @staticmethod
    def compare_versions(local_version: str, latest_version: str) -> str:
        local_version = VersionCheck.normalize(local_version)
        latest_version = VersionCheck.normalize(latest_version)

        if not local_version:
            return "missing"
        if not latest_version:
            return "unknown"

        # Prefer date-based interpretation for yt-dlp style versions.
        if re.fullmatch(r"\d{4}\.\d{1,2}\.\d{1,2}", local_version) and re.fullmatch(r"\d{4}\.\d{1,2}\.\d{1,2}", latest_version):
            local_date = VersionCheck._parse_date_version(local_version)
            latest_date = VersionCheck._parse_date_version(latest_version)
            if local_date and latest_date:
                if local_date < latest_date:
                    delta_days = (latest_date - local_date).days
                    return "critical_outdated" if delta_days >= 60 else "outdated"
                return "ready"

        try:
            local = Version(local_version)
            latest = Version(latest_version)
        except InvalidVersion:
            return "unknown"

        if local < latest:
            major_gap = latest.release[0] - local.release[0] if latest.release and local.release else 0
            return "critical_outdated" if major_gap >= 1 else "outdated"
        return "ready"

    @staticmethod
    def _parse_date_version(value: str):
        try:
            parts = [int(x) for x in value.split(".")]
            return datetime(parts[0], parts[1], parts[2], tzinfo=timezone.utc).date()
        except Exception:
            return None

    @staticmethod
    def fetch_json(url: str, timeout: int = 6) -> dict[str, Any]:
        request = Request(url, headers={"User-Agent": VersionCheck.USER_AGENT})
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    @classmethod
    def get_latest_yt_dlp(cls) -> str:
        data = cls.fetch_json("https://pypi.org/pypi/yt-dlp/json")
        return cls.normalize(data.get("info", {}).get("version", ""))

    @classmethod
    def get_latest_deno(cls) -> str:
        data = cls.fetch_json("https://api.github.com/repos/denoland/deno/releases/latest")
        return cls.normalize(data.get("tag_name", ""))

    @classmethod
    def get_latest_version(cls, dependency_name: str) -> str:
        lowered = dependency_name.lower()
        if lowered == "yt-dlp":
            return cls.get_latest_yt_dlp()
        if lowered == "deno":
            return cls.get_latest_deno()
        if lowered == "ffmpeg":
            return ""
        return ""

    @classmethod
    def safe_get_latest_version(cls, dependency_name: str) -> tuple[str, str]:
        try:
            latest = cls.get_latest_version(dependency_name)
            return latest, ""
        except Exception as exc:
            return "", str(exc)
