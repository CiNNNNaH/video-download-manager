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

from core.browser_cookies import BrowserCookies
from core.downloader import DownloadRequest, Downloader
from core.environment import EnvironmentPaths
from core.path_manager import PathManager
from models.app_settings import AppSettings
from models.format_item import FormatItem


def run() -> None:
    settings = AppSettings(default_browser="firefox", fallback_browsers=False)
    env = EnvironmentPaths(ROOT)
    pm = PathManager(env, settings)
    downloader = Downloader(settings, pm)

    video_only = FormatItem(format_id="137", original_format_ids="137", ext="mp4", media_type="video only")
    req = DownloadRequest(
        url="https://example.com/watch?v=test",
        browser="firefox",
        fallback_browsers=False,
        output_dir=str(ROOT),
        filename_template="%(title)s.%(ext)s",
        media_mode="video+audio",
        selected_item=video_only,
        remux_enabled=True,
        target_container="auto",
    )
    selector = downloader._build_format_selector(req)
    assert selector.startswith("137+")
    assert "bestaudio[ext=m4a]" in selector

    labels = [item.label for item in BrowserCookies.resolve_candidates("firefox", False)]
    assert labels[0] == "Firefox"

    print("package 10 flow regression passed")


if __name__ == "__main__":
    run()
