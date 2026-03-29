import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.environment import EnvironmentPaths
from models.app_settings import AppSettings
from services.log_service import LogService
from services.settings_service import SettingsService


def run() -> None:
    assert (ROOT / "scripts" / "run_pretest_checks.bat").exists()
    assert (ROOT / "scripts" / "export_debug_info.bat").exists()
    assert (ROOT / "docs" / "CONTROLLED_USER_TEST_PLAN.md").exists()
    assert (ROOT / "docs" / "TEST_RESULT_TEMPLATE.md").exists()

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_root = Path(tmpdir)
        env = EnvironmentPaths(temp_root)
        settings = AppSettings()

        settings_service = SettingsService(env.data_dir / "settings.json")
        settings_service.save(settings)
        loaded = settings_service.load()
        assert loaded.version == "VDM_v1.2.0"
        assert loaded.theme in {"light", "dark", "system"}

        log_service = LogService(temp_root / "log.txt", env.logs_dir / "app.log")
        log_service.start_session(loaded, temp_root, env)
        log_service.info("runtime sanity marker")

        root_log = (temp_root / "log.txt").read_text(encoding="utf-8")
        detailed_log = (env.logs_dir / "app.log").read_text(encoding="utf-8")
        assert "VDM session started" in root_log
        assert "runtime sanity marker" in detailed_log
        assert "Session bootstrap:" in detailed_log

        log_service.close()

    print("local runtime sanity passed")


if __name__ == "__main__":
    run()
