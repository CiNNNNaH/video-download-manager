import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.app_settings import AppSettings


def run() -> None:
    settings = AppSettings()
    assert settings.fallback_browsers is True
    print("fallback default regression passed")


if __name__ == "__main__":
    run()
