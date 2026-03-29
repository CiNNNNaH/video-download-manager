from pathlib import Path
from tempfile import TemporaryDirectory

from core.environment import EnvironmentPaths
from models.app_settings import AppSettings
from services.log_service import LogService


def test_session_logging_writes_bootstrap_and_shutdown_markers() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        env = EnvironmentPaths(root)
        service = LogService(root / "log.txt", env.logs_dir / "app.log")
        settings = AppSettings()
        service.start_session(settings, root, env)
        service.trace_step("test", "hello", value=1)
        service.close()

        text = (root / "log.txt").read_text(encoding="utf-8")
        detail = (env.logs_dir / "app.log").read_text(encoding="utf-8")
        assert "VDM session started" in text
        assert '"event": "session.bootstrap"' in detail
        assert '"event": "session.shutdown"' in detail
        assert '"event": "test.hello"' in detail


def test_session_logging_resets_files_on_next_start() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        env = EnvironmentPaths(root)
        settings = AppSettings()

        first = LogService(root / "log.txt", env.logs_dir / "app.log")
        first.start_session(settings, root, env)
        first.trace_step("test", "first_run", value=1)
        first.close()

        second = LogService(root / "log.txt", env.logs_dir / "app.log")
        second.start_session(settings, root, env)
        second.trace_step("test", "second_run", value=2)
        second.close()

        detail = (env.logs_dir / "app.log").read_text(encoding="utf-8")
        assert '"event": "test.second_run"' in detail
        assert '"event": "test.first_run"' not in detail
