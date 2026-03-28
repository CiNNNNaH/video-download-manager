from models.dependency_status import DependencyStatus
from core.dependency_check import DependencyChecker
from core.install_manager import InstallManager


class BootstrapManager:
    MANAGED_DEPENDENCIES = {"yt-dlp", "ffmpeg", "deno"}

    def __init__(self, dependency_checker: DependencyChecker, install_manager: InstallManager):
        self.dependency_checker = dependency_checker
        self.install_manager = install_manager

    def scan(self) -> list[DependencyStatus]:
        return self.dependency_checker.run_all_checks()

    def missing_or_outdated(self, statuses: list[DependencyStatus]) -> list[DependencyStatus]:
        return [
            s for s in statuses
            if s.name in self.MANAGED_DEPENDENCIES and s.status in {"missing", "outdated", "critical_outdated", "error"}
        ]

    def apply_actions(self, statuses: list[DependencyStatus]) -> list[dict]:
        results: list[dict] = []
        for status in statuses:
            if status.install_action not in {"install", "update"}:
                continue

            ok, output = self.install_manager.install_dependency(status.name)
            if status.source in {"system", "custom"}:
                path_ok, path_state, path_output = True, "not-needed", "PATH duzeltmesi gerekmiyor; sistem veya custom kaynak kullaniliyor."
            elif ok:
                path_ok, path_output = self.install_manager.post_install_path_fix(status.name)
                path_state = "ok" if path_ok else "failed"
            else:
                path_ok, path_state, path_output = False, "skipped", "install basarisiz oldugu icin PATH duzeltmesi atlandi"

            verification = self.dependency_checker.check_binary(status.name)
            results.append({
                "name": status.name,
                "ok": ok,
                "output": output,
                "path_ok": path_ok,
                "path_state": path_state,
                "path_output": path_output,
                "resolved_path": verification.resolved_path,
                "verified_status": verification.status,
                "verified_version": verification.local_version,
                "verified_message": verification.message,
            })
        return results
