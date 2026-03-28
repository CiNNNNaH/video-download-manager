from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)


class SetupDialog(QDialog):
    def __init__(self, statuses, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bagimlilik Kurulum Yardimcisi")
        self.resize(920, 520)
        self.install_requested = False
        self.selected_names = []

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Eksik, erisilemeyen veya guncel olmayan bagimliliklar bulundu. Ozellikle yt-dlp kritik durumdaysa once onu duzeltin."))

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["Sec", "Bilesen", "Durum", "Yerel", "Son", "Kaynak", "Mesaj"]
        )
        self._fill_table(statuses)
        layout.addWidget(self.table)

        self.path_checkbox = QCheckBox("Kurulumdan sonra gerekirse kullanici PATH ayarini guncellemeyi dene")
        self.path_checkbox.setChecked(False)
        layout.addWidget(self.path_checkbox)

        layout.addWidget(QLabel("Ayrinti / Oneri"))
        self.details_box = QTextEdit()
        self.details_box.setReadOnly(True)
        layout.addWidget(self.details_box)

        button_row = QHBoxLayout()
        self.install_button = QPushButton("Secilenleri Kur / Guncelle")
        self.continue_button = QPushButton("Sadece Uyar ve Devam Et")
        self.cancel_button = QPushButton("Iptal")

        self.install_button.clicked.connect(self._request_install)
        self.continue_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_row.addWidget(self.install_button)
        button_row.addWidget(self.continue_button)
        button_row.addWidget(self.cancel_button)
        layout.addLayout(button_row)

        self.table.currentCellChanged.connect(self._update_details)
        self._update_details(0, 0, 0, 0)

    def _fill_table(self, statuses) -> None:
        self.table.setRowCount(0)
        for status in statuses:
            row = self.table.rowCount()
            self.table.insertRow(row)

            checked_item = QTableWidgetItem()
            checked_item.setCheckState(
                Qt.CheckState.Checked if status.can_auto_fix else Qt.CheckState.Unchecked
            )
            self.table.setItem(row, 0, checked_item)
            self.table.setItem(row, 1, QTableWidgetItem(status.name))
            self.table.setItem(row, 2, QTableWidgetItem(status.status))
            self.table.setItem(row, 3, QTableWidgetItem(status.local_version or "-"))
            self.table.setItem(row, 4, QTableWidgetItem(status.latest_version or "-"))
            self.table.setItem(row, 5, QTableWidgetItem(status.source or "-"))
            self.table.setItem(row, 6, QTableWidgetItem(status.message))

            # keep payload
            for col in range(7):
                self.table.item(row, col).setData(32, status)

        self.table.resizeColumnsToContents()

    def _update_details(self, current_row, current_column, previous_row, previous_column) -> None:
        if current_row < 0:
            self.details_box.clear()
            return
        item = self.table.item(current_row, 1)
        if not item:
            self.details_box.clear()
            return
        status = item.data(32)
        if not status:
            self.details_box.clear()
            return

        parts = [
            f"Bilesen: {status.name}",
            f"Durum: {status.status}",
            f"Yerel surum: {status.local_version or '-'}",
            f"Son surum: {status.latest_version or '-'}",
            f"Kaynak: {status.source or '-'}",
            f"Onerilen cozum: {status.suggested_fix or '-'}",
        ]
        if status.details:
            parts.append(f"Detay: {status.details}")
        if status.install_command:
            parts.append(f"Onerilen komut: {status.install_command}")
        self.details_box.setPlainText("\n".join(parts))

    def _request_install(self) -> None:
        selected = []
        for row in range(self.table.rowCount()):
            check_item = self.table.item(row, 0)
            payload_item = self.table.item(row, 1)
            if not check_item or not payload_item:
                continue
            if check_item.checkState() == Qt.CheckState.Checked:
                status = payload_item.data(32)
                if status:
                    selected.append(status.name)

        if not selected:
            QMessageBox.warning(self, "Secim Gerekiyor", "Kurulum icin en az bir bilesen secmelisin.")
            return

        self.selected_names = selected
        self.install_requested = True
        self.accept()
