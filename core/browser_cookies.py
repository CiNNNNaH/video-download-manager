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

    FALLBACK_ORDER = ["firefox", "cookies_disabled", "chrome", "edge", "brave"]

    @classmethod
    def resolve_candidates(cls, selected: str, fallback_enabled: bool) -> List[BrowserCandidate]:
        selected = (selected or "").strip().lower()
        if selected == "cookies_disabled":
            return [cls.NAME_MAP[selected]]

        candidates: list[BrowserCandidate] = []
        seen = set()

        def add(name: str) -> None:
            if name in cls.NAME_MAP and name not in seen:
                candidates.append(cls.NAME_MAP[name])
                seen.add(name)

        if fallback_enabled:
            # Firefox is the primary cookie source because it is the most reliable
            # path in the field. Chromium-family browsers remain secondary.
            add("firefox")
            if selected and selected != "firefox":
                add(selected)
            for item in cls.FALLBACK_ORDER:
                add(item)
        else:
            add(selected)

        return candidates
