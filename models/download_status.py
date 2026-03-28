from dataclasses import dataclass


@dataclass
class DownloadStatus:
    status: str = "idle"
    stage: str = "hazir"
    percent: float = 0.0
    speed_text: str = "-"
    eta_text: str = "-"
    downloaded_text: str = "-"
    total_text: str = "-"
    filename: str = ""
    final_path: str = ""
    message: str = ""
