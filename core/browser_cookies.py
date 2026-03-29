from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class BrowserCandidate:
    yt_dlp_name: str
    label: str


class BrowserCookies:
    NAME_MAP = {
        "chrome": BrowserCandidate("chrome", "Chrome"),
        "brave": BrowserCandidate("brave", "Brave"),
        "firefox": BrowserCandidate("firefox", "Firefox"),
        "edge": BrowserCandidate("edge", "Edge"),
        "cookies_disabled": BrowserCandidate("", "Cookies Disabled"),
    }

    FALLBACK_ORDER = ["chrome", "edge", "brave", "firefox"]

    @classmethod
    def resolve_candidates(cls, selected: str, fallback_enabled: bool) -> List[BrowserCandidate]:
        selected = (selected or "").strip().lower()
        if selected == "cookies_disabled":
            return [cls.NAME_MAP[selected]]

        candidates: list[BrowserCandidate] = []
        seen = set()
        if selected in cls.NAME_MAP:
            candidates.append(cls.NAME_MAP[selected])
            seen.add(selected)

        if fallback_enabled:
            for item in cls.FALLBACK_ORDER:
                if item not in seen:
                    candidates.append(cls.NAME_MAP[item])
                    seen.add(item)

        return candidates
