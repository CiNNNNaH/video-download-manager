from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from core.browser_cookies import BrowserCookies
from core.error_handler import ErrorHandler
from core.path_manager import PathManager
from core.remuxer import RemuxPlanner
from models.download_status import DownloadStatus
from models.format_item import FormatItem


class DownloadCancelled(Exception):
    pass


@dataclass
class DownloadRequest:
    url: str
    browser: str
    fallback_browsers: bool
    output_dir: str
    filename_template: str
    media_mode: str
    selected_item: FormatItem
    remux_enabled: bool
    target_container: str


class Downloader:
    def __init__(self, settings, path_manager: PathManager):
        self.settings = settings
        self.path_manager = path_manager
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._active = False

    @property
    def is_active(self) -> bool:
        return self._active

    @staticmethod
    def _human_size(value: float | int | None) -> str:
        if not value:
            return "-"
        size = float(value)
        units = ["B", "KB", "MB", "GB", "TB"]
        idx = 0
        while size >= 1024 and idx < len(units) - 1:
            size /= 1024
            idx += 1
        return f"{size:.1f} {units[idx]}"

    @staticmethod
    def _human_speed(value: float | int | None) -> str:
        if not value:
            return "-"
        return f"{Downloader._human_size(value)}/s"

    @staticmethod
    def _human_eta(value: int | float | None) -> str:
        if value is None:
            return "-"
        seconds = max(int(value), 0)
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02}:{m:02}:{s:02}" if h else f"{m:02}:{s:02}"

    def _preferred_audio_selector(self, request: DownloadRequest) -> str:
        item = request.selected_item
        target = (request.target_container or "").strip().lower()
        ext = (item.ext or "").strip().lower()

        prefers_mp4_family = target == "mp4" or (target in {"", "auto", "keep original"} and ext == "mp4")
        if prefers_mp4_family:
            return "bestaudio[ext=m4a]/bestaudio[acodec*=mp4a]/bestaudio/best"

        prefers_webm_family = target == "webm" or (target in {"", "auto", "keep original"} and ext == "webm")
        if prefers_webm_family:
            return "bestaudio[ext=webm]/bestaudio[acodec*=opus]/bestaudio/best"

        return "bestaudio/best"

    def _build_format_selector(self, request: DownloadRequest) -> str:
        item = request.selected_item
        base_selector = item.original_format_ids or item.format_id or "best"
        media_mode = request.media_mode
        preferred_audio = self._preferred_audio_selector(request)

        if media_mode == "audio only":
            if item.media_type == "audio only":
                return base_selector
            return preferred_audio

        if media_mode == "video only":
            if item.media_type == "audio only":
                return "bestvideo/best"
            if item.media_type == "muxed":
                return base_selector
            return base_selector

        if item.media_type == "audio only":
            return preferred_audio
        if item.media_type == "video only":
            return f"{base_selector}+{preferred_audio}"
        return base_selector

    def _requires_ffmpeg(self, request: DownloadRequest, format_selector: str, remux_target: str) -> bool:
        if remux_target:
            return True
        if "+" in format_selector:
            return True
        if request.media_mode == "video+audio" and request.selected_item.media_type == "video only":
            return True
        return False

    def _resolve_final_output_path(
        self,
        output_dir: Path,
        final_path: str,
        last_filename: str,
        started_at: datetime,
    ) -> str:
        candidates: list[Path] = []

        for raw in [final_path, last_filename]:
            if raw:
                try:
                    candidates.append(Path(raw).resolve())
                except Exception:
                    pass

        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return str(candidate)

        try:
            lower_bound = started_at - timedelta(seconds=5)
            files = [
                item for item in output_dir.rglob("*")
                if item.is_file() and datetime.fromtimestamp(item.stat().st_mtime) >= lower_bound
            ]
            if files:
                latest = max(files, key=lambda item: item.stat().st_mtime)
                return str(latest.resolve())
        except Exception:
            pass

        return final_path or last_filename or ""

    def _base_opts(self) -> dict[str, Any]:
        opts: dict[str, Any] = {
            "quiet": True,
            "noprogress": True,
            "windowsfilenames": True,
            "overwrites": True,
            "continuedl": True,
            "retries": 3,
            "nopart": False,
        }
        # VDM 9.2 hotfix:
        # Avoid custom js_runtimes injection until the yt-dlp runtime config is
        # rebuilt in a verified format. This unblocks standard download flows.
        ffmpeg_path, _ = self.path_manager.resolve_binary("ffmpeg", self.settings.ffmpeg_path)
        if ffmpeg_path:
            opts["ffmpeg_location"] = ffmpeg_path
        return opts

    def stop(self) -> None:
        self._stop_event.set()

    def start(
        self,
        request: DownloadRequest,
        on_progress: Callable[[DownloadStatus], None],
        on_complete: Callable[[DownloadStatus], None],
        on_error: Callable[[str], None],
        on_log: Callable[[str], None],
    ) -> bool:
        with self._lock:
            if self._active:
                return False
            self._active = True
            self._stop_event.clear()

        def run() -> None:
            final_status = DownloadStatus(status="started", stage="hazirlaniyor", message="Indirme hazirlaniyor")
            last_filename = ""
            final_path = ""
            try:
                output_dir = Path(request.output_dir).resolve()
                started_at = datetime.now()
                output_dir.mkdir(parents=True, exist_ok=True)
                on_progress(final_status)
                on_log(f"Indirme hazirlaniyor | url={request.url}")

                format_selector = self._build_format_selector(request)
                remux_target = RemuxPlanner.determine_target(
                    request.selected_item,
                    request.media_mode,
                    request.remux_enabled,
                    request.target_container,
                    format_selector=format_selector,
                )

                if self._requires_ffmpeg(request, format_selector, remux_target):
                    ffmpeg_path, _ = self.path_manager.resolve_binary("ffmpeg", self.settings.ffmpeg_path)
                    if not ffmpeg_path:
                        raise DownloadError(
                            "ffmpeg missing: birlestirme/remux icin ffmpeg gerekli ama bulunamadi"
                        )

                candidates = BrowserCookies.resolve_candidates(request.browser, request.fallback_browsers)
                if not candidates:
                    candidates = BrowserCookies.resolve_candidates("cookies kapali", False)

                errors: list[str] = []
                for candidate in candidates:
                    opts = self._base_opts()
                    opts["paths"] = {"home": str(output_dir)}
                    opts["outtmpl"] = request.filename_template or "%(title)s.%(ext)s"
                    opts["format"] = format_selector
                    opts["noplaylist"] = False

                    if candidate.yt_dlp_name:
                        opts["cookiesfrombrowser"] = (candidate.yt_dlp_name,)

                    if remux_target:
                        opts["merge_output_format"] = remux_target
                        opts["remuxvideo"] = remux_target
                        on_log(f"Remux hedefi aktif: {remux_target}")

                    def hook(data: dict[str, Any]) -> None:
                        nonlocal last_filename, final_path
                        if self._stop_event.is_set():
                            raise DownloadCancelled("Indirme kullanici tarafindan durduruldu.")

                        status = data.get("status")
                        downloaded = data.get("downloaded_bytes") or data.get("processed_bytes")
                        total = data.get("total_bytes") or data.get("total_bytes_estimate")
                        percent = 0.0
                        if downloaded and total:
                            percent = min((downloaded / total) * 100.0, 100.0)
                        speed = self._human_speed(data.get("speed"))
                        eta = self._human_eta(data.get("eta"))
                        filename = data.get("filename") or data.get("info_dict", {}).get("_filename") or last_filename
                        if filename:
                            last_filename = filename
                        if status == "downloading":
                            on_progress(
                                DownloadStatus(
                                    status="downloading",
                                    stage="indiriliyor",
                                    percent=percent,
                                    speed_text=speed,
                                    eta_text=eta,
                                    downloaded_text=self._human_size(downloaded),
                                    total_text=self._human_size(total),
                                    filename=last_filename,
                                    message="Indirme suruyor",
                                )
                            )
                        elif status == "finished":
                            final_path = data.get("filename") or final_path
                            on_progress(
                                DownloadStatus(
                                    status="finished",
                                    stage="birlestiriliyor/remux yapiliyor",
                                    percent=100.0,
                                    speed_text=speed,
                                    eta_text="00:00",
                                    downloaded_text=self._human_size(downloaded),
                                    total_text=self._human_size(total),
                                    filename=last_filename,
                                    message="Ham indirme tamamlandi",
                                )
                            )

                    opts["progress_hooks"] = [hook]

                    try:
                        on_log(f"Indirme denemesi | cookie kaynagi={candidate.label} | format={format_selector}")
                        with YoutubeDL(opts) as ydl:
                            info = ydl.extract_info(request.url, download=True)
                            if isinstance(info, dict):
                                requested = info.get("requested_downloads") or []
                                if requested:
                                    final_path = requested[-1].get("filepath") or requested[-1].get("_filename") or final_path
                                final_path = (
                                    info.get("requested_downloads", [{}])[-1].get("filepath")
                                    if info.get("requested_downloads")
                                    else final_path
                                ) or info.get("filepath") or info.get("_filename") or info.get("__finaldir") or final_path
                        break
                    except DownloadCancelled:
                        raise
                    except DownloadError as exc:
                        errors.append(f"{candidate.label}: {exc}")
                        on_log(f"Indirme denemesi basarisiz | {candidate.label} | {exc}")
                        continue
                    except Exception as exc:
                        errors.append(f"{candidate.label}: {type(exc).__name__}: {exc}")
                        on_log(f"Indirme denemesi basarisiz | {candidate.label} | {type(exc).__name__}: {exc}")
                        continue
                else:
                    raise DownloadError(" | ".join(errors[:4]) or "Indirme basarisiz oldu")

                resolved_final_path = self._resolve_final_output_path(
                    output_dir=output_dir,
                    final_path=str(final_path) if final_path else "",
                    last_filename=last_filename,
                    started_at=started_at,
                )
                status = DownloadStatus(
                    status="completed",
                    stage="tamamlandi",
                    percent=100.0,
                    speed_text="-",
                    eta_text="00:00",
                    downloaded_text="-",
                    total_text="-",
                    filename=last_filename,
                    final_path=resolved_final_path,
                    message="Indirme tamamlandi",
                )
                on_complete(status)
                on_log(f"Indirme tamamlandi | final_path={resolved_final_path or "-"}")
            except DownloadCancelled as exc:
                app_error = ErrorHandler.classify_download_error(str(exc))
                on_error(
                    f"{app_error.title}\n{app_error.message}\n\n{app_error.detail}\n\nOneri: {app_error.suggestion}"
                )
                on_log(str(exc))
            except DownloadError as exc:
                raw_message = f"yt-dlp hatasi: {exc}"
                app_error = ErrorHandler.classify_download_error(raw_message)
                on_error(
                    f"{app_error.title}\n{app_error.message}\n\n{app_error.detail}\n\nOneri: {app_error.suggestion}"
                )
                on_log(raw_message)
            except Exception as exc:
                raw_message = f"Indirme hatasi: {type(exc).__name__}: {exc}"
                app_error = ErrorHandler.classify_download_error(raw_message)
                on_error(
                    f"{app_error.title}\n{app_error.message}\n\n{app_error.detail}\n\nOneri: {app_error.suggestion}"
                )
                on_log(raw_message)
            finally:
                with self._lock:
                    self._active = False
                self._stop_event.clear()

        self._thread = threading.Thread(target=run, name="vdm-download-worker", daemon=True)
        self._thread.start()
        return True
