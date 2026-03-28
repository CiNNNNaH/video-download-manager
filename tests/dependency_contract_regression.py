import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.dependency_check import DependencyChecker
from core.environment import EnvironmentPaths
from core.path_manager import PathManager
from models.app_settings import AppSettings


def run() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        env = EnvironmentPaths(Path(tmpdir))
        settings = AppSettings(check_online_updates_on_startup=False)
        pm = PathManager(env, settings)
        checker = DependencyChecker(settings, pm)

        status = checker.check_binary("yt-dlp")
        assert status.status in {"ready", "outdated", "critical_outdated", "missing", "error"}
        assert status.severity_label in {"OK", "UYARI", "KRITIK", "HATA", "BILINMIYOR"}
        assert "source=" in (status.details or "") or status.status == "missing"
        assert status.ui_summary.startswith("[")

    print("dependency contract regression passed")


if __name__ == "__main__":
    run()
