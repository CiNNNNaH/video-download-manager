from __future__ import annotations

import math

from models.format_item import FormatItem


class FormatProcessor:
    SIMPLE_TARGETS = [144, 240, 360, 480, 720, 1080, 1440, 2160]

    @staticmethod
    def _human_size(value) -> str:
        if not value:
            return "-"
        size = float(value)
        units = ["B", "KB", "MB", "GB", "TB"]
        idx = 0
        while size >= 1024 and idx < len(units) - 1:
            size /= 1024
            idx += 1
        return f"{size:.1f} {units[idx]}"

    @staticmethod
    def _resolution(fmt: dict) -> str:
        resolution = fmt.get("resolution")
        if resolution:
            return str(resolution)
        height = fmt.get("height")
        width = fmt.get("width")
        if width and height:
            return f"{width}x{height}"
        if fmt.get("vcodec") == "none":
            return "audio only"
        return "-"

    @staticmethod
    def _media_type(fmt: dict) -> str:
        vcodec = fmt.get("vcodec", "")
        acodec = fmt.get("acodec", "")
        if vcodec != "none" and acodec != "none":
            return "muxed"
        if vcodec != "none":
            return "video only"
        return "audio only"

    @staticmethod
    def _file_type(fmt: dict) -> str:
        media_type = FormatProcessor._media_type(fmt)
        if media_type == "muxed":
            return "muxed"
        if media_type == "video only":
            return "video"
        return "audio"

    @staticmethod
    def _tbr(fmt: dict) -> str:
        value = fmt.get("tbr")
        if value in (None, ""):
            return "-"
        try:
            return f"{float(value):.0f}k"
        except Exception:
            return str(value)

    @staticmethod
    def _notes(fmt: dict) -> str:
        notes = []
        if fmt.get("dynamic_range"):
            notes.append(str(fmt.get("dynamic_range")))
        if fmt.get("format_note"):
            notes.append(str(fmt.get("format_note")))
        if fmt.get("container") and str(fmt.get("container")) not in {"none", "-"}:
            notes.append(str(fmt.get("container")))
        return ", ".join(dict.fromkeys(notes)) if notes else "-"

    @staticmethod
    def _more_info(fmt: dict) -> str:
        parts = []
        media_type = FormatProcessor._media_type(fmt)
        if media_type == "video only":
            parts.append("video only")
        elif media_type == "audio only":
            parts.append("audio only")
        protocol = fmt.get("protocol")
        if protocol and protocol not in {"-", "none"}:
            if "dash" in str(protocol).lower():
                parts.append("DASH")
            else:
                parts.append(str(protocol))
        if fmt.get("format_note"):
            parts.append(str(fmt.get("format_note")))
        if fmt.get("language"):
            parts.append(str(fmt.get("language")))
        if fmt.get("ext") == "m4a" and media_type == "audio only":
            parts.append("m4a_dash")
        return ", ".join(dict.fromkeys(parts)) if parts else "-"

    @staticmethod
    def _resolution_height(item: FormatItem) -> int:
        res = (item.resolution or "").lower()
        if "x" in res:
            try:
                return int(res.split("x")[-1])
            except ValueError:
                return 0
        if res.endswith("p"):
            try:
                return int(res[:-1])
            except ValueError:
                return 0
        return 0

    @staticmethod
    def _bitrate_value(item: FormatItem) -> float:
        raw = (item.tbr or "").strip().lower().replace("k", "")
        try:
            return float(raw)
        except ValueError:
            return 0.0

    @staticmethod
    def _is_storyboard(item: FormatItem) -> bool:
        text = f"{item.more_info} {item.display_label}".lower()
        return item.ext == "mhtml" or "storyboard" in text or item.media_type == "images"

    @classmethod
    def _rank_item(cls, item: FormatItem, prefer_ext: str | None = None) -> tuple:
        return (
            cls._is_storyboard(item) is False,
            item.media_type == "muxed",
            item.ext == prefer_ext if prefer_ext else False,
            cls._resolution_height(item),
            cls._bitrate_value(item),
            item.fps not in {"", "-"},
        )

    @classmethod
    def _normalize_simple_height(cls, item: FormatItem) -> int:
        height = cls._resolution_height(item)
        if height <= 0:
            return 0
        return min(cls.SIMPLE_TARGETS, key=lambda target: (abs(target - height), target))

    @staticmethod
    def _parse_size_bytes(value: float | int | None) -> int:
        if value in (None, ""):
            return 0
        try:
            return int(float(value))
        except Exception:
            return 0

    @staticmethod
    def _size_from_text(text: str) -> int:
        raw = (text or "").strip().upper()
        if not raw or raw == "-":
            return 0
        try:
            number, unit = raw.split()[:2]
            value = float(number)
        except Exception:
            return 0
        scale = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
        return int(value * scale.get(unit, 1))

    @classmethod
    def _sort_advanced_items(cls, items: list[FormatItem]) -> list[FormatItem]:
        def key(item: FormatItem) -> tuple:
            size_bytes = item.size_bytes or cls._size_from_text(item.size_text)
            return (
                cls._is_storyboard(item) is False,
                size_bytes,
                cls._resolution_height(item),
                cls._bitrate_value(item),
                item.media_type == "muxed",
            )

        return sorted(items, key=key, reverse=True)

    @classmethod
    def build_advanced_items(cls, formats: list[dict]) -> list[FormatItem]:
        items: list[FormatItem] = []
        for fmt in formats or []:
            format_id = str(fmt.get("format_id", "")).strip()
            if not format_id:
                continue
            size_bytes = cls._parse_size_bytes(fmt.get("filesize") or fmt.get("filesize_approx"))
            items.append(
                FormatItem(
                    display_label=fmt.get("format") or format_id,
                    format_id=format_id,
                    ext=fmt.get("ext", "-") or "-",
                    resolution=cls._resolution(fmt),
                    fps=str(fmt.get("fps", "") or "-"),
                    vcodec=fmt.get("vcodec", "-") or "-",
                    acodec=fmt.get("acodec", "-") or "-",
                    size_text=cls._human_size(size_bytes),
                    size_bytes=size_bytes,
                    tbr=cls._tbr(fmt),
                    proto=fmt.get("protocol", "-") or "-",
                    media_type=cls._media_type(fmt),
                    notes=cls._notes(fmt),
                    more_info=cls._more_info(fmt),
                    source_kind="advanced",
                    original_format_ids=format_id,
                )
            )
        return cls._sort_advanced_items(items)

    @classmethod
    def build_simple_items(cls, advanced_items: list[FormatItem]) -> list[FormatItem]:
        simple: list[FormatItem] = []
        if not advanced_items:
            return simple

        usable_items = [item for item in advanced_items if not cls._is_storyboard(item)]
        muxed = [i for i in usable_items if i.media_type == "muxed"]
        audio = [i for i in usable_items if i.media_type == "audio only"]
        video = [i for i in usable_items if i.media_type == "video only"]

        def pick_best(items: list[FormatItem], prefer_ext: str | None = None) -> FormatItem | None:
            if not items:
                return None
            return sorted(items, key=lambda item: cls._rank_item(item, prefer_ext), reverse=True)[0]

        def clone(item: FormatItem, label: str) -> FormatItem:
            return FormatItem(
                display_label=label,
                format_id=item.format_id,
                ext=item.ext,
                resolution=item.resolution,
                fps=item.fps,
                vcodec=item.vcodec,
                acodec=item.acodec,
                size_text=item.size_text,
                size_bytes=item.size_bytes,
                tbr=item.tbr,
                proto=item.proto,
                media_type=item.media_type,
                notes=item.notes,
                more_info=item.more_info,
                source_kind="simple",
                original_format_ids=item.original_format_ids,
            )

        best_muxed = pick_best(muxed, "mp4")
        if best_muxed:
            simple.append(clone(best_muxed, "Best Compatible"))

        audio_best = pick_best(audio, "m4a")
        if audio_best:
            simple.append(clone(audio_best, "Audio Only"))

        combined = muxed + video
        for target in cls.SIMPLE_TARGETS:
            candidates = [item for item in combined if cls._normalize_simple_height(item) == target]
            if not candidates:
                continue
            matched = pick_best(candidates, "mp4")
            if not matched:
                continue
            media_tag = "" if matched.media_type == "muxed" else " Video Only"
            label = f"{target}p{media_tag} ({matched.ext.upper()})"
            if any(existing.display_label == label for existing in simple):
                continue
            simple.append(clone(matched, label))

        return simple
