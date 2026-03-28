from dataclasses import dataclass


@dataclass
class DependencyStatus:
    name: str
    installed: bool = False
    accessible: bool = False
    local_version: str = ""
    latest_version: str = ""
    status: str = "unknown"   # ready, warning, outdated, critical_outdated, missing, error
    message: str = ""
    resolved_path: str = ""
    install_action: str = ""
    install_command: str = ""
    source: str = ""  # portable, system, custom, unknown
    can_auto_fix: bool = False
    is_critical: bool = False
    details: str = ""
    suggested_fix: str = ""
    path_updated: bool = False

    @property
    def has_issue(self) -> bool:
        return self.status in {"missing", "outdated", "critical_outdated", "error"}

    @property
    def is_ready(self) -> bool:
        return self.status == "ready"


    @property
    def severity_label(self) -> str:
        mapping = {
            "ready": "OK",
            "outdated": "UYARI",
            "critical_outdated": "KRITIK",
            "missing": "KRITIK",
            "error": "HATA",
            "warning": "UYARI",
            "unknown": "BILINMIYOR",
        }
        return mapping.get(self.status, self.status.upper())

    @property
    def ui_summary(self) -> str:
        local = self.local_version or "-"
        latest = self.latest_version or "-"
        source = self.source or "-"
        return f"[{self.severity_label}] {self.name} | durum={self.status} | local={local} | latest={latest} | source={source} | {self.message}"
