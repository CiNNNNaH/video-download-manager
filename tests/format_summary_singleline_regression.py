import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import QApplication, QLabel, QLineEdit
from gui.main_window import MainWindow


class DummyAnalyzer:
    pass


def run() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow(DummyAnalyzer())
    assert isinstance(window.selection_summary_label, QLabel)
    assert isinstance(window.tech_summary, QLineEdit)
    assert window.selection_summary_box.maximumHeight() <= 60
    assert window.tech_summary.maximumHeight() <= 32
    print("format summary singleline regression passed")
    window.close()
    app.quit()


if __name__ == "__main__":
    run()
