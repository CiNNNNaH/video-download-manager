from pathlib import Path

from core.environment import EnvironmentPaths


def test_environment_paths_runtime_dirs(tmp_path: Path):
    env = EnvironmentPaths(tmp_path)
    env.ensure_runtime_dirs()
    assert env.data_dir.exists()
    assert env.logs_dir.exists()
    assert env.tools_dir.exists()


def test_ffmpeg_portable_candidates_include_bin_folder(tmp_path: Path):
    env = EnvironmentPaths(tmp_path)
    candidates = env.portable_binary_candidates("ffmpeg")
    assert env.ffmpeg_bin_dir / "ffmpeg.exe" in candidates
