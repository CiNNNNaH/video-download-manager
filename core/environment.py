from pathlib import Path


class EnvironmentPaths:
    def __init__(self, root: Path):
        self.root = root
        self.tools_dir = root / "tools"
        self.ffmpeg_dir = self.tools_dir / "ffmpeg"
        self.deno_dir = self.tools_dir / "deno"
        self.data_dir = root / "data"
        self.logs_dir = root / "logs"

    def portable_binary_candidates(self, name: str) -> list[Path]:
        exe_name = f"{name}.exe"
        if name == "ffmpeg":
            return [self.ffmpeg_dir / exe_name]
        if name == "deno":
            return [self.deno_dir / exe_name]
        if name == "yt-dlp":
            return [self.tools_dir / exe_name, self.root / exe_name]
        return [self.tools_dir / exe_name]
