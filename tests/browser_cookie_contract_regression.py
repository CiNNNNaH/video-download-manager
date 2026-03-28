import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.browser_cookies import BrowserCookies


def run() -> None:
    disabled = BrowserCookies.resolve_candidates("cookies kapali", False)
    assert len(disabled) == 1
    assert disabled[0].label == "Cookies Kapali"

    firefox_only = BrowserCookies.resolve_candidates("firefox", False)
    assert [item.label for item in firefox_only] == ["Firefox"]

    chrome_fallback = BrowserCookies.resolve_candidates("chrome", True)
    labels = [item.label for item in chrome_fallback]
    assert labels[0] == "Chrome"
    assert len(labels) == len(set(labels))
    assert set(labels) == {"Chrome", "Edge", "Brave", "Firefox"}

    print("browser cookie contract regression passed")


if __name__ == "__main__":
    run()
