from dataclasses import dataclass, field


@dataclass
class ContentInfo:
    url: str = ""
    webpage_url: str = ""
    extractor: str = ""
    site: str = ""
    title: str = ""
    uploader: str = ""
    duration_seconds: int = 0
    duration_text: str = ""
    content_type: str = "video"
    is_playlist: bool = False
    playlist_count: int = 0
    login_required: bool = False
    thumbnail_url: str = ""
    upload_date: str = ""
    raw: dict = field(default_factory=dict)
