from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from core.browser_cookies import BrowserCookies
from core.error_handler import ErrorHandler
from core.format_processor import FormatProcessor
from core.path_manager import PathManager
from core.url_utils import UrlUtils
from models.content_info import ContentInfo


@dataclass
class AnalyzeResult:
    ok: bool
    content: ContentInfo | None = None
    simple_formats: list[Any] | None = None
    advanced_formats: list[Any] | None = None
    used_browser: str = ""
    message: str = ""
    technical_details: str = ""


class Analyzer:
    def __init__(self, settings, path_manager: PathManager):
        self.settings = settings
        self.path_manager = path_manager

    @staticmethod
    def _format_duration(seconds: int | None) -> str:
        if not seconds:
            return "-"
        seconds = int(seconds)
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02}:{m:02}:{s:02}" if h else f"{m:02}:{s:02}"

    def _base_opts(self) -> dict:
        opts: dict[str, Any] = {
            "quiet": True,
            "skip_download": True,
            "noplaylist": True,
            "extract_flat": False,
            "windowsfilenames": False,
            "ignoreerrors": False,
        }
        # VDM 9.2 hotfix:
        # Do not inject js_runtimes here.
        # The previous shape triggered yt-dlp ValueError on public analysis flows
        # (expected dict of {runtime: [config]}). Public links should analyze without
        # any browser runtime customization.
        return opts

    def _build_content(self, info: dict, original_url: str) -> ContentInfo:
        entries = info.get("entries") or []
        is_playlist = bool(entries)
        source = info
        if is_playlist and isinstance(entries, list) and entries:
            source = entries[0] or info

        content_type = "playlist" if is_playlist else "video"
        if source.get("vcodec") == "none":
            content_type = "audio"

        return ContentInfo(
            url=original_url,
            webpage_url=source.get("webpage_url") or info.get("webpage_url") or original_url,
            extractor=info.get("extractor_key") or info.get("extractor") or "",
            site=info.get("extractor") or info.get("webpage_url_domain") or "",
            title=source.get("title") or info.get("title") or "",
            uploader=source.get("uploader") or info.get("uploader") or source.get("channel") or "",
            duration_seconds=source.get("duration") or 0,
            duration_text=self._format_duration(source.get("duration") or 0),
            content_type=content_type,
            is_playlist=is_playlist,
            playlist_count=len(entries) if is_playlist and isinstance(entries, list) else 0,
            login_required=False,
            thumbnail_url=source.get("thumbnail") or info.get("thumbnail") or "",
            upload_date=source.get("upload_date") or info.get("upload_date") or "",
            raw=info,
        )

    def analyze(self, url: str, browser: str, fallback_browsers: bool = False) -> AnalyzeResult:
        normalized = UrlUtils.normalize_url(url)
        if not UrlUtils.is_valid_url(normalized):
            return AnalyzeResult(ok=False, message="Invalid URL", technical_details="The URL is not in http/https format.")

        candidates = BrowserCookies.resolve_candidates(browser, fallback_browsers)
        if not candidates:
            candidates = BrowserCookies.resolve_candidates("cookies_disabled", False)

        errors: list[str] = []
        for candidate in candidates:
            opts = self._base_opts()
            if candidate.yt_dlp_name:
                opts["cookiesfrombrowser"] = (candidate.yt_dlp_name,)
            try:
                with YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(normalized, download=False)
                content = self._build_content(info, normalized)
                advanced = FormatProcessor.build_advanced_items(info.get("formats") or [])
                simple = FormatProcessor.build_simple_items(advanced)
                return AnalyzeResult(
                    ok=True,
                    content=content,
                    simple_formats=simple,
                    advanced_formats=advanced,
                    used_browser=candidate.label,
                    message=f"Analysis completed. Browser used: {candidate.label}",
                )
            except DownloadError as exc:
                errors.append(f"{candidate.label}: {exc}")
            except Exception as exc:
                errors.append(f"{candidate.label}: {type(exc).__name__}: {exc}")

        app_error = ErrorHandler.classify_analyze_error(
            message="Analysis failed.",
            detail=" | ".join(errors[:4]),
        )
        return AnalyzeResult(
            ok=False,
            used_browser=", ".join(c.label for c in candidates),
            message=app_error.message,
            technical_details=f"{app_error.title} | {app_error.detail} | Suggestion: {app_error.suggestion}",
        )
