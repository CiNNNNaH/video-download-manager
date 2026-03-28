import shutil
import subprocess

from models.dependency_status import DependencyStatus
from models.app_settings import AppSettings
from core.path_manager import PathManager
from core.version_check import VersionCheck


class DependencyChecker:
    def __init__(self, settings: AppSettings, path_manager: PathManager):
        self.settings = settings
        self.path_manager = path_manager

    def _extract_version_line(self, output: str) -> str:
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        return lines[0] if lines else ""

    def _custom_path_for(self, name: str) -> str:
        mapping = {
            "yt-dlp": self.settings.yt_dlp_path,
            "ffmpeg": self.settings.ffmpeg_path,
            "deno": self.settings.deno_path,
        }
        return mapping.get(name, "")

    def _install_command_for(self, name: str) -> str:
        if name == "yt-dlp":
            return "python -m pip install -U yt-dlp"
        if name == "deno":
            if shutil.which("winget"):
                return "winget install -e --id DenoLand.Deno"
            return "PowerShell: irm https://deno.land/install.ps1 | iex"
        if name == "ffmpeg":
            if shutil.which("winget"):
                return "winget install -e --id Gyan.FFmpeg"
            return "Portable ffmpeg paketini tools/ffmpeg altina koy."
        return ""

    def _suggested_fix_for(self, name: str, status: str) -> str:
        if name == "yt-dlp":
            if status in {"outdated", "critical_outdated"}:
                return "yt-dlp surumunu hemen guncelle. Eski surum site davranisini bozabilir."
            return "Uygulama icinden guncelle veya python -m pip install -U yt-dlp calistir."
        if name == "deno":
            return "Uygulama icinden yuklemeyi dene. Gerekirse winget veya resmi PowerShell kurulumunu kullan."
        if name == "ffmpeg":
            return "Uygulama icinden kurulum dene veya tools/ffmpeg altina portable binary ekle."
        if status == "missing":
            return "Bileseni kurup tekrar kontrol et."
        return "Detayli logu incele."

    def _check_latest(self, name: str) -> tuple[str, str]:
        if not self.settings.check_online_updates_on_startup:
            return "", "online version check disabled"
        return VersionCheck.safe_get_latest_version(name)

    def _resolution_detail(self, resolved_path: str, source: str, custom_path: str = "") -> str:
        details = [f"resolved_path={resolved_path}", f"source={source}"]
        if custom_path:
            details.append(f"custom_path={custom_path}")
        return " | ".join(details)

    def check_binary(self, name: str, version_arg: str = "--version") -> DependencyStatus:
        if name == "ffmpeg":
            version_arg = "-version"
        custom_path = self._custom_path_for(name)
        resolved_path, source = self.path_manager.resolve_binary(name, custom_path)
        if not resolved_path:
            return DependencyStatus(
                name=name,
                installed=False,
                accessible=False,
                status="missing",
                message=f"{name} bulunamadi",
                install_action="install",
                install_command=self._install_command_for(name),
                source=source,
                can_auto_fix=name in {"yt-dlp", "deno", "ffmpeg"},
                is_critical=name == "yt-dlp",
                details=f"resolved_path=- | source={source} | custom_path={custom_path or '-'}",
                suggested_fix=self._suggested_fix_for(name, "missing"),
            )

        try:
            result = subprocess.run(
                [resolved_path, version_arg],
                capture_output=True,
                text=True,
                timeout=8,
                env=self.path_manager.build_runtime_env(),
            )
            output = "\n".join([result.stdout or "", result.stderr or ""]).strip()
            if result.returncode != 0:
                return DependencyStatus(
                    name=name,
                    installed=True,
                    accessible=False,
                    status="error",
                    message=f"{name} surum bilgisi okunamadi",
                    resolved_path=resolved_path,
                    install_command=self._install_command_for(name),
                    source=source,
                    can_auto_fix=name in {"yt-dlp", "deno", "ffmpeg"},
                    is_critical=name == "yt-dlp",
                    details=f"{self._resolution_detail(resolved_path, source, custom_path)} | command_exit={result.returncode} | raw={output or '-'}",
                    suggested_fix=self._suggested_fix_for(name, "error"),
                )

            version_text = self._extract_version_line(output)
            latest_version, latest_error = self._check_latest(name)
            compare_state = VersionCheck.compare_versions(version_text, latest_version)

            if name == "ffmpeg" and not latest_version:
                status = "ready"
                message = "ffmpeg erisilebilir"
                if self.settings.check_online_updates_on_startup:
                    message += " (online son surum karsilastirmasi yok)"
            else:
                status = compare_state if compare_state in {"ready", "outdated", "critical_outdated"} else "ready"
                message = f"{name} erisilebilir"
                if status == "outdated":
                    message = f"{name} guncel degil"
                elif status == "critical_outdated":
                    message = f"{name} kritik derecede eski"
                elif latest_error and latest_error != "online version check disabled":
                    message = f"{name} erisilebilir, online surum kontrolu yapilamadi"
                elif latest_error == "online version check disabled":
                    message = f"{name} erisilebilir, online surum kontrolu kapali"

            details = self._resolution_detail(resolved_path, source, custom_path)
            if latest_error:
                details += f" | latest_check={latest_error}"

            return DependencyStatus(
                name=name,
                installed=True,
                accessible=True,
                local_version=VersionCheck.normalize(version_text),
                latest_version=latest_version,
                status=status,
                message=message,
                resolved_path=resolved_path,
                install_action="update" if status in {"outdated", "critical_outdated"} else "none",
                install_command=self._install_command_for(name),
                source=source,
                can_auto_fix=name in {"yt-dlp", "deno", "ffmpeg"},
                is_critical=(name == "yt-dlp" and status in {"outdated", "critical_outdated"}),
                details=details,
                suggested_fix=self._suggested_fix_for(name, status),
            )
        except Exception as exc:
            return DependencyStatus(
                name=name,
                installed=True,
                accessible=False,
                status="error",
                message=f"{name} kontrol hatasi",
                resolved_path=resolved_path,
                install_command=self._install_command_for(name),
                source=source,
                can_auto_fix=name in {"yt-dlp", "deno", "ffmpeg"},
                is_critical=name == "yt-dlp",
                details=f"{self._resolution_detail(resolved_path, source, custom_path)} | exception={type(exc).__name__}: {exc}",
                suggested_fix=self._suggested_fix_for(name, "error"),
            )

    def check_browsers(self) -> list[DependencyStatus]:
        browsers = [
            ("chrome", "Chrome"),
            ("brave", "Brave"),
            ("firefox", "Firefox"),
            ("edge", "Edge"),
        ]
        statuses: list[DependencyStatus] = []
        for browser_key, browser_label in browsers:
            binary, source = self.path_manager.resolve_browser_binary(browser_key)
            statuses.append(
                DependencyStatus(
                    name=browser_label,
                    installed=bool(binary),
                    accessible=bool(binary),
                    status="ready" if binary else "missing",
                    message="Browser bulundu" if binary else "Browser bulunamadi",
                    resolved_path=binary or "",
                    source=source,
                    can_auto_fix=False,
                    details=f"resolved_path={binary or '-'} | source={source}",
                    suggested_fix="Browser yoksaniz ilgili tarayiciyi kurun.",
                )
            )
        return statuses

    def run_all_checks(self) -> list[DependencyStatus]:
        return [
            self.check_binary("yt-dlp"),
            self.check_binary("ffmpeg"),
            self.check_binary("deno"),
            *self.check_browsers(),
        ]
