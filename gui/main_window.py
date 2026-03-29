from __future__ import annotations

import os
import sys
import subprocess
import traceback
import urllib.request
import tempfile
from pathlib import Path
import re

from PySide6.QtCore import QObject, Qt, QThread, Signal, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QCheckBox,
    QAbstractItemView,
    QFrame,
)

from core.downloader import DownloadRequest
from core.url_utils import UrlUtils
from gui.settings_dialog import SettingsDialog
from gui.setup_dialog import SetupDialog


class UiSignals(QObject):
    progress = Signal(object)
    completed = Signal(object)
    error = Signal(str)
    log = Signal(str)


class AnalyzeWorker(QObject):
    finished = Signal(object)
    crashed = Signal(str)

    def __init__(self, analyzer, url: str, browser: str, fallback_browsers: bool, log_service):
        super().__init__()
        self.analyzer = analyzer
        self.url = url
        self.browser = browser
        self.fallback_browsers = fallback_browsers
        self.log_service = log_service

    @Slot()
    def run(self):
        self.log_service.trace(
            "analyze_worker.run.enter",
            url=self.url,
            browser=self.browser,
            fallback=self.fallback_browsers,
        )
        try:
            result = self.analyzer.analyze(
                url=self.url,
                browser=self.browser,
                fallback_browsers=self.fallback_browsers,
            )
            self.log_service.trace(
                "analyze_worker.run.exit",
                url=self.url,
                browser=self.browser,
                ok=result.ok,
                used_browser=result.used_browser,
            )
            self.finished.emit(
                {
                    "url": self.url,
                    "browser": self.browser,
                    "fallback": self.fallback_browsers,
                    "result": result,
                }
            )
        except Exception:
            detail = traceback.format_exc()
            self.log_service.error(f"Analyze worker crashed | {detail.replace(chr(10), ' | ')}")
            self.crashed.emit(detail)


class MainWindow(QMainWindow):
    def __init__(
        self,
        settings,
        history,
        history_service,
        analyzer,
        downloader,
        log_service,
        dependency_checker,
        bootstrap_manager,
        path_manager,
        theme_service,
        settings_service,
        app,
        i18n,
    ):
        super().__init__()
        self.settings = settings
        self.history = history
        self.history_service = history_service
        self.analyzer = analyzer
        self.downloader = downloader
        self.log_service = log_service
        self.dependency_checker = dependency_checker
        self.bootstrap_manager = bootstrap_manager
        self.path_manager = path_manager
        self.theme_service = theme_service
        self.settings_service = settings_service
        self.app = app
        self.i18n = i18n
        self.t = i18n.t

        self.current_result = None
        self.current_view_mode = self.settings.default_view_mode
        self.current_formats = []
        self.last_completed_path = ""
        self.analysis_thread: QThread | None = None
        self.analysis_worker: AnalyzeWorker | None = None
        self.analysis_active = False
        self.pending_analysis_request: dict | None = None
        self._action_seq = 0
        self._last_logged_url = ""
        self._format_header_initializing = False
        self.format_columns = [
            "ID",
            "File Type",
            "Choice",
            "Resolution",
            "Filesize",
            "TBR",
            "VCodec",
            "ACodec",
            "Ext",
            "FPS",
            "Proto",
            "More Info",
        ]

        self.reencode_presets = {
            "mp4_h265_balanced": {
                "label": self.t("preset.h265_balanced"),
                "video_codec": "hevc_nvenc",
                "audio_codec": "aac",
                "audio_bitrate": "160k",
                "extra": ["-preset", "p5", "-cq", "28"],
                "suffix": "_reencode_h265_dengeli",
                "ext": ".mp4",
            },
            "mp4_h265_quality": {
                "label": self.t("preset.h265_quality"),
                "video_codec": "hevc_nvenc",
                "audio_codec": "aac",
                "audio_bitrate": "192k",
                "extra": ["-preset", "p7", "-cq", "23"],
                "suffix": "_reencode_h265_kalite",
                "ext": ".mp4",
            },
            "mp4_h264_compatible": {
                "label": self.t("preset.h264_compatible"),
                "video_codec": "h264_nvenc",
                "audio_codec": "aac",
                "audio_bitrate": "160k",
                "extra": ["-preset", "p5", "-cq", "23"],
                "suffix": "_reencode_h264_uyumlu",
                "ext": ".mp4",
            },
        }

        self.default_filename_template = "%(title)s.%(ext)s"
        self.filename_presets = [
            (self.t("filename.original_title"), self.default_filename_template),
            (self.t("filename.uploader_title"), "%(uploader)s - %(title)s.%(ext)s"),
            (self.t("filename.title_resolution"), "%(title)s - %(resolution)s.%(ext)s"),
            (self.t("filename.uploader_title_resolution"), "%(uploader)s - %(title)s - %(resolution)s.%(ext)s"),
            (self.t("filename.title_date"), "%(title)s - %(upload_date)s.%(ext)s"),
        ]

        self.ui_signals = UiSignals()
        self.ui_signals.progress.connect(self._on_download_progress)
        self.ui_signals.completed.connect(self._on_download_completed)
        self.ui_signals.error.connect(self._on_download_error)
        self.ui_signals.log.connect(self._append_log)

        self.setWindowTitle(f"{settings.app_name} - {settings.version}")
        self.resize(1440, 900)

        self._build_ui()
        self.log_service.info("Main window initialized")
        self.log_service.trace("mainwindow.init.complete", view_mode=self.current_view_mode)
        self._run_startup_checks(startup=True)

    def _next_action_id(self) -> str:
        self._action_seq += 1
        return f"A{self._action_seq:05d}"

    def _trace(self, event: str, **fields) -> None:
        self.log_service.trace(event, action_id=self._next_action_id(), **fields)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(8)

        top_row = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(self.t("main.url_placeholder"))
        self.paste_button = QPushButton(self.t("main.paste"))
        self.clear_button = QPushButton(self.t("main.clear"))
        self.analyze_button = QPushButton(self.t("main.analyze"))
        self.open_browser_button = QPushButton(self.t("main.open_in_browser"))
        self.settings_button = QPushButton(self.t("main.settings"))
        top_row.addWidget(self.url_input, 1)
        top_row.addWidget(self.paste_button)
        top_row.addWidget(self.clear_button)
        top_row.addWidget(self.analyze_button)
        top_row.addWidget(self.open_browser_button)
        top_row.addWidget(self.settings_button)
        root.addLayout(top_row)

        second_row = QHBoxLayout()
        self.url_history_combo = QComboBox()
        self.url_history_combo.addItem(self.t("main.history_placeholder"))
        for item in self.history.get("recent_urls", []):
            self.url_history_combo.addItem(item)
        self.url_history_combo.currentTextChanged.connect(self._history_selected)

        self.simple_view_button = QPushButton(self.t("main.simple_view"))
        self.advanced_view_button = QPushButton(self.t("main.advanced_view"))
        self.fallback_checkbox = QCheckBox(self.t("main.browser_fallback"))
        self.fallback_checkbox.setChecked(self.settings.fallback_browsers)
        second_row.addWidget(self.url_history_combo, 1)
        second_row.addWidget(self.simple_view_button)
        second_row.addWidget(self.advanced_view_button)
        second_row.addWidget(self.fallback_checkbox)
        root.addLayout(second_row)

        mid_row = QHBoxLayout()

        browser_box = QGroupBox(self.t("main.browser_group"))
        browser_box.setMaximumWidth(280)
        browser_layout = QVBoxLayout(browser_box)
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["chrome", "brave", "firefox", "edge", "cookies_disabled"])
        current_browser = self.settings.default_browser or self.history.get("last_browser", "chrome")
        self.browser_combo.setCurrentText(current_browser)
        browser_layout.addWidget(QLabel(self.t("main.cookie_source")))
        browser_layout.addWidget(self.browser_combo)
        self.cookie_status_label = QLabel(self.t("main.cookies_unknown"))
        self.cookie_status_label.setWordWrap(True)
        browser_layout.addWidget(self.cookie_status_label)

        status_box = QGroupBox(self.t("main.system_status"))
        status_layout = QVBoxLayout(status_box)
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(120)
        button_row = QHBoxLayout()
        self.refresh_deps_button = QPushButton(self.t("main.check_now"))
        self.refresh_updates_button = QPushButton(self.t("main.check_updates"))
        self.refresh_deps_button.clicked.connect(lambda: self._run_startup_checks(startup=False))
        self.refresh_updates_button.clicked.connect(self._force_online_check)
        button_row.addWidget(self.refresh_deps_button)
        button_row.addWidget(self.refresh_updates_button)
        status_layout.addWidget(self.status_text)
        status_layout.addLayout(button_row)

        mid_row.addWidget(browser_box, 0)
        mid_row.addWidget(status_box, 1)
        root.addLayout(mid_row)

        info_row = QHBoxLayout()
        info_box = QGroupBox(self.t("main.content_info"))
        info_layout = QVBoxLayout(info_box)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(125)
        info_layout.addWidget(self.info_text)

        thumb_box = QGroupBox(self.t("main.thumbnail"))
        thumb_box.setMaximumWidth(360)
        thumb_layout = QVBoxLayout(thumb_box)
        self.thumbnail_label = QLabel(self.t("main.no_preview"))
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setMinimumSize(220, 124)
        self.thumbnail_label.setMaximumHeight(125)
        thumb_layout.addWidget(self.thumbnail_label)

        info_row.addWidget(info_box, 1)
        info_row.addWidget(thumb_box, 0)
        root.addLayout(info_row)

        self.media_table_panel = QFrame()
        self.media_table_panel.setObjectName("mediaTablePanel")
        self.media_table_panel.setFrameShape(QFrame.Shape.StyledPanel)
        self.media_table_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        media_table_layout = QVBoxLayout(self.media_table_panel)
        media_table_layout.setContentsMargins(0, 0, 0, 0)
        media_table_layout.setSpacing(0)

        self.format_table = QTableWidget(0, len(self.format_columns))
        self.format_table.setHorizontalHeaderLabels(self.format_columns)
        self.format_table.itemSelectionChanged.connect(self._update_format_summary)
        self.format_table.setAlternatingRowColors(False)
        self.format_table.setWordWrap(False)
        header = self.format_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionsMovable(True)
        header.setStretchLastSection(False)
        self.format_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.format_table.setMinimumHeight(210)
        self.format_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        media_table_layout.addWidget(self.format_table, 1)

        root.addWidget(self.media_table_panel, 7)

        self.selection_summary_panel = QFrame()
        self.selection_summary_panel.setObjectName("selectionSummaryPanel")
        self.selection_summary_panel.setFrameShape(QFrame.Shape.StyledPanel)
        self.selection_summary_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.selection_summary_panel.setFixedHeight(34)
        summary_panel_layout = QHBoxLayout(self.selection_summary_panel)
        summary_panel_layout.setContentsMargins(8, 4, 8, 4)
        summary_panel_layout.setSpacing(8)
        self.selection_summary_label = QLabel(f"{self.t('main.selected_format_group')}:" )
        self.selection_summary_label.setObjectName("selectionSummaryCaption")
        self.selection_summary_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.selection_summary_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.tech_summary = QLabel()
        self.tech_summary.setObjectName("selectionSummaryValue")
        self.tech_summary.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.tech_summary.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.tech_summary.setMinimumHeight(20)
        self.tech_summary.setMaximumHeight(20)
        self.tech_summary.setWordWrap(False)
        self.tech_summary.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.tech_summary.setText(self.t("main.selected_format_summary"))
        summary_panel_layout.addWidget(self.selection_summary_label, 0)
        summary_panel_layout.addWidget(self.tech_summary, 1)
        root.addWidget(self.selection_summary_panel, 0)

        download_box = QGroupBox(self.t("main.download_settings"))
        download_layout = QVBoxLayout(download_box)

        row1 = QHBoxLayout()
        self.download_dir_label = QLabel(self._current_download_dir())
        self.download_dir_button = QPushButton(self.t("main.choose_folder"))
        row1.addWidget(QLabel(self.t("main.output_folder")))
        row1.addWidget(self.download_dir_label, 1)
        row1.addWidget(self.download_dir_button)
        download_layout.addLayout(row1)

        row2 = QHBoxLayout()
        self.filename_preset_combo = QComboBox()
        for label, template in self.filename_presets:
            self.filename_preset_combo.addItem(label, template)
        self.filename_preset_combo.addItem(self.t("common.manual"), "__manual__")
        self.manual_filename_edit = QLineEdit()
        self.manual_filename_edit.setPlaceholderText(self.t("main.filename_placeholder"))
        self.filename_preview_edit = QLineEdit()
        self.filename_preview_edit.setReadOnly(True)

        self.media_mode_combo = QComboBox()
        self.media_mode_combo.addItems(["video+audio", "video only", "audio only"])
        self.media_mode_combo.setCurrentText(self.settings.default_media_mode)

        self.target_container_combo = QComboBox()
        self.target_container_combo.addItems(["auto", "mp4", "mkv", "keep original"])
        self.target_container_combo.setCurrentText(self.settings.target_container)

        self.remux_checkbox = QCheckBox(self.t("main.remux_if_needed"))
        self.remux_checkbox.setChecked(self.settings.remux_enabled)

        row2.addWidget(QLabel(self.t("main.media_mode")))
        row2.addWidget(self.media_mode_combo)
        row2.addWidget(QLabel(self.t("main.container")))
        row2.addWidget(self.target_container_combo)
        row2.addWidget(self.remux_checkbox)
        download_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel(self.t("main.filename_pattern")))
        row3.addWidget(self.filename_preset_combo, 1)
        row3.addWidget(self.manual_filename_edit, 2)
        download_layout.addLayout(row3)

        row3b = QHBoxLayout()
        row3b.addWidget(QLabel(self.t("main.result_filename")))
        row3b.addWidget(self.filename_preview_edit, 1)
        download_layout.addLayout(row3b)

        row4 = QHBoxLayout()
        self.download_button = QPushButton(self.t("main.download"))
        self.stop_button = QPushButton(self.t("main.stop"))
        self.open_folder_button = QPushButton(self.t("main.open_folder"))
        self.open_file_button = QPushButton(self.t("main.open_file"))
        self.reencode_preset_combo = QComboBox()
        for preset_key, preset_data in self.reencode_presets.items():
            self.reencode_preset_combo.addItem(preset_data["label"], preset_key)
        preset_index = self.reencode_preset_combo.findData(self.settings.default_reencode_preset)
        self.reencode_preset_combo.setCurrentIndex(preset_index if preset_index >= 0 else 0)
        self.reencode_button = QPushButton(self.t("main.reencode_button"))
        self.download_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.open_file_button.setEnabled(False)
        self.reencode_button.setEnabled(False)
        self.reencode_button.setEnabled(False)
        self.open_folder_button.setEnabled(True)
        self.reencode_preset_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        row4.addWidget(self.download_button)
        row4.addWidget(self.stop_button)
        row4.addWidget(self.open_folder_button)
        row4.addWidget(self.open_file_button)
        row4.addWidget(self.reencode_preset_combo, 1)
        row4.addWidget(self.reencode_button)
        download_layout.addLayout(row4)
        root.addWidget(download_box, 0)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        root.addWidget(self.progress_bar)

        self.progress_details = QLabel(self.t("main.ready_progress"))
        root.addWidget(self.progress_details)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(110)
        root.addWidget(self.log_output, 0)
        root.setStretch(0, 0)
        root.setStretch(1, 0)
        root.setStretch(2, 1)
        root.setStretch(3, 1)
        root.setStretch(4, 7)
        root.setStretch(5, 0)
        root.setStretch(6, 0)
        root.setStretch(7, 0)
        root.setStretch(8, 0)
        root.setStretch(9, 0)
        self.statusBar().showMessage(self.t("main.ready"))

        self.download_dir_button.clicked.connect(self._select_download_dir)
        self.settings_button.clicked.connect(self._open_settings)
        self.clear_button.clicked.connect(self._clear_form)
        self.paste_button.clicked.connect(self._paste_url)
        self.analyze_button.clicked.connect(self._request_analyze)
        self.open_browser_button.clicked.connect(self._open_in_selected_browser)
        self.simple_view_button.clicked.connect(lambda: self._switch_view_mode("simple"))
        self.advanced_view_button.clicked.connect(lambda: self._switch_view_mode("advanced"))
        self.download_button.clicked.connect(self._start_download)
        self.stop_button.clicked.connect(self._stop_download)
        self.open_folder_button.clicked.connect(self._open_download_folder)
        self.open_file_button.clicked.connect(self._open_last_file)
        self.reencode_button.clicked.connect(self._launch_external_reencode)
        self.url_input.textChanged.connect(self._on_url_text_changed)
        self.url_input.returnPressed.connect(self._request_analyze)
        self.browser_combo.currentTextChanged.connect(self._persist_runtime_preferences)
        self.browser_combo.currentTextChanged.connect(self._update_cookie_mode_hint)
        self.media_mode_combo.currentTextChanged.connect(self._persist_runtime_preferences)
        self.target_container_combo.currentTextChanged.connect(self._persist_runtime_preferences)
        self.target_container_combo.currentTextChanged.connect(self._update_filename_preview)
        self.remux_checkbox.toggled.connect(self._persist_runtime_preferences)
        self.fallback_checkbox.toggled.connect(self._persist_runtime_preferences)
        self.fallback_checkbox.toggled.connect(self._update_cookie_mode_hint)
        self.reencode_preset_combo.currentIndexChanged.connect(self._persist_runtime_preferences)
        self.filename_preset_combo.currentIndexChanged.connect(self._on_filename_controls_changed)
        self.manual_filename_edit.textChanged.connect(self._on_filename_controls_changed)
        header.sectionMoved.connect(self._on_format_header_changed)
        header.sectionResized.connect(self._on_format_header_changed)
        self._apply_saved_format_table_layout()
        self._reset_filename_controls(persist=False)
        self._update_filename_preview()
        self._update_cookie_mode_hint()


    def _persist_runtime_preferences(self, *_args) -> None:
        self.settings.default_browser = self.browser_combo.currentText()
        self.settings.default_media_mode = self.media_mode_combo.currentText()
        self.settings.target_container = self.target_container_combo.currentText()
        self.settings.remux_enabled = self.remux_checkbox.isChecked()
        self.settings.fallback_browsers = self.fallback_checkbox.isChecked()
        self.settings.filename_template = self._effective_filename_template()
        self.settings.default_reencode_preset = self.reencode_preset_combo.currentData() or "mp4_h265_balanced"
        self.settings_service.save(self.settings)
        self._update_filename_preview()
        self._update_cookie_mode_hint()
        self._trace(
            "persist_runtime_preferences",
            browser=self.settings.default_browser,
            media_mode=self.settings.default_media_mode,
            container=self.settings.target_container,
            remux=self.settings.remux_enabled,
            fallback=self.settings.fallback_browsers,
            reencode_preset=self.settings.default_reencode_preset,
        )

    def _apply_filename_controls_from_template(self, template: str) -> None:
        matched_index = -1
        for index in range(self.filename_preset_combo.count() - 1):
            if self.filename_preset_combo.itemData(index) == template:
                matched_index = index
                break
        self.filename_preset_combo.blockSignals(True)
        self.manual_filename_edit.blockSignals(True)
        try:
            if matched_index >= 0:
                self.filename_preset_combo.setCurrentIndex(matched_index)
                self.manual_filename_edit.setText(template)
                self.manual_filename_edit.setEnabled(False)
            else:
                self.filename_preset_combo.setCurrentIndex(self.filename_preset_combo.count() - 1)
                self.manual_filename_edit.setText(template)
                self.manual_filename_edit.setEnabled(True)
        finally:
            self.filename_preset_combo.blockSignals(False)
            self.manual_filename_edit.blockSignals(False)

    def _effective_filename_template(self) -> str:
        current = self.filename_preset_combo.currentData()
        if current == "__manual__":
            return self.manual_filename_edit.text().strip() or self.default_filename_template
        return current or self.default_filename_template

    def _safe_filename_component(self, value: str) -> str:
        cleaned = (value or "").strip()
        cleaned = re.sub(r'[\/:*?"<>|]+', '-', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip(' .')
        return cleaned or 'video'

    def _safe_optional_filename_component(self, value: str, fallback: str = "") -> str:
        cleaned = (value or "").strip()
        cleaned = re.sub(r'[\/:*?"<>|]+', '-', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip(' .')
        return cleaned or fallback

    def _display_resolution_for_filename(self, item) -> str:
        if item and item.resolution:
            match = re.match(r"^(\d+)x(\d+)$", str(item.resolution))
            if match:
                height = match.group(2)
                return f"{height}p"
            resolution = str(item.resolution).strip()
            if resolution and resolution.lower() != "audio only":
                return resolution
        return "original"

    def _display_upload_date_for_filename(self, content) -> str:
        raw_date = getattr(content, "upload_date", "") if content else ""
        if raw_date and len(raw_date) == 8 and raw_date.isdigit():
            return f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
        return self._safe_optional_filename_component(raw_date, "unknown-date")

    def _reset_filename_controls(self, persist: bool = False) -> None:
        self.filename_preset_combo.blockSignals(True)
        self.manual_filename_edit.blockSignals(True)
        try:
            self.filename_preset_combo.setCurrentIndex(0)
            self.manual_filename_edit.clear()
            self.manual_filename_edit.setEnabled(False)
        finally:
            self.filename_preset_combo.blockSignals(False)
            self.manual_filename_edit.blockSignals(False)
        if persist:
            self.settings.filename_template = self.default_filename_template
            self.settings_service.save(self.settings)
        self._update_filename_preview()
        self._update_cookie_mode_hint()

    def _preview_extension(self) -> str:
        container = self.target_container_combo.currentText()
        if container not in {"auto", "keep original"}:
            return container
        item = self._selected_format_item()
        if item and item.ext:
            return item.ext
        if self.last_completed_path:
            suffix = Path(self.last_completed_path).suffix.lstrip('.')
            if suffix:
                return suffix
        return 'mp4'

    def _update_filename_preview(self, *_args) -> None:
        template = self._effective_filename_template()
        ext = self._preview_extension()
        content = self.current_result.content if self.current_result and self.current_result.content else None
        item = self._selected_format_item()
        replacements = {
            '%(title)s': self._safe_filename_component(content.title if content else 'video'),
            '%(uploader)s': self._safe_filename_component(content.uploader if content and content.uploader else 'Unknown Uploader'),
            '%(resolution)s': self._safe_filename_component(self._display_resolution_for_filename(item)),
            '%(upload_date)s': self._safe_filename_component(self._display_upload_date_for_filename(content)),
            '%(ext)s': ext,
        }
        preview = template
        for key, value in replacements.items():
            preview = preview.replace(key, value)
        preview = self._safe_filename_component(preview.replace('.' + ext, '')) + f'.{ext}' if '%(ext)s' not in template else preview
        if preview.endswith('..' + ext):
            preview = preview[:-len(ext)-1] + ext
        self.filename_preview_edit.setText(preview)

    def _on_filename_controls_changed(self, *_args) -> None:
        is_manual = self.filename_preset_combo.currentData() == "__manual__"
        if not is_manual and self.manual_filename_edit.text():
            self.manual_filename_edit.blockSignals(True)
            self.manual_filename_edit.clear()
            self.manual_filename_edit.blockSignals(False)
        self.manual_filename_edit.setEnabled(is_manual)
        self._update_filename_preview()

    def _default_format_column_order(self) -> list[str]:
        return [
            "ID",
            "File Type",
            "Choice",
            "Resolution",
            "Filesize",
            "TBR",
            "VCodec",
            "ACodec",
            "Ext",
            "FPS",
            "Proto",
            "More Info",
        ]

    def _apply_saved_format_table_layout(self) -> None:
        header = self.format_table.horizontalHeader()
        order = [name for name in self.settings.format_table_column_order if name in self.format_columns]
        for name in self.format_columns:
            if name not in order:
                order.append(name)

        widths = dict(self.settings.format_table_column_widths or {})
        self._format_header_initializing = True
        try:
            for visual_index, name in enumerate(order):
                logical_index = self.format_columns.index(name)
                current_visual = header.visualIndex(logical_index)
                if current_visual != visual_index:
                    header.moveSection(current_visual, visual_index)
            for name in self.format_columns:
                width = int(widths.get(name, 120))
                self.format_table.setColumnWidth(self.format_columns.index(name), max(55, width))
        finally:
            self._format_header_initializing = False
        self._save_format_table_layout()

    def _save_format_table_layout(self) -> None:
        header = self.format_table.horizontalHeader()
        order = []
        widths = {}
        for visual_index in range(header.count()):
            logical_index = header.logicalIndex(visual_index)
            name = self.format_columns[logical_index]
            order.append(name)
            widths[name] = int(self.format_table.columnWidth(logical_index))
        self.settings.format_table_column_order = order
        self.settings.format_table_column_widths = widths
        self.settings_service.save(self.settings)

    def _on_format_header_changed(self, *_args) -> None:
        if self._format_header_initializing:
            return
        self._save_format_table_layout()
        self._trace("format_header_changed", order=self.settings.format_table_column_order)

    def _current_download_dir(self) -> str:
        return self.settings.default_download_dir or self.history.get("last_download_dir") or str(Path.home() / "Downloads")

    def _append_log(self, text: str) -> None:
        self.log_output.append(text)

    def _set_analysis_ui_state(self, active: bool) -> None:
        self.analysis_active = active
        self.analyze_button.setEnabled(True)
        self.clear_button.setEnabled(not active)
        self.paste_button.setEnabled(not active)
        self.url_history_combo.setEnabled(not active)
        self.browser_combo.setEnabled(not active)
        self.fallback_checkbox.setEnabled(not active)

    def _on_url_text_changed(self, text: str) -> None:
        value = text.strip()
        if not value or value == self._last_logged_url:
            return
        if value.startswith("http://") or value.startswith("https://"):
            previous = self._last_logged_url or "-"
            self._last_logged_url = value
            self.log_service.info(f"URL updated | previous={previous} | current={value}")
            self.log_service.trace("url_input.changed", previous=previous, new=value)

    def _summarize_dependency_issues(self, statuses) -> str:
        managed = [item for item in statuses if item.name in {"yt-dlp", "ffmpeg", "deno"}]
        critical = [item.name for item in managed if item.status in {"missing", "critical_outdated", "error"}]
        warnings = [item.name for item in managed if item.status == "outdated"]
        if critical:
            return f"Critical dependency issue: {', ' .join(critical)}"
        if warnings:
            return f"Outdated dependency: {', ' .join(warnings)}"
        return self.t("status.dependencies_ready")

    def _update_cookie_mode_hint(self, *_args) -> None:
        selected = self.browser_combo.currentText()
        fallback = self.fallback_checkbox.isChecked()
        if selected == "cookies_disabled":
            hint = self.t("main.cookies_disabled_status")
        elif fallback:
            hint = self.t("main.cookie_status_fallback_hint", browser=selected)
        else:
            hint = self.t("main.cookie_status_selected_hint", browser=selected)
        self.cookie_status_label.setText(hint)

    def _render_statuses(self, statuses, log_to_ui: bool = False, prefix: str = "") -> None:
        self._trace("render_statuses.enter", count=len(statuses), prefix=prefix, log_to_ui=log_to_ui)
        self.status_text.clear()
        rendered_lines = []
        for item in statuses:
            line = item.ui_summary
            self.status_text.append(line)
            rendered_lines.append(line)
            self.log_service.info(line)
            if item.details:
                self.log_service.debug(f"{item.name} details: {item.details}")
        summary = self._summarize_dependency_issues(statuses)
        self.status_text.append("")
        self.status_text.append(self.t("main.log_dependency_summary", summary=summary))
        self.log_service.info(f"Dependency summary | {summary}")
        if log_to_ui and rendered_lines:
            if prefix:
                self._append_log(prefix)
            self._append_log("; ".join(rendered_lines))
            self._append_log(self.t("main.log_dependency_summary", summary=summary))
        self._trace("render_statuses.exit", count=len(rendered_lines), summary=summary)

    def _run_startup_checks(self, startup: bool = False):
        self._trace("startup_checks.enter", startup=startup)
        if startup and not self.settings.startup_dependency_check:
            self.statusBar().showMessage(self.t("main.startup_check_disabled"))
            self._append_log(self.t("main.startup_check_skipped"))
            self._trace("startup_checks.skip", startup=startup)
            return

        statuses = self.bootstrap_manager.scan()
        self._render_statuses(statuses, log_to_ui=not startup, prefix=self.t("main.dependency_check_refreshed"))

        issues = self.bootstrap_manager.missing_or_outdated(statuses)
        summary = self._summarize_dependency_issues(statuses)
        self._trace("startup_checks.scan.complete", startup=startup, issues=len(issues), summary=summary)
        if issues and self.settings.auto_prompt_missing_dependencies:
            dlg = SetupDialog(issues, self.i18n, self)
            if dlg.exec() and dlg.install_requested:
                selected = [item for item in issues if item.name in dlg.selected_names]
                if dlg.path_checkbox.isChecked():
                    self.settings.allow_system_path_updates = True
                    self.settings_service.save(self.settings)

                results = self.bootstrap_manager.apply_actions(selected)
                for result in results:
                    path_state = result.get('path_state') or ('ok' if result['path_ok'] else 'failed')
                    resolved_path = result.get('resolved_path') or '-'
                    msg = (
                        f"{result['name']}: {'ok' if result['ok'] else 'failed'} | "
                        f"verify={result['verified_status']} | version={result['verified_version'] or '-'} | "
                        f"path={path_state} | resolved_path={resolved_path} | "
                        f"verify_message={result['verified_message'] or '-'}"
                    )
                    self._append_log(msg)
                    self.log_service.info(msg if result["ok"] else f"ERROR {msg}")
                    if result["output"]:
                        self.log_service.debug(f"{result['name']} install output: {result['output']}")
                    if result["path_output"]:
                        self.log_service.debug(f"{result['name']} path output: {result['path_output']}")
                self.statusBar().showMessage(self.t("main.install_update_completed"))
                statuses = self.bootstrap_manager.scan()
                self._render_statuses(statuses, log_to_ui=True, prefix=self.t("main.post_install_status"))
                self.statusBar().showMessage(self._summarize_dependency_issues(statuses))
                self._trace("startup_checks.install.complete", selected=[item.name for item in selected])
                return

        self.statusBar().showMessage(summary)
        self._trace("startup_checks.exit", startup=startup, summary=summary)

    def _force_online_check(self):
        self._trace("force_online_check.enter")
        original = self.settings.check_online_updates_on_startup
        try:
            self.settings.check_online_updates_on_startup = True
            statuses = self.bootstrap_manager.scan()
            self._render_statuses(statuses, log_to_ui=True, prefix=self.t("main.online_update_check_completed"))
            summary = ", ".join(f"{item.name}={item.latest_version or '-'}" for item in statuses[:3])
            self.statusBar().showMessage(f"{self.t("main.online_update_check_completed")} | {summary}")
        finally:
            self.settings.check_online_updates_on_startup = original
            self._trace("force_online_check.exit")

    def _open_settings(self):
        self._trace("open_settings.enter")
        dlg = SettingsDialog(self.settings, self.i18n, self)
        if dlg.exec():
            dlg.apply_to_settings()
            self.settings.fallback_browsers = self.fallback_checkbox.isChecked()
            self.settings_service.save(self.settings)
            self.theme_service.apply_theme(self.app, self.settings.theme)
            self.browser_combo.setCurrentText(self.settings.default_browser)
            self.fallback_checkbox.setChecked(self.settings.fallback_browsers)
            self._update_cookie_mode_hint()
            self._apply_filename_controls_from_template(self.settings.filename_template)
            self._update_filename_preview()
            self.media_mode_combo.setCurrentText(self.settings.default_media_mode)
            self.target_container_combo.setCurrentText(self.settings.target_container)
            self.remux_checkbox.setChecked(self.settings.remux_enabled)
            self.download_dir_label.setText(self._current_download_dir())
            self.log_service.info(
                f"Settings updated | theme={self.settings.theme} | browser={self.settings.default_browser} | media_mode={self.settings.default_media_mode} | container={self.settings.target_container}"
            )
            self.statusBar().showMessage(self.t("main.settings_updated", theme=self.settings.theme))
        self._trace("open_settings.exit")

    def _select_download_dir(self):
        self._trace("select_download_dir.enter")
        folder = QFileDialog.getExistingDirectory(self, self.t("main.choose_download_folder"), self._current_download_dir())
        if folder:
            self.settings.default_download_dir = folder
            self.history["last_download_dir"] = folder
            self.settings_service.save(self.settings)
            self.history_service.save(self.history)
            self.download_dir_label.setText(folder)
            self.log_service.info(f"Download folder updated: {folder}")
            self.statusBar().showMessage(self.t("main.folder_selected", folder=folder))
        self._trace("select_download_dir.exit", selected=bool(folder), folder=folder or "")

    def _reset_analysis_views(self, reason: str) -> None:
        self._trace("reset_analysis_views.enter", reason=reason)
        self.info_text.clear()
        self.thumbnail_label.clear()
        self.thumbnail_label.setText(self.t("main.no_preview"))
        self.format_table.setRowCount(0)
        self.tech_summary.clear()
        self.download_button.setEnabled(False)
        self.current_result = None
        self.current_formats = []
        self.last_completed_path = ""
        self.open_file_button.setEnabled(False)
        self.reencode_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_details.setText(self.t("main.ready_progress"))
        self.log_service.info(f"Analysis views reset | reason={reason}")
        self._update_filename_preview()
        self._trace("reset_analysis_views.exit", reason=reason)

    def _clear_form(self):
        self._trace("clear_form.enter", analysis_active=self.analysis_active, download_active=self.downloader.is_active)
        if self.downloader.is_active:
            self.show_error(self.t("main.clear_blocked"))
            return
        if self.analysis_active:
            self.pending_analysis_request = None
            self.url_input.clear()
            self.statusBar().showMessage(self.t("main.clear_waiting_for_analysis"))
            self.log_service.info("Clear form requested | only the URL field was cleared because an analysis is active")
            self._trace("clear_form.defer", analysis_active=True)
            return
        self.url_input.clear()
        self._reset_analysis_views("clear_form")
        self.log_service.info("Form cleared")
        self.statusBar().showMessage(self.t("main.form_cleared"))
        self._trace("clear_form.exit")

    def _paste_url(self):
        clipboard = self.app.clipboard()
        value = clipboard.text().strip()
        self.url_input.setText(value)
        self._trace("paste_url", length=len(value), has_value=bool(value))

    def _queue_pending_analysis(self, url: str, browser: str, fallback: bool) -> None:
        self.pending_analysis_request = {"url": url, "browser": browser, "fallback": fallback}
        self._append_log(self.t("main.analysis_queued", url=url))
        self.log_service.info(f"Analysis queued | url={url} | browser={browser} | fallback={fallback}")
        self.statusBar().showMessage(self.t("main.analysis_queue_notice"))
        self._trace("analyze_url.queued", url=url, browser=browser, fallback=fallback)

    def _start_analysis_request(self, url: str, selected_browser: str, fallback: bool) -> None:
        self.settings.default_browser = selected_browser
        self.settings.fallback_browsers = fallback
        self.settings_service.save(self.settings)
        self._reset_filename_controls(persist=False)
        site_family = UrlUtils.detect_site_family(url)
        self._append_log(f"Analysis settings | browser={selected_browser} | fallback={fallback} | site_family={site_family}")
        self.log_service.info(f"Analysis request received | url={url} | browser={selected_browser} | fallback={fallback}")

        self._reset_analysis_views("pre_analyze_reset")
        self._set_analysis_ui_state(True)
        self.statusBar().showMessage(self.t("main.link_analyzing"))
        self.progress_bar.setValue(15)
        self.progress_details.setText(self.t("main.analyzing_progress"))
        self._append_log(f"Analysis started: {url} | site_family={site_family}")
        self.cookie_status_label.setText(self.t("main.cookie_status_analysis_running", browser=selected_browser))

        self.analysis_thread = QThread(self)
        self.analysis_worker = AnalyzeWorker(
            analyzer=self.analyzer,
            url=url,
            browser=selected_browser,
            fallback_browsers=fallback,
            log_service=self.log_service,
        )
        self.analysis_worker.moveToThread(self.analysis_thread)
        self.analysis_thread.started.connect(self.analysis_worker.run)
        self.analysis_worker.finished.connect(self._on_analyze_finished)
        self.analysis_worker.crashed.connect(self._on_analyze_crashed)
        self.analysis_worker.finished.connect(lambda *_: self._cleanup_analysis_thread())
        self.analysis_worker.crashed.connect(lambda *_: self._cleanup_analysis_thread())
        self.analysis_thread.start()
        self._trace("analyze_url.worker_started", url=url, browser=selected_browser, fallback=fallback)

    def _request_analyze(self):
        url = self.url_input.text().strip()
        self._trace(
            "request_analyze.enter",
            analysis_active=self.analysis_active,
            download_active=self.downloader.is_active,
            current_url=url,
        )
        if self.downloader.is_active:
            self.show_error(self.t("main.analyze_blocked"))
            return
        if not url:
            self.show_error(self.t("main.enter_link_first"))
            return

        selected_browser = self.browser_combo.currentText()
        fallback = self.fallback_checkbox.isChecked()
        if self.analysis_active:
            self._queue_pending_analysis(url, selected_browser, fallback)
            return

        self._start_analysis_request(url, selected_browser, fallback)

    def _history_selected(self, text: str):
        if text and text != self.t("main.history_placeholder"):
            self.url_input.setText(text)
            self._trace("history_selected", value=text)

    def _open_in_selected_browser(self):
        url = self.url_input.text().strip()
        self._trace("open_in_selected_browser.enter", url=url, browser=self.browser_combo.currentText())
        if not url:
            self.show_error(self.t("main.enter_link_first"))
            return

        selected = self.browser_combo.currentText()
        if selected == "cookies_disabled":
            self.show_error(self.t("main.browser_selection_unavailable"))
            return
        binary_path, _ = self.path_manager.resolve_browser_binary(selected)
        if not binary_path:
            self.show_error(self.t("main.browser_not_found", browser=selected))
            return
        try:
            subprocess.Popen([binary_path, url])
            self.log_service.info(f"Opened in browser | browser={selected} | binary={binary_path} | url={url}")
            self.statusBar().showMessage(f"Link {selected} ile acildi")
        except Exception as exc:
            self.log_service.error(f"Browser open error | browser={selected} | error={exc}")
            self.show_error(self.t("main.browser_open_error", error=exc))
        self._trace("open_in_selected_browser.exit", browser=selected)

    def _cleanup_analysis_thread(self):
        self._trace("analysis_thread.cleanup.enter", has_thread=bool(self.analysis_thread), has_worker=bool(self.analysis_worker))
        if self.analysis_thread:
            self.analysis_thread.quit()
            self.analysis_thread.wait(2000)
            self.analysis_thread.deleteLater()
        if self.analysis_worker:
            self.analysis_worker.deleteLater()
        self.analysis_thread = None
        self.analysis_worker = None
        self._set_analysis_ui_state(False)
        pending = self.pending_analysis_request
        self.pending_analysis_request = None
        self._trace("analysis_thread.cleanup.exit", has_pending=bool(pending))
        if pending:
            self._append_log(self.t("main.analysis_queue_starting", url=pending["url"]))
            self._start_analysis_request(pending["url"], pending["browser"], pending["fallback"])

    def _on_analyze_finished(self, payload):
        result = payload["result"]
        url = payload["url"]
        selected_browser = payload["browser"]
        self._trace("analyze_finished.enter", url=url, ok=result.ok, used_browser=result.used_browser)

        if not result.ok:
            self.progress_bar.setValue(0)
            self.current_result = None
            self.current_formats = []
            self.format_table.setRowCount(0)
            self.tech_summary.clear()
            self.tech_summary.setToolTip("")
            self.cookie_status_label.setText(self.t("main.analysis_failed_cookie_status"))
            self._append_log(f"Analysis error: {result.technical_details or result.message}")
            self.show_error(f"{result.message}\n\n{result.technical_details}")
            self.log_service.error(f"Analysis failed | url={url} | detail={result.technical_details or result.message}")
            self.statusBar().showMessage(self.t("main.analysis_failed"))
            self.progress_details.setText(self.t("main.analysis_error_progress"))
            self._update_filename_preview()
            self._trace("analyze_finished.fail", url=url)
            return

        self.current_result = result
        self.current_formats = []
        self.last_completed_path = ""
        self.open_file_button.setEnabled(False)
        self.reencode_button.setEnabled(False)
        self.history["last_browser"] = selected_browser
        recent = [u for u in self.history.get("recent_urls", []) if u != url]
        self.history["recent_urls"] = [url] + recent[:14]
        self.history_service.save(self.history)
        self._refresh_history_combo()

        self.cookie_status_label.setText(self.t("main.cookie_status_used_source", browser=result.used_browser))
        self._render_content_info(result)
        self._render_format_table(result)
        self._update_filename_preview()
        self.progress_bar.setValue(100)
        self.progress_details.setText(self.t("main.analysis_done_progress"))
        self.download_button.setEnabled(bool(self.current_formats))
        self._update_filename_preview()
        self._append_log(result.message)
        self.log_service.info(
            f"Analysis completed | url={url} | site={result.content.site or '-'} | extractor={result.content.extractor or '-'} | formats={len(self.current_formats)} | used_browser={result.used_browser}"
        )
        if selected_browser != result.used_browser:
            fallback_message = self.t("main.fallback_used", selected=selected_browser, used=result.used_browser)
            self.cookie_status_label.setText(self.t("main.cookie_status_switched", selected=selected_browser, used=result.used_browser))
            self._append_log(fallback_message)
            self.log_service.info(f"Browser fallback success | requested={selected_browser} | used={result.used_browser}")
            self.statusBar().showMessage(fallback_message)
        else:
            self.statusBar().showMessage(self.t("main.analysis_completed"))
        self._trace("analyze_finished.success", url=url, format_count=len(self.current_formats))

    def _on_analyze_crashed(self, detail: str):
        url = self.url_input.text().strip()
        self.progress_bar.setValue(0)
        self.progress_details.setText(self.t("main.analysis_crash_progress"))
        self.cookie_status_label.setText(self.t("main.analysis_crash_cookie_status"))
        message = "The analysis worker ended unexpectedly. Check the detailed log."
        self._append_log(message)
        self.log_service.error(f"Analysis crash | url={url} | detail={detail.replace(chr(10), ' | ')}")
        self.show_error(message)
        self.statusBar().showMessage(self.t("main.analysis_crash"))
        self._trace("analyze_crashed", url=url)

    def _render_content_info(self, result):
        content = result.content
        self._trace("render_content_info.enter", title=content.title or "", playlist=content.is_playlist)
        lines = [
            self.t("main.content_title", value=content.title or "-"),
            self.t("main.content_site", value=content.site or "-"),
            self.t("main.content_extractor", value=content.extractor or "-"),
            self.t("main.uploaded_by", name=content.uploader or "-"),
            self.t("main.content_duration", value=content.duration_text or "-"),
            self.t("main.content_type", value=content.content_type or "-"),
            self.t("main.content_playlist", value=self.t("common.yes") if content.is_playlist else self.t("common.no")),
            self.t("main.content_playlist_count", value=content.playlist_count if content.is_playlist else "-"),
            self.t("main.content_url", value=content.webpage_url or content.url),
        ]
        self.info_text.setPlainText("\n".join(lines))
        self._load_thumbnail(content.thumbnail_url)
        self._trace("render_content_info.exit")

    def _load_thumbnail(self, url: str):
        self._trace("load_thumbnail.enter", has_url=bool(url))
        if not url:
            self.thumbnail_label.setText(self.t("main.no_preview"))
            self._trace("load_thumbnail.skip")
            return
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = response.read()
            pixmap = QPixmap()
            if pixmap.loadFromData(data):
                pixmap = pixmap.scaled(320, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.thumbnail_label.setPixmap(pixmap)
                self._trace("load_thumbnail.success")
                return
        except Exception as exc:
            self.log_service.debug(self.t("main.thumbnail_load_failed_log", error=exc))
            self._trace("load_thumbnail.error", error=str(exc))
        self.thumbnail_label.setText(self.t("main.thumbnail_load_failed"))

    def _switch_view_mode(self, mode: str):
        self.current_view_mode = mode
        self.settings.default_view_mode = mode
        self.settings_service.save(self.settings)
        self.simple_view_button.setEnabled(mode != "simple")
        self.advanced_view_button.setEnabled(mode != "advanced")
        self._trace("switch_view_mode", mode=mode, has_result=bool(self.current_result))
        if self.current_result:
            self._render_format_table(self.current_result)

    def _render_format_table(self, result):
        simple_count = len(result.simple_formats or [])
        advanced_count = len(result.advanced_formats or [])
        self._trace("render_format_table.enter", mode=self.current_view_mode, simple_count=simple_count, advanced_count=advanced_count)
        if self.current_view_mode == "advanced":
            self.current_formats = result.advanced_formats or []
        else:
            self.current_formats = result.simple_formats or result.advanced_formats or []

        self.format_table.clearSelection()
        self.format_table.setCurrentCell(-1, -1)
        self.format_table.setRowCount(len(self.current_formats))
        for row, item in enumerate(self.current_formats):
            values = [
                item.format_id,
                item.media_type,
                item.display_label,
                item.resolution,
                item.size_text,
                item.tbr,
                item.vcodec,
                item.acodec,
                item.ext,
                item.fps,
                item.proto,
                item.more_info,
            ]
            for col, value in enumerate(values):
                self.format_table.setItem(row, col, QTableWidgetItem(str(value)))
        if self.current_formats:
            selected_row = self._preferred_selected_row()
            self.format_table.selectRow(selected_row)
            self._update_format_summary()
        else:
            self._update_filename_preview()
        self.download_button.setEnabled(bool(self.current_formats))
        self._trace("render_format_table.exit", rows=len(self.current_formats))

    def _selected_format_item(self):
        row = self.format_table.currentRow()
        if row < 0 or row >= len(self.current_formats):
            return None
        return self.current_formats[row]

    def _preferred_selected_row(self) -> int:
        for index, item in enumerate(self.current_formats):
            more_info = (item.more_info or "").lower()
            label = (item.display_label or "").lower()
            if item.ext == "mhtml" or "storyboard" in more_info or label.startswith("sb") or "storyboard" in label:
                continue
            if item.media_type == "muxed":
                return index
        for index, item in enumerate(self.current_formats):
            more_info = (item.more_info or "").lower()
            label = (item.display_label or "").lower()
            if item.ext == "mhtml" or "storyboard" in more_info or label.startswith("sb") or "storyboard" in label:
                continue
            if item.media_type in {"video only", "audio only"}:
                return index
        return 0

    def _update_format_summary(self):
        item = self._selected_format_item()
        if not item:
            self.tech_summary.setText(self.t("main.total_formats_visible", count=len(self.current_formats)))
            self.tech_summary.setToolTip(self.tech_summary.text())
            self._update_filename_preview()
            return
        summary = (
            f"{self.t('main.selected', text=item.display_label)} | id={item.format_id} | type={item.media_type} | "
            f"res={item.resolution} | size={item.size_text} | ext={item.ext} | "
            f"v={item.vcodec} | a={item.acodec} | fps={item.fps} | proto={item.proto}"
        )
        self.tech_summary.setText(summary)
        self.tech_summary.setToolTip(summary)
        self._update_filename_preview()
        self._trace("update_format_summary", format_id=item.format_id)

    def _refresh_history_combo(self):
        current = self.url_input.text().strip()
        self.url_history_combo.blockSignals(True)
        self.url_history_combo.clear()
        self.url_history_combo.addItem(self.t("main.history_placeholder"))
        for item in self.history.get("recent_urls", []):
            self.url_history_combo.addItem(item)
        index = self.url_history_combo.findText(current)
        if index >= 0:
            self.url_history_combo.setCurrentIndex(index)
        else:
            self.url_history_combo.setCurrentIndex(0)
        self.url_history_combo.blockSignals(False)
        self._trace("refresh_history_combo", current=current, count=len(self.history.get("recent_urls", [])))

    def _start_download(self):
        self._trace("start_download.enter", analysis_active=self.analysis_active, download_active=self.downloader.is_active)
        if self.analysis_active:
            self.show_error(self.t("main.analysis_incomplete_download_blocked"))
            return
        if self.downloader.is_active:
            self.show_error(self.t("main.download_already_active"))
            return
        if not self.current_result or not self.current_result.content:
            self.show_error(self.t("main.complete_analysis_first"))
            return
        selected_item = self._selected_format_item()
        if not selected_item:
            self.show_error(self.t("main.select_format_first"))
            return

        output_dir = self._current_download_dir()
        filename_template = self._effective_filename_template()
        media_mode = self.media_mode_combo.currentText()
        target_container = self.target_container_combo.currentText()

        self.settings.filename_template = filename_template
        self.settings.default_media_mode = media_mode
        self.settings.target_container = target_container
        self.settings.remux_enabled = self.remux_checkbox.isChecked()
        self.settings_service.save(self.settings)

        request_url = self.current_result.content.webpage_url or self.current_result.content.url
        site_family = UrlUtils.detect_site_family(request_url) if request_url else "unknown"

        request = DownloadRequest(
            url=self.current_result.content.webpage_url or self.current_result.content.url,
            browser=self.browser_combo.currentText(),
            fallback_browsers=self.fallback_checkbox.isChecked(),
            output_dir=output_dir,
            filename_template=filename_template,
            media_mode=media_mode,
            selected_item=selected_item,
            remux_enabled=self.remux_checkbox.isChecked(),
            target_container=target_container,
        )

        started = self.downloader.start(
            request=request,
            on_progress=self.ui_signals.progress.emit,
            on_complete=self.ui_signals.completed.emit,
            on_error=self.ui_signals.error.emit,
            on_log=self.ui_signals.log.emit,
        )
        if not started:
            self.show_error("The download engine is busy.")
            return

        self.progress_bar.setValue(0)
        self.progress_details.setText(self.t("main.preparing_progress"))
        self.download_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.open_file_button.setEnabled(False)
        self.reencode_button.setEnabled(False)
        self.log_service.info(
            f"Download request received | url={request.url} | format={selected_item.format_id} | ext={selected_item.ext} | media_type={selected_item.media_type} | mode={media_mode} | target_container={target_container} | remux={request.remux_enabled} | browser={request.browser} | fallback={request.fallback_browsers}"
        )
        self.statusBar().showMessage(self.t("main.download_started"))
        self._append_log(f"Download started | site_family={site_family} | format={selected_item.format_id} | mode={media_mode} | browser={request.browser} | fallback={request.fallback_browsers}")
        self._trace("start_download.exit", started=started)

    def _stop_download(self):
        if not self.downloader.is_active:
            self.statusBar().showMessage(self.t("main.no_active_download_to_stop"))
            return
        self.downloader.stop()
        self.statusBar().showMessage(self.t("main.stop_requested"))
        self._append_log(self.t("main.user_requested_stop"))
        self._trace("stop_download")

    def _on_download_progress(self, status):
        self.progress_bar.setValue(int(status.percent))
        self.progress_details.setText(
            f"%{status.percent:.1f} | Speed: {status.speed_text} | Remaining: {status.eta_text} | "
            f"Size: {status.downloaded_text} / {status.total_text} | Stage: {status.stage}"
        )
        if status.filename:
            self.statusBar().showMessage(self.t("main.active_file", name=Path(status.filename).name))

    def _on_download_completed(self, status):
        self.progress_bar.setValue(100)
        self.progress_details.setText(self.t("main.download_done_progress"))
        self.download_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.last_completed_path = status.final_path or status.filename or ""
        self.open_file_button.setEnabled(bool(self.last_completed_path))
        self.reencode_button.setEnabled(bool(self.last_completed_path))
        self.statusBar().showMessage(self.t("main.download_completed"))
        if self.last_completed_path:
            self._append_log(self.t("main.output_path", path=self.last_completed_path))
        self.log_service.info(f"Download completed | final_path={self.last_completed_path or '-'}")
        self._trace("download_completed", path=self.last_completed_path or "")

    def _on_download_error(self, message: str):
        self.stop_button.setEnabled(False)
        self.download_button.setEnabled(bool(self.current_formats))
        self._update_filename_preview()
        normalized_message = self._normalize_multiline_message(message)
        self._append_log(normalized_message)
        is_cancelled = "cancel" in normalized_message.lower() or "stop" in normalized_message.lower()
        if is_cancelled:
            self.statusBar().showMessage(self.t("main.stop"))
            self.progress_details.setText(self.t("main.download_stopped_progress"))
            self.log_service.info(f"Download stopped | {normalized_message.replace(chr(10), ' | ')}")
            self._trace("download_cancelled", message=normalized_message)
            return
        self.statusBar().showMessage(self.t("main.download_error"))
        self.log_service.error(f"Download error | {normalized_message.replace(chr(10), ' | ')}")
        self._trace("download_error", message=normalized_message)
        self.show_error(normalized_message)


    def _normalize_multiline_message(self, message: str) -> str:
        lines = []
        seen = set()
        for raw in (message or '').splitlines():
            line = raw.strip()
            if not line or line in seen:
                continue
            seen.add(line)
            lines.append(line)
        return "\n".join(lines) if lines else (message or "")

    def _open_download_folder(self):
        folder = self._current_download_dir()
        self._trace("open_download_folder.enter", folder=folder)
        if not Path(folder).exists():
            self.show_error(self.t("main.folder_missing"))
            return
        try:
            if hasattr(subprocess, "CREATE_NO_WINDOW"):
                subprocess.Popen(["explorer", folder], creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen(["explorer", folder])
            self.log_service.info(f"Folder opened: {folder}")
        except Exception as exc:
            self.log_service.error(f"Folder open error | folder={folder} | error={exc}")
            self.show_error(self.t("main.folder_open_error", error=exc))
        self._trace("open_download_folder.exit", folder=folder)

    def _open_last_file(self):
        if not self.last_completed_path:
            self.show_error(self.t("main.no_file_to_open"))
            return
        path = Path(self.last_completed_path)
        self._trace("open_last_file.enter", path=str(path))
        if not path.exists():
            self.show_error(self.t("main.output_not_found"))
            return
        try:
            if os.name == "nt":
                os.startfile(str(path))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
            self.log_service.info(f"File opened: {path}")
        except Exception as exc:
            self.log_service.error(f"File open error | path={path} | error={exc}")
            self.show_error(self.t("main.file_open_error", error=exc))
        self._trace("open_last_file.exit", path=str(path))


    def _build_reencode_output_path(self, input_path: Path, preset_key: str) -> Path:
        preset = self.reencode_presets[preset_key]
        suffix = preset["suffix"]
        ext = preset["ext"]
        candidate = input_path.with_name(f"{input_path.stem}{suffix}{ext}")
        counter = 2
        while candidate.exists():
            candidate = input_path.with_name(f"{input_path.stem}{suffix}_{counter}{ext}")
            counter += 1
        return candidate

    def _build_external_reencode_command(self, ffmpeg_path: str, input_path: Path, output_path: Path, preset_key: str) -> list[str]:
        preset = self.reencode_presets[preset_key]
        command = [
            ffmpeg_path,
            "-hwaccel", "cuda",
            "-i", str(input_path),
            "-c:v", preset["video_codec"],
            *preset["extra"],
            "-c:a", preset["audio_codec"],
            "-b:a", preset["audio_bitrate"],
            str(output_path),
        ]
        return command

    def _launch_external_reencode(self):
        if not self.last_completed_path:
            self.show_error(self.t("main.no_finished_file_for_reencode"))
            return
        source_path = Path(self.last_completed_path)
        self._trace("external_reencode.enter", path=str(source_path))
        if not source_path.exists():
            self.show_error(self.t("main.reencode_source_missing"))
            return
        if os.name != "nt":
            self.show_error(self.t("main.reencode_windows_only"))
            return

        preset_key = self.reencode_preset_combo.currentData() or "mp4_h265_balanced"
        self.settings.default_reencode_preset = preset_key
        self.settings_service.save(self.settings)
        ffmpeg_path, ffmpeg_source = self.path_manager.resolve_binary("ffmpeg", self.settings.ffmpeg_path)
        if not ffmpeg_path:
            self.show_error(self.t("main.ffmpeg_missing"))
            return

        output_path = self._build_reencode_output_path(source_path, preset_key)
        command = self._build_external_reencode_command(ffmpeg_path, source_path, output_path, preset_key)
        quoted_command = subprocess.list2cmdline(command)
        script_body = "\r\n".join([
            "@echo off",
            "chcp 65001>nul",
            "title VDM FFmpeg Re-encode",
            self.t("main.external_reencode_cmd_started"),
            self.t("main.external_reencode_cmd_untracked"),
            "echo.",
            self.t("main.external_reencode_cmd_source", path=source_path),
            self.t("main.external_reencode_cmd_target", path=output_path),
            "echo.",
            quoted_command,
            "echo.",
            self.t("main.external_reencode_cmd_completed"),
            "pause",
            "",
        ])
        temp_dir = Path(tempfile.gettempdir()) / "vdm_reencode_cmd"
        temp_dir.mkdir(parents=True, exist_ok=True)
        script_path = temp_dir / f"vdm_reencode_{source_path.stem[:40]}_{preset_key}.cmd"
        script_path.write_text(script_body, encoding="utf-8")
        try:
            subprocess.Popen(["cmd", "/c", "start", "", str(script_path)], creationflags=subprocess.CREATE_NEW_CONSOLE)
            self._append_log(f"External FFmpeg re-encode started | preset={self.reencode_presets[preset_key]['label']} | source={source_path.name} | target={output_path.name}")
            self.statusBar().showMessage(self.t("main.external_reencode_started"))
            self.log_service.info(
                f"External re-encode started | ffmpeg_source={ffmpeg_source} | preset={preset_key} | source={source_path} | output={output_path} | script={script_path}"
            )
        except Exception as exc:
            self.log_service.error(f"External re-encode start error | error={exc}")
            self.show_error(self.t("main.external_reencode_failed", error=exc))
            return
        self._trace("external_reencode.exit", preset=preset_key, output=str(output_path))

    def show_error(self, message: str):
        self.log_service.error(f"UI error dialog | {message.replace(chr(10), ' | ')}")
        QMessageBox.critical(self, self.t("common.error"), message)
