import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.format_processor import FormatProcessor


def test_simple_view_produces_representative_ladder_for_youtube_heights():
    formats = [
        {"format_id": "sb3", "ext": "mhtml", "resolution": "48x27", "vcodec": "none", "acodec": "none", "protocol": "mhtml", "format": "storyboard", "format_note": "storyboard"},
        {"format_id": "140", "ext": "m4a", "resolution": "audio only", "vcodec": "none", "acodec": "mp4a.40.2", "protocol": "https", "tbr": 129, "format": "audio only", "filesize": 5033164},
        {"format_id": "18", "ext": "mp4", "resolution": "640x338", "vcodec": "avc1", "acodec": "mp4a.40.2", "protocol": "https", "tbr": 425, "format": "18 - 360p", "filesize": 16536000},
        {"format_id": "135", "ext": "mp4", "resolution": "854x450", "vcodec": "avc1", "acodec": "none", "protocol": "https", "tbr": 207, "format": "135 - 480p", "filesize": 8042578},
        {"format_id": "136", "ext": "mp4", "resolution": "1280x676", "vcodec": "avc1", "acodec": "none", "protocol": "https", "tbr": 328, "format": "136 - 720p", "filesize": 12761170},
        {"format_id": "137", "ext": "mp4", "resolution": "1920x1012", "vcodec": "avc1", "acodec": "none", "protocol": "https", "tbr": 986, "format": "137 - 1080p", "filesize": 38335938},
        {"format_id": "400", "ext": "mp4", "resolution": "2560x1350", "vcodec": "av01", "acodec": "none", "protocol": "https", "tbr": 1157, "format": "400 - 1440p", "filesize": 44952453},
        {"format_id": "401", "ext": "mp4", "resolution": "3840x2026", "vcodec": "av01", "acodec": "none", "protocol": "https", "tbr": 2278, "format": "401 - 2160p", "filesize": 88552243},
    ]
    advanced = FormatProcessor.build_advanced_items(formats)
    simple = FormatProcessor.build_simple_items(advanced)
    labels = [item.display_label for item in simple]

    assert labels[0] == "Best Compatible"
    assert "Audio Only" in labels
    assert any("360p" in label for label in labels)
    assert any("480p" in label for label in labels)
    assert any("720p" in label for label in labels)
    assert any("1080p" in label for label in labels)
    assert any("1440p" in label for label in labels)
    assert any("2160p" in label for label in labels)
    assert len(simple) >= 8


def test_advanced_items_sort_by_filesize_desc_and_storyboards_last():
    formats = [
        {"format_id": "sb0", "ext": "mhtml", "resolution": "341x180", "vcodec": "none", "acodec": "none", "protocol": "mhtml", "format": "storyboard", "format_note": "storyboard"},
        {"format_id": "18", "ext": "mp4", "resolution": "640x338", "vcodec": "avc1", "acodec": "mp4a.40.2", "protocol": "https", "tbr": 425, "format": "18 - 360p", "filesize": 16536000},
        {"format_id": "401", "ext": "mp4", "resolution": "3840x2026", "vcodec": "av01", "acodec": "none", "protocol": "https", "tbr": 2278, "format": "401 - 2160p", "filesize": 88552243},
    ]
    advanced = FormatProcessor.build_advanced_items(formats)
    assert advanced[0].format_id == "401"
    assert advanced[-1].format_id == "sb0"
