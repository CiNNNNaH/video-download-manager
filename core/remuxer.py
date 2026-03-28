from __future__ import annotations

from models.format_item import FormatItem


class RemuxPlanner:
    @staticmethod
    def determine_target(
        selected_item: FormatItem,
        media_mode: str,
        remux_enabled: bool,
        target_container: str,
        format_selector: str = "",
    ) -> str:
        if not remux_enabled or media_mode == "audio only":
            return ""

        normalized_target = (target_container or "").strip().lower()
        selected_ext = (selected_item.ext or "").strip().lower()
        notes = (selected_item.notes or "").lower()

        if normalized_target and normalized_target not in {"auto", "keep original", ""}:
            return normalized_target

        if normalized_target == "keep original":
            return ""

        # Prefer natural container preservation when auto is selected.
        # If the chosen stream is already mp4 and we are pairing it with an mp4-friendly
        # audio selector, keep the final container as mp4 instead of unnecessarily falling
        # back to mkv.
        if normalized_target in {"", "auto"}:
            if selected_ext == "mp4" and "bestaudio[ext=m4a]" in format_selector:
                return "mp4"
            if selected_ext == "webm" and "bestaudio[ext=webm]" in format_selector:
                return "webm"

        risky_exts = {"ts", "flv"}
        risky_notes = "remux" in notes or "mkv" in notes
        if selected_ext in risky_exts or risky_notes:
            return "mp4"
        return ""
