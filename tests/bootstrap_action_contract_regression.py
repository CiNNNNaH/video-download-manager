import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.bootstrap_manager import BootstrapManager
from models.dependency_status import DependencyStatus


class FakeChecker:
    def check_binary(self, name: str):
        return DependencyStatus(name=name, status="outdated", local_version="1.0", message="still outdated")


class FakeInstaller:
    def __init__(self):
        self.path_fix_calls = 0

    def install_dependency(self, name: str):
        return True, f"installed {name}"

    def post_install_path_fix(self, name: str):
        self.path_fix_calls += 1
        return True, f"path fixed for {name}"


def run() -> None:
    manager = BootstrapManager(FakeChecker(), FakeInstaller())

    system_status = DependencyStatus(name="deno", status="outdated", install_action="update", source="system")
    results = manager.apply_actions([system_status])
    assert results[0]["path_state"] == "not-needed"
    assert results[0]["path_ok"] is True

    portable_status = DependencyStatus(name="ffmpeg", status="missing", install_action="install", source="portable")
    installer = FakeInstaller()
    manager = BootstrapManager(FakeChecker(), installer)
    results = manager.apply_actions([portable_status])
    assert results[0]["path_state"] == "ok"
    assert installer.path_fix_calls == 1

    print("bootstrap action contract regression passed")


if __name__ == "__main__":
    run()
