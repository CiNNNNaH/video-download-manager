import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.url_utils import UrlUtils


def run() -> None:
    cases = {
        'https://www.youtube.com/watch?v=abc123&list=PL123&t=42': ('youtube', 'https://www.youtube.com/watch?v=abc123&t=42'),
        'https://youtu.be/abc123': ('youtube', 'https://youtu.be/abc123'),
        'https://vimeo.com/123456': ('vimeo', 'https://vimeo.com/123456'),
        'https://x.com/user/status/1': ('x', 'https://x.com/user/status/1'),
        'https://www.instagram.com/reel/abc/': ('instagram', 'https://www.instagram.com/reel/abc/'),
        'https://www.tiktok.com/@u/video/1': ('tiktok', 'https://www.tiktok.com/@u/video/1'),
        'https://soundcloud.com/a/b': ('soundcloud', 'https://soundcloud.com/a/b'),
        'https://example.org/video': ('example.org', 'https://example.org/video'),
    }

    for raw, (expected_family, expected_normalized) in cases.items():
        family = UrlUtils.detect_site_family(raw)
        normalized = UrlUtils.normalize_url(raw)
        assert family == expected_family, (raw, family, expected_family)
        assert normalized == expected_normalized, (raw, normalized, expected_normalized)

    print('multisite_site_family_regression passed')


if __name__ == '__main__':
    run()
