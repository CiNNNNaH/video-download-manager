from dataclasses import dataclass, field


@dataclass
class AppSettings:
    app_name: str = "Video Download Manager"
    version: str = "VDM_v1.2.0"
    theme: str = "system"  # light, dark, system
    default_browser: str = "chrome"
    fallback_browsers: bool = True
    default_download_dir: str = ""
    default_view_mode: str = "simple"  # simple, advanced
    remux_enabled: bool = True
    target_container: str = "auto"
    filename_template: str = "%(title)s.%(ext)s"
    default_media_mode: str = "video+audio"
    remember_last_browser: bool = True
    remember_last_download_dir: bool = True
    startup_dependency_check: bool = True
    auto_prompt_missing_dependencies: bool = True
    detailed_logging: bool = True
    yt_dlp_path: str = ""
    ffmpeg_path: str = ""
    deno_path: str = ""
    prefer_portable_tools: bool = True
    allow_system_path_updates: bool = False
    check_online_updates_on_startup: bool = True
    installer_prefer_winget: bool = True
    format_table_column_order: list[str] = field(default_factory=lambda: [
        "ID",
        "File Type",
        "Secim",
        "Resolution",
        "Filesize",
        "TBR",
        "VCodec",
        "ACodec",
        "Ext",
        "FPS",
        "Proto",
        "More Info",
    ])
    format_table_column_widths: dict[str, int] = field(default_factory=lambda: {
        "ID": 70,
        "File Type": 110,
        "Secim": 180,
        "Resolution": 110,
        "Filesize": 110,
        "TBR": 70,
        "VCodec": 150,
        "ACodec": 120,
        "Ext": 65,
        "FPS": 55,
        "Proto": 85,
        "More Info": 260,
    })
    default_reencode_preset: str = "mp4_h265_balanced"
