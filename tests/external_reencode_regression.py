from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.app_settings import AppSettings


def run():
    settings = AppSettings(default_reencode_preset="mp4_h265_balanced")
    assert settings.default_reencode_preset == "mp4_h265_balanced"
    print("external reencode regression passed")


if __name__ == "__main__":
    run()
