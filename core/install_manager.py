import shutil
import subprocess
import sys

from core.path_manager import PathManager
from core.subprocess_utils import hidden_subprocess_kwargs


class InstallManager:
    def __init__(self, path_manager: PathManager):
        self.path_manager = path_manager

    def run_shell_command(self, command: list[str], timeout: int = 900) -> tuple[bool, str]:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=self.path_manager.build_runtime_env(),
                shell=False,
                **hidden_subprocess_kwargs(),
            )
            output = "\n".join([result.stdout.strip(), result.stderr.strip()]).strip()
            command_text = subprocess.list2cmdline(command)
            annotated = f"command={command_text}\n{output}".strip()
            return result.returncode == 0, annotated or f"command={command_text}\nCommand finished."
        except Exception as exc:
            command_text = subprocess.list2cmdline(command)
            return False, f"command={command_text}\nexception={type(exc).__name__}: {exc}"

    def _winget_exists(self) -> bool:
        return shutil.which("winget") is not None

    def _python_package_command(self, package_name: str) -> list[str]:
        return [sys.executable, "-m", "pip", "install", "-U", package_name]

    def preview_install_command(self, dependency_name: str) -> str:
        lowered = dependency_name.lower()
        if lowered == "yt-dlp":
            return "python -m pip install -U yt-dlp"
        if lowered == "deno":
            if self._winget_exists():
                return "winget upgrade -e --id DenoLand.Deno || winget install -e --id DenoLand.Deno"
            return "deno upgrade  (alternatif: PowerShell: irm https://deno.land/install.ps1 | iex)"
        if lowered == "ffmpeg":
            if self._winget_exists():
                return "winget upgrade -e --id Gyan.FFmpeg || winget install -e --id Gyan.FFmpeg"
            return "Portable ffmpeg paketini tools/ffmpeg altina koy."
        return ""

    def install_dependency(self, dependency_name: str) -> tuple[bool, str]:
        lowered = dependency_name.lower()

        if lowered == "yt-dlp":
            return self.run_shell_command(self._python_package_command("yt-dlp"))

        if lowered == "deno":
            outputs: list[str] = []
            deno_binary, source = self.path_manager.resolve_binary("deno")
            if deno_binary:
                ok, output = self.run_shell_command([deno_binary, "upgrade"])
                outputs.append(f"deno_upgrade_source={source}\n{output}")
                if ok:
                    return True, "\n\n".join(outputs)

            if self._winget_exists():
                for command in (
                    ["winget", "upgrade", "-e", "--id", "DenoLand.Deno", "--accept-source-agreements", "--accept-package-agreements"],
                    ["winget", "install", "-e", "--id", "DenoLand.Deno", "--accept-source-agreements", "--accept-package-agreements"],
                ):
                    ok, output = self.run_shell_command(command)
                    outputs.append(output)
                    if ok:
                        return True, "\n\n".join(outputs)
                return False, "\n\n".join(outputs)

            outputs.append("winget was not found. Recommended Deno command: irm https://deno.land/install.ps1 | iex")
            return False, "\n\n".join(outputs)

        if lowered == "ffmpeg":
            if self._winget_exists():
                outputs: list[str] = []
                for command in (
                    ["winget", "upgrade", "-e", "--id", "Gyan.FFmpeg", "--accept-source-agreements", "--accept-package-agreements"],
                    ["winget", "install", "-e", "--id", "Gyan.FFmpeg", "--accept-source-agreements", "--accept-package-agreements"],
                ):
                    ok, output = self.run_shell_command(command)
                    outputs.append(output)
                    if ok:
                        return True, "\n\n".join(outputs)
                return False, "\n\n".join(outputs)
            return False, "winget was not found. ffmpeg requires a portable package or manual installation."

        return False, f"Unknown dependency: {dependency_name}"

    def post_install_path_fix(self, dependency_name: str) -> tuple[bool, str]:
        return self.path_manager.ensure_dependency_paths(dependency_name)
