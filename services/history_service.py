import json
from pathlib import Path


class HistoryService:
    def __init__(self, history_path: Path):
        self.history_path = history_path

    def load(self) -> dict:
        if not self.history_path.exists():
            data = {"recent_urls": [], "last_browser": "chrome", "last_download_dir": ""}
            self.save(data)
            return data

        with self.history_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, history: dict) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
