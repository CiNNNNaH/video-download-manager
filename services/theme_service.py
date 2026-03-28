from PySide6.QtWidgets import QApplication


class ThemeService:
    def apply_theme(self, app: QApplication, theme: str) -> None:
        if theme == "light":
            app.setStyleSheet("")
            return

        if theme == "dark":
            app.setStyleSheet(
                """
                QWidget {
                    background-color: #202124;
                    color: #e8eaed;
                }
                QLineEdit, QTextEdit, QPlainTextEdit, QTableWidget, QComboBox {
                    background-color: #2b2c2f;
                    color: #e8eaed;
                    border: 1px solid #555;
                }
                QPushButton {
                    background-color: #303134;
                    color: #e8eaed;
                    border: 1px solid #555;
                    padding: 6px 10px;
                }
                QGroupBox {
                    border: 1px solid #555;
                    margin-top: 8px;
                    padding-top: 8px;
                }
                """
            )
            return

        app.setStyleSheet("")
