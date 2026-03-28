import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.bootstrap_manager import BootstrapManager
from models.dependency_status import DependencyStatus


class DummyChecker:
    def check_binary(self, name):
        return DependencyStatus(
            name=name,
            status="ready",
            local_version="1.2.3",
            latest_version="1.2.3",
            message=f"{name} erisilebilir",
            resolved_path=f"C:/Tools/{name}.exe",
            source="system",
        )


class DummyInstallManager:
    def install_dependency(self, name):
        return True, f"installed {name}"

    def post_install_path_fix(self, name):
        return True, "path fixed"


def run() -> None:
    manager = BootstrapManager(DummyChecker(), DummyInstallManager())
    status = DependencyStatus(
        name="yt-dlp",
        status="outdated",
        local_version="1.0.0",
        latest_version="1.2.3",
        source="system",
        install_action="update",
    )
    results = manager.apply_actions([status])
    assert results and results[0]["resolved_path"] == "C:/Tools/yt-dlp.exe"
    print("dependency path logging regression passed")


if __name__ == "__main__":
    run()
