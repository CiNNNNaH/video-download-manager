import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.browser_cookies import BrowserCookies
from core.remuxer import RemuxPlanner
from core.version_check import VersionCheck
from models.format_item import FormatItem


def run() -> None:
    assert VersionCheck.compare_versions("2026.03.17", "2026.03.17") == "ready"
    assert VersionCheck.compare_versions("2025.12.01", "2026.03.17") in {"outdated", "critical_outdated"}

    candidates = BrowserCookies.resolve_candidates("chrome", True)
    labels = [item.label for item in candidates]
    assert labels[0] == "Chrome"
    assert "Edge" in labels

    risky = FormatItem(ext="ts", media_type="video only", notes="remux gerekebilir")
    assert RemuxPlanner.determine_target(risky, "video+audio", True, "auto") == "mp4"

    safe = FormatItem(ext="mp4", media_type="muxed", notes="-")
    assert RemuxPlanner.determine_target(safe, "video+audio", True, "auto") == ""

    print("internal smoke test passed")


if __name__ == "__main__":
    run()
