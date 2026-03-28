import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.error_handler import ErrorHandler


def run() -> None:
    assert ErrorHandler.classify_analyze_error("x", "HTTP Error 429: Too Many Requests").code == "rate_limited"
    assert ErrorHandler.classify_analyze_error("x", "This video is not available in your country").code == "geo_blocked"
    assert ErrorHandler.classify_analyze_error("x", "Sign in to confirm your age").code in {"age_gate", "login_required"}
    assert ErrorHandler.classify_download_error("HTTP Error 403: Forbidden").code == "forbidden"
    assert ErrorHandler.classify_download_error("ffmpeg missing: not found").code == "ffmpeg_missing"
    print("error taxonomy regression passed")


if __name__ == "__main__":
    run()
