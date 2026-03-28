from __future__ import annotations

from models.format_item import FormatItem


class FormatProcessor:
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

    @classmethod
    def build_advanced_items(cls, formats: list[dict]) -> list[FormatItem]:
        items: list[FormatItem] = []
        for fmt in formats or []:
            format_id = str(fmt.get("format_id", "")).strip()
            if not format_id:
                continue
            items.append(
                FormatItem(
                    display_label=fmt.get("format") or format_id,
                    format_id=format_id,
                    ext=fmt.get("ext", "-") or "-",
                    resolution=cls._resolution(fmt),
                    fps=str(fmt.get("fps", "") or "-"),
                    vcodec=fmt.get("vcodec", "-") or "-",
                    acodec=fmt.get("acodec", "-") or "-",
                    size_text=cls._human_size(fmt.get("filesize") or fmt.get("filesize_approx")),
                    tbr=cls._tbr(fmt),
                    proto=fmt.get("protocol", "-") or "-",
                    media_type=cls._media_type(fmt),
                    notes=cls._notes(fmt),
                    more_info=cls._more_info(fmt),
                    source_kind="advanced",
                    original_format_ids=format_id,
                )
            )
        return items

    @classmethod
    def build_simple_items(cls, advanced_items: list[FormatItem]) -> list[FormatItem]:
        simple: list[FormatItem] = []
        if not advanced_items:
            return simple

        muxed = [i for i in advanced_items if i.media_type == "muxed"]
        audio = [i for i in advanced_items if i.media_type == "audio only"]
        video = [i for i in advanced_items if i.media_type == "video only"]

        def pick_best(items: list[FormatItem], prefer_ext: str | None = None) -> FormatItem | None:
            if not items:
                return None
            def sort_key(item: FormatItem):
                res = item.resolution
                height = 0
                if "x" in res:
                    try:
                        height = int(res.split("x")[-1])
                    except ValueError:
                        height = 0
                elif res.endswith("p"):
                    try:
                        height = int(res[:-1])
                    except ValueError:
                        height = 0
                return (item.ext == prefer_ext if prefer_ext else False, height, item.fps not in {"", "-"}, item.size_text)
            return sorted(items, key=sort_key, reverse=True)[0]

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

        seen_labels = {item.display_label for item in simple}
        for target in [2160, 1440, 1080, 720, 480, 360]:
            matched = None
            for item in sorted(video + muxed, key=lambda x: x.resolution, reverse=True):
                res = item.resolution.lower()
                if f"x{target}" in res or res == f"{target}p":
                    matched = item
                    break
            if matched:
                label = f"{target}p {matched.ext.upper()}"
                if label in seen_labels:
                    continue
                seen_labels.add(label)
                simple.append(clone(matched, label))

        return simple
