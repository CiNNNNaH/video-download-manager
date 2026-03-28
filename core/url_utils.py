from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


class UrlUtils:
    @staticmethod
    def is_valid_url(url: str) -> bool:
        if not url or not isinstance(url, str):
            return False
        parsed = urlparse(url.strip())
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    @staticmethod
    def normalize_url(url: str) -> str:
        value = (url or "").strip()
        if not value:
            return value

        parsed = urlparse(value)
        host = (parsed.netloc or "").lower()
        if host.startswith("www."):
            host = host[4:]

        # Treat YouTube watch URLs that contain both a concrete video id and a
        # playlist/radio context as single-video analysis targets by default.
        # This avoids playlist hangs in the single-item analysis workflow while
        # still keeping the selected video id intact.
        if host in {"youtube.com", "m.youtube.com", "music.youtube.com"} and parsed.path == "/watch":
            query = dict(parse_qsl(parsed.query, keep_blank_values=True))
            if query.get("v"):
                allowed = [("v", query["v"])]
                if query.get("t"):
                    allowed.append(("t", query["t"]))
                if query.get("start"):
                    allowed.append(("start", query["start"]))
                return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(allowed), ""))

        return value

    @staticmethod
    def detect_site_family(url: str) -> str:
        value = (url or "").strip()
        if not value:
            return "unknown"

        parsed = urlparse(value)
        host = (parsed.netloc or "").lower()
        if host.startswith("www."):
            host = host[4:]

        mapping = {
            "youtube.com": "youtube",
            "m.youtube.com": "youtube",
            "music.youtube.com": "youtube",
            "youtu.be": "youtube",
            "vimeo.com": "vimeo",
            "player.vimeo.com": "vimeo",
            "x.com": "x",
            "twitter.com": "x",
            "instagram.com": "instagram",
            "tiktok.com": "tiktok",
            "vm.tiktok.com": "tiktok",
            "facebook.com": "facebook",
            "fb.watch": "facebook",
            "dailymotion.com": "dailymotion",
            "bilibili.com": "bilibili",
            "twitch.tv": "twitch",
            "soundcloud.com": "soundcloud",
        }
        for candidate, family in mapping.items():
            if host == candidate or host.endswith('.' + candidate):
                return family
        return host or "generic"
