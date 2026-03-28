import json
from pathlib import Path
from models.app_settings import AppSettings


class SettingsService:
    def __init__(self, settings_path: Path):
        self.settings_path = settings_path

    def load(self) -> AppSettings:
        if not self.settings_path.exists():
            settings = AppSettings()
            self.save(settings)
            return settings

        with self.settings_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)

        return AppSettings(**raw)

    def save(self, settings: AppSettings) -> None:
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        with self.settings_path.open("w", encoding="utf-8") as f:
            json.dump(settings.__dict__, f, ensure_ascii=False, indent=2)
