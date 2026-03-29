from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class I18nService:
    def __init__(self, locales_dir: Path, language: str = "en"):
        self.locales_dir = locales_dir
        self.language = "en"
        self._fallback: dict[str, str] = {}
        self._messages: dict[str, str] = {}
        self._load_fallback()
        self.set_language(language)

    def _read_locale(self, language: str) -> dict[str, str]:
        path = self.locales_dir / f"{language}.json"
        if not path.exists():
            return {}
        with path.open('r', encoding='utf-8') as f:
            data = json.load(f)
        return {str(k): str(v) for k, v in data.items()}

    def _load_fallback(self) -> None:
        self._fallback = self._read_locale('en')
        self._messages = dict(self._fallback)

    def set_language(self, language: str | None) -> None:
        chosen = (language or 'en').strip().lower() or 'en'
        if chosen not in {'en', 'tr'}:
            chosen = 'en'
        self.language = chosen
        selected = self._read_locale(chosen)
        self._messages = dict(self._fallback)
        self._messages.update(selected)

    def t(self, key: str, default: str | None = None, **kwargs: Any) -> str:
        text = self._messages.get(key) or default or self._fallback.get(key) or key
        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text
