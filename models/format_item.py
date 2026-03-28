from dataclasses import dataclass


@dataclass
class FormatItem:
    display_label: str = ""
    format_id: str = ""
    ext: str = ""
    resolution: str = ""
    fps: str = ""
    vcodec: str = ""
    acodec: str = ""
    size_text: str = ""
    tbr: str = ""
    proto: str = ""
    media_type: str = ""
    notes: str = ""
    more_info: str = ""
    source_kind: str = "advanced"  # advanced or simple
    original_format_ids: str = ""
