from pathlib import Path


class EnvironmentPaths:
    def __init__(self, app_root: Path, bundle_root: Path | None = None):
        self.root = app_root
        self.app_root = app_root
        self.bundle_root = bundle_root or app_root

        self.tools_dir = app_root / "tools"
        self.ffmpeg_dir = self.tools_dir / "ffmpeg"
        self.ffmpeg_bin_dir = self.ffmpeg_dir / "bin"
        self.deno_dir = self.tools_dir / "deno"
        self.data_dir = app_root / "data"
        self.logs_dir = app_root / "logs"

        self.docs_dir = self.bundle_root / "docs"
        self.locales_dir = self.bundle_root / "locales"
        self.assets_dir = self.bundle_root / "assets"
        self.app_icon_png = self.assets_dir / "app_icon.png"
        self.app_icon_ico = self.assets_dir / "app_icon.ico"

    def ensure_runtime_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.tools_dir.mkdir(parents=True, exist_ok=True)

    def portable_binary_candidates(self, name: str) -> list[Path]:
        exe_name = f"{name}.exe"
        if name == "ffmpeg":
            return [
                self.ffmpeg_bin_dir / exe_name,
                self.ffmpeg_dir / exe_name,
                self.tools_dir / exe_name,
            ]
        if name == "deno":
            return [self.deno_dir / exe_name, self.tools_dir / exe_name]
        if name == "yt-dlp":
            return [self.tools_dir / exe_name, self.root / exe_name]
        return [self.tools_dir / exe_name]
