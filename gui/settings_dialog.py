from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


FILENAME_PRESETS = [
    ("Orijinal Title", "%(title)s.%(ext)s"),
    ("Yukleyici - Title", "%(uploader)s - %(title)s.%(ext)s"),
    ("Title - Resolution", "%(title)s - %(resolution)s.%(ext)s"),
    ("Yukleyici - Title - Resolution", "%(uploader)s - %(title)s - %(resolution)s.%(ext)s"),
    ("Title - Date", "%(title)s - %(upload_date)s.%(ext)s"),
]


class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Ayarlar")
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["system", "light", "dark"])
        self.theme_combo.setCurrentText(settings.theme)
        form.addRow("Tema", self.theme_combo)

        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["chrome", "brave", "firefox", "edge"])
        self.browser_combo.setCurrentText(settings.default_browser)
        form.addRow("Varsayilan Browser", self.browser_combo)

        self.media_mode_combo = QComboBox()
        self.media_mode_combo.addItems(["video+audio", "video only", "audio only"])
        self.media_mode_combo.setCurrentText(settings.default_media_mode)
        form.addRow("Varsayilan Medya Modu", self.media_mode_combo)

        self.container_combo = QComboBox()
        self.container_combo.addItems(["auto", "mp4", "mkv", "keep original"])
        self.container_combo.setCurrentText(settings.target_container)
        form.addRow("Hedef Container", self.container_combo)

        self.filename_preset_combo = QComboBox()
        for label, template in FILENAME_PRESETS:
            self.filename_preset_combo.addItem(label, template)
        self.filename_preset_combo.addItem("Manuel", "__manual__")
        self.manual_filename_edit = QLineEdit()
        self.manual_filename_edit.setPlaceholderText("Ornek: %(title)s.%(ext)s veya kendi sablonunuz")
        self.filename_preview_label = QLabel()
        self.filename_preview_label.setWordWrap(True)

        preset_row = QHBoxLayout()
        preset_row.addWidget(self.filename_preset_combo, 1)
        preset_row.addWidget(self.manual_filename_edit, 2)
        form.addRow("Dosya Adi Bicimi", preset_row)
        form.addRow("Kaydedilecek Sablon", self.filename_preview_label)

        self._apply_filename_controls_from_template(settings.filename_template)
        self.filename_preset_combo.currentIndexChanged.connect(self._on_filename_controls_changed)
        self.manual_filename_edit.textChanged.connect(self._on_filename_controls_changed)

        self.remux_checkbox = QCheckBox("Gerekirse remux uygula")
        self.remux_checkbox.setChecked(settings.remux_enabled)
        form.addRow("", self.remux_checkbox)

        self.startup_check_checkbox = QCheckBox("Acilista bagimlilik kontrolu yap")
        self.startup_check_checkbox.setChecked(settings.startup_dependency_check)
        form.addRow("", self.startup_check_checkbox)

        self.online_updates_checkbox = QCheckBox("Acilista online guncellik kontrolu yap")
        self.online_updates_checkbox.setChecked(settings.check_online_updates_on_startup)
        form.addRow("", self.online_updates_checkbox)

        self.auto_prompt_checkbox = QCheckBox("Eksik bagimliliklarda kurulum oner")
        self.auto_prompt_checkbox.setChecked(settings.auto_prompt_missing_dependencies)
        form.addRow("", self.auto_prompt_checkbox)

        self.prefer_portable_checkbox = QCheckBox("Portable tools klasorunu oncele")
        self.prefer_portable_checkbox.setChecked(settings.prefer_portable_tools)
        form.addRow("", self.prefer_portable_checkbox)

        self.allow_path_checkbox = QCheckBox("Gerekirse kullanici PATH ayarini guncellemeye izin ver")
        self.allow_path_checkbox.setChecked(settings.allow_system_path_updates)
        form.addRow("", self.allow_path_checkbox)

        self.prefer_winget_checkbox = QCheckBox("Kurulumda winget kullanmayi tercih et")
        self.prefer_winget_checkbox.setChecked(settings.installer_prefer_winget)
        form.addRow("", self.prefer_winget_checkbox)

        layout.addLayout(form)

        row = QHBoxLayout()
        ok_button = QPushButton("Tamam")
        cancel_button = QPushButton("Iptal")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        row.addWidget(ok_button)
        row.addWidget(cancel_button)
        layout.addLayout(row)

    def _apply_filename_controls_from_template(self, template: str) -> None:
        for index in range(self.filename_preset_combo.count() - 1):
            if self.filename_preset_combo.itemData(index) == template:
                self.filename_preset_combo.setCurrentIndex(index)
                self.manual_filename_edit.setText(template)
                self.manual_filename_edit.setEnabled(False)
                self.filename_preview_label.setText(template)
                return
        manual_index = self.filename_preset_combo.count() - 1
        self.filename_preset_combo.setCurrentIndex(manual_index)
        self.manual_filename_edit.setText(template)
        self.manual_filename_edit.setEnabled(True)
        self.filename_preview_label.setText(template or "%(title)s.%(ext)s")

    def _effective_filename_template(self) -> str:
        current = self.filename_preset_combo.currentData()
        if current == "__manual__":
            return self.manual_filename_edit.text().strip() or "%(title)s.%(ext)s"
        return current or "%(title)s.%(ext)s"

    def _on_filename_controls_changed(self, *_args) -> None:
        is_manual = self.filename_preset_combo.currentData() == "__manual__"
        self.manual_filename_edit.setEnabled(is_manual)
        self.filename_preview_label.setText(self._effective_filename_template())

    def apply_to_settings(self) -> None:
        self.settings.theme = self.theme_combo.currentText()
        self.settings.default_browser = self.browser_combo.currentText()
        self.settings.default_media_mode = self.media_mode_combo.currentText()
        self.settings.target_container = self.container_combo.currentText()
        self.settings.filename_template = self._effective_filename_template()
        self.settings.remux_enabled = self.remux_checkbox.isChecked()
        self.settings.startup_dependency_check = self.startup_check_checkbox.isChecked()
        self.settings.check_online_updates_on_startup = self.online_updates_checkbox.isChecked()
        self.settings.auto_prompt_missing_dependencies = self.auto_prompt_checkbox.isChecked()
        self.settings.prefer_portable_tools = self.prefer_portable_checkbox.isChecked()
        self.settings.allow_system_path_updates = self.allow_path_checkbox.isChecked()
        self.settings.installer_prefer_winget = self.prefer_winget_checkbox.isChecked()
