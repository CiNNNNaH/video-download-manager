import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import types

if 'yt_dlp' not in sys.modules:
    fake_yt_dlp = types.ModuleType('yt_dlp')
    fake_yt_dlp.YoutubeDL = object
    fake_utils = types.ModuleType('yt_dlp.utils')
    class FakeDownloadError(Exception):
        pass
    fake_utils.DownloadError = FakeDownloadError
    sys.modules['yt_dlp'] = fake_yt_dlp
    sys.modules['yt_dlp.utils'] = fake_utils

from core.bootstrap_manager import BootstrapManager
from core.browser_cookies import BrowserCookies
from core.dependency_check import DependencyChecker
from core.downloader import DownloadRequest, Downloader
from core.environment import EnvironmentPaths
from core.error_handler import ErrorHandler
from core.path_manager import PathManager
from core.remuxer import RemuxPlanner
from models.app_settings import AppSettings
from models.dependency_status import DependencyStatus
from models.format_item import FormatItem


class DummyChecker:
    def __init__(self):
        self.calls = []

    def run_all_checks(self):
        return []

    def check_binary(self, name: str):
        self.calls.append(name)
        return DependencyStatus(name=name, installed=True, accessible=True, status="ready", message="ok")


class DummyInstaller:
    def __init__(self, ok: bool):
        self.ok = ok
        self.path_fix_calls = []

    def install_dependency(self, name: str):
        return self.ok, "done"

    def post_install_path_fix(self, name: str):
        self.path_fix_calls.append(name)
        return True, "path ok"


def run():
    settings = AppSettings(check_online_updates_on_startup=False)
    env = EnvironmentPaths(ROOT)
    pm = PathManager(env, settings)
    checker = DependencyChecker(settings, pm)

    missing = checker.check_binary("yt-dlp")
    assert missing.status in {"missing", "ready", "outdated", "critical_outdated", "error"}

    candidates = BrowserCookies.resolve_candidates("chrome", True)
    assert candidates[0].label == "Chrome"
    assert candidates[-1].label in {"Firefox", "Brave", "Edge"}

    downloader = Downloader(settings, pm)
    item = FormatItem(format_id="137", original_format_ids="137", ext="mp4", media_type="video only")
    request = DownloadRequest(
        url="https://example.com/video",
        browser="chrome",
        fallback_browsers=True,
        output_dir=str(ROOT),
        filename_template="%(title)s.%(ext)s",
        media_mode="video+audio",
        selected_item=item,
        remux_enabled=True,
        target_container="auto",
    )
    assert downloader._build_format_selector(request) == "137+bestaudio[ext=m4a]/bestaudio[acodec*=mp4a]/bestaudio/best"
    assert RemuxPlanner.determine_target(
        item,
        "video+audio",
        True,
        "auto",
        format_selector=downloader._build_format_selector(request),
    ) == "mp4"

    error = ErrorHandler.classify_download_error("ffmpeg missing: not found")
    assert error.code == "ffmpeg_missing"

    ok_checker = DummyChecker()
    bad_installer = DummyInstaller(False)
    bootstrap = BootstrapManager(ok_checker, bad_installer)
    statuses = [DependencyStatus(name="yt-dlp", status="missing", install_action="install", message="x")]
    bootstrap.apply_actions(statuses)
    assert bad_installer.path_fix_calls == []

    ok_checker = DummyChecker()
    good_installer = DummyInstaller(True)
    bootstrap = BootstrapManager(ok_checker, good_installer)
    bootstrap.apply_actions(statuses)
    assert good_installer.path_fix_calls == ["yt-dlp"]

    print("pretest core checks passed")


if __name__ == "__main__":
    run()


from core.analyzer import Analyzer
from core.path_manager import PathManager
from core.remuxer import RemuxPlanner
from core.environment import EnvironmentPaths
from models.app_settings import AppSettings
from services.log_service import LogService
import tempfile


def _regression_checks():
    settings = AppSettings()
    with tempfile.TemporaryDirectory() as tmpdir:
        env = EnvironmentPaths(Path(tmpdir))
        pm = PathManager(env, settings)
        analyzer = Analyzer(settings, pm)
        opts = analyzer._base_opts()
        assert "js_runtimes" not in opts

        log_service = LogService(Path(tmpdir) / "root.log", env.logs_dir / "app.log")
        log_service.start_session(settings, Path(tmpdir), env)
        log_service.info("close regression")
        assert hasattr(log_service, "close")
        assert hasattr(log_service, "trace")
        log_service.trace("regression", ok=True)
        log_service.close()


_regression_checks()


from models.format_item import FormatItem

assert hasattr(FormatItem(), "tbr") and hasattr(FormatItem(), "proto") and hasattr(FormatItem(), "more_info"), "format item fields missing"
print("format item fields check passed")

from core.url_utils import UrlUtils

yt_watch_with_playlist = "https://www.youtube.com/watch?v=cgybhbLlAbs&list=RDcgybhbLlAbs&start_radio=1"
assert UrlUtils.normalize_url(yt_watch_with_playlist) == "https://www.youtube.com/watch?v=cgybhbLlAbs", "youtube playlist normalization failed"
print("youtube watch normalization check passed")

from core.version_check import VersionCheck

ffmpeg_line = "ffmpeg version 2025-10-19-git-dc39a576ad-essentials_build-www.gyan.dev Copyright (c) 2000-2025 the FFmpeg developers"
assert VersionCheck.normalize(ffmpeg_line) == "2025.10.19", "ffmpeg version normalization failed"
print("ffmpeg version normalization check passed")
