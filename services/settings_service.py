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

        raw = self._migrate_legacy_settings(raw)
        return AppSettings(**raw)

    def _migrate_legacy_settings(self, raw: dict) -> dict:
        migrated = dict(raw or {})
        if not migrated.get("language"):
            migrated["language"] = "en"
        if migrated.get("default_browser") == "cookies kapali":
            migrated["default_browser"] = "cookies_disabled"
        order = migrated.get("format_table_column_order") or []
        migrated["format_table_column_order"] = ["Choice" if item == "Secim" else item for item in order]
        widths = migrated.get("format_table_column_widths") or {}
        if "Secim" in widths and "Choice" not in widths:
            widths["Choice"] = widths.pop("Secim")
        migrated["format_table_column_widths"] = widths
        return migrated

    def save(self, settings: AppSettings) -> None:
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        with self.settings_path.open("w", encoding="utf-8") as f:
            json.dump(settings.__dict__, f, ensure_ascii=False, indent=2)
