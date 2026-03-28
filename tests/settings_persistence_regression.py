import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.app_settings import AppSettings
from services.settings_service import SettingsService


def run() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "settings.json"
        svc = SettingsService(path)
        original = AppSettings(
            default_browser="firefox",
            default_media_mode="audio only",
            target_container="mp4",
            remux_enabled=False,
            fallback_browsers=True,
        )
        svc.save(original)
        loaded = svc.load()
        assert loaded.default_browser == "firefox"
        assert loaded.default_media_mode == "audio only"
        assert loaded.target_container == "mp4"
        assert loaded.remux_enabled is False
        assert loaded.fallback_browsers is True

    print("settings persistence regression passed")


if __name__ == "__main__":
    run()
